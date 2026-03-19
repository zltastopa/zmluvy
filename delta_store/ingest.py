"""Delta Lake ingestion pipeline for CRZ daily exports.

End-to-end pipeline: download daily XML → parse contracts → download PDFs →
convert PDFs to text → extract with LLM → upsert into Delta tables.

Usage:
    # Full daily pipeline for today
    uv run python delta_store/ingest.py --date 2026-03-18

    # Date range
    uv run python delta_store/ingest.py --from 2026-03-01 --to 2026-03-18

    # Individual steps
    uv run python delta_store/ingest.py --date 2026-03-18 --step download
    uv run python delta_store/ingest.py --date 2026-03-18 --step parse
    uv run python delta_store/ingest.py --date 2026-03-18 --step pdf
    uv run python delta_store/ingest.py --date 2026-03-18 --step text
    uv run python delta_store/ingest.py --date 2026-03-18 --step extract
    uv run python delta_store/ingest.py --date 2026-03-18 --step flag
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

import httpx
import pyarrow as pa
from deltalake import DeltaTable, write_deltalake
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "pipeline"))

from settings import get_env, get_path, normalize_company_name
from openrouter_utils import OPENROUTER_BASE, load_openrouter_api_key
from load_crz import parse_xml, REZORT_MAP
from extract_contracts import (
    extract_one,
    extract_one_pdf,
    sanitize_extraction,
    get_manifest,
    smart_truncate,
)
from pipeline.pdf_to_text import extract_text as pdftotext_extract

TABLES_DIR = Path(__file__).parent / "tables"
DATA_DIR = REPO_ROOT / "data"

CRZ_EXPORT_URL = "https://www.crz.gov.sk/export/{date}.zip"

# Reuse schemas from migrate script
from delta_store.migrate_from_sqlite import SCHEMAS

ALL_STEPS = ["download", "parse", "pdf", "text", "extract", "flag"]


# ---------------------------------------------------------------------------
# Delta helpers
# ---------------------------------------------------------------------------

def delta_upsert(table_name: str, rows: list[dict], pk: str):
    """Upsert rows into a Delta table using merge."""
    if not rows:
        return 0

    schema = SCHEMAS[table_name]
    table_path = str(TABLES_DIR / table_name)

    # Build PyArrow table from rows
    columns = {f.name: [] for f in schema}
    for row in rows:
        for field in schema:
            val = row.get(field.name)
            if field.type == pa.utf8() and val is not None and not isinstance(val, str):
                val = str(val)
            columns[field.name].append(val)

    arrays = [pa.array(columns[f.name], type=f.type) for f in schema]
    source = pa.table({f.name: arr for f, arr in zip(schema, arrays)}, schema=schema)

    if not (Path(table_path) / "_delta_log").exists():
        write_deltalake(table_path, source, mode="overwrite")
        return len(rows)

    dt = DeltaTable(table_path)
    (
        dt.merge(
            source=source,
            predicate=f"s.{pk} = t.{pk}",
            source_alias="s",
            target_alias="t",
        )
        .when_matched_update_all()
        .when_not_matched_insert_all()
        .execute()
    )
    return len(rows)


# ---------------------------------------------------------------------------
# Step 1: Download daily XML export
# ---------------------------------------------------------------------------

def step_download(dates: list[date], data_dir: Path) -> list[Path]:
    """Download CRZ daily ZIP exports, return list of XML paths."""
    xml_dir = data_dir / "xml"
    xml_dir.mkdir(parents=True, exist_ok=True)

    xml_paths = []
    for d in dates:
        xml_path = xml_dir / f"{d}.xml"
        if xml_path.exists() and xml_path.stat().st_size > 0:
            print(f"  {d}: already downloaded")
            xml_paths.append(xml_path)
            continue

        zip_url = CRZ_EXPORT_URL.format(date=d)
        print(f"  {d}: downloading {zip_url}")
        try:
            resp = httpx.get(zip_url, timeout=60, follow_redirects=True)
            resp.raise_for_status()

            if len(resp.content) == 0:
                print(f"  {d}: empty ZIP (no data for this day)")
                continue

            with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                xml_names = [n for n in zf.namelist() if n.endswith(".xml")]
                if not xml_names:
                    print(f"  {d}: ZIP contains no XML files")
                    continue

                # Extract first XML (daily exports contain one file)
                xml_data = zf.read(xml_names[0])
                xml_path.write_bytes(xml_data)
                print(f"  {d}: {len(xml_data):,} bytes")
                xml_paths.append(xml_path)

        except httpx.HTTPStatusError as e:
            print(f"  {d}: HTTP {e.response.status_code}")
        except Exception as e:
            print(f"  {d}: {e}")

    return xml_paths


# ---------------------------------------------------------------------------
# Step 2: Parse XML → upsert into Delta (zmluvy, prilohy, rezorty)
# ---------------------------------------------------------------------------

def step_parse(xml_paths: list[Path]) -> tuple[int, int]:
    """Parse XML exports and upsert contracts + attachments into Delta."""
    all_contracts = []
    all_attachments = []

    for xml_path in xml_paths:
        print(f"  Parsing {xml_path.name}...")
        contracts, attachments = parse_xml(str(xml_path))
        all_contracts.extend(contracts)
        all_attachments.extend(attachments)

    # Deduplicate by id (keep latest)
    seen = {}
    for c in all_contracts:
        if c["id"] is not None:
            seen[c["id"]] = c
    contracts = list(seen.values())

    att_seen = {}
    for a in all_attachments:
        if a["id"] is not None:
            att_seen[a["id"]] = a
    attachments = list(att_seen.values())

    print(f"  {len(contracts)} contracts, {len(attachments)} attachments (after dedup)")

    n_contracts = delta_upsert("zmluvy", contracts, "id")
    n_attachments = delta_upsert("prilohy", attachments, "id")

    # Rezorty lookup
    rezort_rows = [{"id": k, "nazov": v} for k, v in REZORT_MAP.items() if k != "0" and v]
    delta_upsert("rezorty", rezort_rows, "id")

    return n_contracts, n_attachments


# ---------------------------------------------------------------------------
# Step 3: Download PDFs
# ---------------------------------------------------------------------------

def step_pdf(dates: list[date], workers: int = 16, limit: int = 0) -> int:
    """Download PDF attachments for contracts in the given date range."""
    import duckdb

    pdf_dir = Path(get_path("CRZ_PDF_DIR", "data/pdfs"))
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # Query Delta table for attachments
    conn = duckdb.connect()
    conn.execute("INSTALL delta; LOAD delta;")

    zmluvy_path = str(TABLES_DIR / "zmluvy")
    prilohy_path = str(TABLES_DIR / "prilohy")

    if not (Path(zmluvy_path) / "_delta_log").exists():
        print("  No zmluvy Delta table found. Run --step parse first.")
        return 0

    date_from = min(dates).isoformat()
    date_to = max(dates).isoformat() + " 23:59:59"

    rows = conn.execute(f"""
        SELECT p.url, p.subor, z.id as zmluva_id
        FROM delta_scan('{prilohy_path}') p
        JOIN delta_scan('{zmluvy_path}') z ON p.zmluva_id = z.id
        WHERE p.subor LIKE '%.pdf'
          AND z.datum_zverejnenia >= $1
          AND z.datum_zverejnenia <= $2
    """, [date_from, date_to]).fetchall()

    existing = set(
        f for f in os.listdir(pdf_dir)
        if f.endswith(".pdf") and os.path.getsize(pdf_dir / f) > 0
    )

    to_download = [(url, subor, zid) for url, subor, zid in rows if subor not in existing]
    if limit > 0:
        to_download = to_download[:limit]

    already = len(rows) - len(to_download)
    print(f"  {len(rows)} PDFs total, {already} already downloaded, {len(to_download)} to download")

    if not to_download:
        return 0

    ok, fail, total_bytes = 0, 0, 0

    def download_one(item):
        url, subor, _ = item
        dest = pdf_dir / subor
        try:
            resp = client.get(url)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            return (subor, len(resp.content), None)
        except Exception as e:
            return (subor, 0, str(e))

    pbar = tqdm(total=len(to_download), desc="Downloading PDFs", unit="pdf")
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(download_one, item): item for item in to_download}
            for future in as_completed(futures):
                subor, size, error = future.result()
                pbar.update(1)
                if error:
                    pbar.write(f"  FAIL {subor}: {error}")
                    fail += 1
                else:
                    ok += 1
                    total_bytes += size
                pbar.set_postfix(ok=ok, fail=fail, MB=f"{total_bytes/1024/1024:.0f}")
    pbar.close()

    print(f"  {ok} downloaded, {fail} failed, {total_bytes/1024/1024:.0f} MB")
    return ok


# ---------------------------------------------------------------------------
# Step 4: PDF → text
# ---------------------------------------------------------------------------

def _convert_one_pdf(args: tuple) -> tuple:
    """Convert a single PDF to text. Module-level for ProcessPoolExecutor pickling."""
    fname, pdf_dir, text_dir, force = args
    pdf_path = str(Path(pdf_dir) / fname)
    txt_path = Path(text_dir) / fname.replace(".pdf", ".txt")

    if not force and txt_path.exists() and txt_path.stat().st_size > 0:
        return ("skip", fname, None)

    # Try native text extraction first
    try:
        from pipeline.pdf_to_text import extract_text as _pdftotext
        text = _pdftotext(pdf_path)
    except Exception as e:
        return ("fail", fname, str(e))

    if text and text.strip():
        txt_path.write_text(text)
        return ("ok", fname, None)

    # Scanned PDF — fall back to OCR
    try:
        import logging
        import ocrmypdf
        logging.getLogger("ocrmypdf").setLevel(logging.ERROR)
        logging.getLogger("PIL").setLevel(logging.ERROR)

        ocr_pdf = Path(pdf_dir) / f".ocr_{os.getpid()}_{fname}"
        ocrmypdf.ocr(
            pdf_path,
            str(ocr_pdf),
            language="slk+ces",
            skip_text=True,
            progress_bar=False,
            pages="1-20",
            tesseract_timeout=60,
        )
        text = _pdftotext(str(ocr_pdf))
        ocr_pdf.unlink(missing_ok=True)

        if text and text.strip():
            txt_path.write_text(text)
            return ("ocr_ok", fname, None)
        return ("ocr_fail", fname, "OCR produced no text")

    except Exception as e:
        Path(pdf_dir).joinpath(f".ocr_{os.getpid()}_{fname}").unlink(missing_ok=True)
        return ("ocr_fail", fname, str(e))


def step_text(dates: list[date], workers: int = 0, force: bool = False) -> int:
    """Convert downloaded PDFs to text. Uses ProcessPoolExecutor for OCR parallelism."""
    import duckdb

    if workers <= 0:
        workers = min(os.cpu_count() or 4, 8)

    pdf_dir = Path(get_path("CRZ_PDF_DIR", "data/pdfs"))
    text_dir = Path(get_path("CRZ_TEXT_DIR", "data/texts"))
    text_dir.mkdir(parents=True, exist_ok=True)

    # Get PDF filenames for the date range from Delta
    conn = duckdb.connect()
    conn.execute("INSTALL delta; LOAD delta;")

    zmluvy_path = str(TABLES_DIR / "zmluvy")
    prilohy_path = str(TABLES_DIR / "prilohy")

    if not (Path(zmluvy_path) / "_delta_log").exists():
        print("  No zmluvy Delta table found.")
        return 0

    date_from = min(dates).isoformat()
    date_to = max(dates).isoformat() + " 23:59:59"

    rows = conn.execute(f"""
        SELECT DISTINCT p.subor
        FROM delta_scan('{prilohy_path}') p
        JOIN delta_scan('{zmluvy_path}') z ON p.zmluva_id = z.id
        WHERE p.subor LIKE '%.pdf'
          AND z.datum_zverejnenia >= $1
          AND z.datum_zverejnenia <= $2
    """, [date_from, date_to]).fetchall()

    pdf_files = [r[0] for r in rows if (pdf_dir / r[0]).exists()]
    print(f"  {len(pdf_files)} PDFs to convert ({workers} workers)")

    ok, fail, skip, ocr_ok, ocr_fail = 0, 0, 0, 0, 0

    task_args = [(f, str(pdf_dir), str(text_dir), force) for f in pdf_files]

    pbar = tqdm(total=len(pdf_files), desc="PDF→text", unit="pdf")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_convert_one_pdf, a): a[0] for a in task_args}
        for future in as_completed(futures):
            status, fname, error = future.result()
            pbar.update(1)
            if status == "ok":
                ok += 1
            elif status == "skip":
                skip += 1
            elif status == "ocr_ok":
                ocr_ok += 1
            elif status == "ocr_fail":
                ocr_fail += 1
                pbar.write(f"  OCR_FAIL {fname}: {error}")
            else:
                fail += 1
                pbar.write(f"  FAIL {fname}: {error}")
            pbar.set_postfix(ok=ok, ocr=ocr_ok, ocr_fail=ocr_fail, fail=fail, skip=skip)
    pbar.close()

    print(f"  {ok} native, {ocr_ok} OCR, {ocr_fail} OCR failed, {fail} failed, {skip} skipped")
    return ok


# ---------------------------------------------------------------------------
# Step 5: LLM extraction → upsert into Delta extractions table
# ---------------------------------------------------------------------------

def step_extract(
    dates: list[date],
    workers: int = 8,
    model: str | None = None,
    force: bool = False,
    limit: int = 0,
) -> int:
    """Extract structured data from contract texts/PDFs and upsert into Delta."""
    import duckdb

    model = model or get_env("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
    api_key = load_openrouter_api_key()

    pdf_dir = Path(get_path("CRZ_PDF_DIR", "data/pdfs"))
    text_dir = Path(get_path("CRZ_TEXT_DIR", "data/texts"))
    output_dir = Path(get_path("CRZ_EXTRACTIONS_DIR", "data/extractions"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get contract list from Delta
    conn = duckdb.connect()
    conn.execute("INSTALL delta; LOAD delta;")

    zmluvy_path = str(TABLES_DIR / "zmluvy")
    prilohy_path = str(TABLES_DIR / "prilohy")
    extractions_path = str(TABLES_DIR / "extractions")

    date_from = min(dates).isoformat()
    date_to = max(dates).isoformat() + " 23:59:59"

    # Get contracts with their PDF filenames
    rows = conn.execute(f"""
        SELECT z.id, z.dodavatel, z.objednavatel, p.subor
        FROM delta_scan('{zmluvy_path}') z
        JOIN delta_scan('{prilohy_path}') p ON p.zmluva_id = z.id
        WHERE p.subor LIKE '%.pdf'
          AND z.datum_zverejnenia >= $1
          AND z.datum_zverejnenia <= $2
    """, [date_from, date_to]).fetchall()

    # Group by contract ID (one extraction per contract, pick first PDF)
    contracts = {}
    for zid, dodavatel, objednavatel, subor in rows:
        if zid not in contracts:
            contracts[zid] = {
                "id": zid,
                "dodavatel": dodavatel,
                "objednavatel": objednavatel,
                "subor": subor,
            }

    # Filter already-extracted (unless force)
    if not force and (Path(extractions_path) / "_delta_log").exists():
        existing_ids = set(
            r[0] for r in conn.execute(f"""
                SELECT zmluva_id FROM delta_scan('{extractions_path}')
            """).fetchall()
        )
        to_process = {k: v for k, v in contracts.items() if k not in existing_ids}
    else:
        to_process = contracts

    if limit > 0:
        to_process = dict(list(to_process.items())[:limit])

    print(f"  {len(contracts)} contracts total, {len(to_process)} to extract")

    if not to_process:
        return 0

    extraction_rows = []
    ok, fail = 0, 0

    def process_one(contract, client):
        zid = contract["id"]
        subor = contract["subor"]
        txt_name = subor.replace(".pdf", ".txt")
        txt_path = text_dir / txt_name
        pdf_path = pdf_dir / subor

        text = None
        source_kind = None

        if txt_path.exists():
            text = txt_path.read_text()
            if len(text.strip()) >= 50:
                source_kind = "text"

        if source_kind is None and pdf_path.exists():
            source_kind = "pdf"

        if source_kind is None:
            return (zid, None, "no text or pdf")

        try:
            if source_kind == "text":
                extraction, usage = extract_one(client, api_key, text, model=model)
            else:
                extraction, usage = extract_one_pdf(client, api_key, str(pdf_path), model=model)

            meta = {"dodavatel": contract["dodavatel"], "objednavatel": contract["objednavatel"]}
            extraction = sanitize_extraction(extraction, meta, text)
            extraction["_zmluva_id"] = zid
            extraction["_model"] = model
            extraction["_source_kind"] = source_kind

            # Save JSON sidecar
            json_path = output_dir / f"{subor.replace('.pdf', '.json')}"
            json_path.write_text(json.dumps(extraction, ensure_ascii=False, indent=2))

            return (zid, extraction, None)

        except json.JSONDecodeError as e:
            return (zid, None, f"bad JSON: {e}")
        except httpx.HTTPStatusError as e:
            return (zid, None, f"HTTP {e.response.status_code}")
        except Exception as e:
            return (zid, None, str(e))

    pbar = tqdm(total=len(to_process), desc="Extracting", unit="contract")

    with httpx.Client(timeout=120) as client:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(process_one, contract, client): contract
                for contract in to_process.values()
            }
            for future in as_completed(futures):
                zid, extraction, error = future.result()
                pbar.update(1)

                if error:
                    pbar.write(f"  FAIL {zid}: {error}")
                    fail += 1
                    continue

                ok += 1
                # Build extraction row for Delta
                subcontractors = [
                    e for e in extraction.get("hidden_entities", [])
                    if e.get("role") == "subcontractor"
                ]
                sub_pcts = [e["percentage"] for e in subcontractors if e.get("percentage") is not None]

                extraction_rows.append({
                    "zmluva_id": zid,
                    "service_category": extraction.get("service_category"),
                    "actual_subject": extraction.get("actual_subject"),
                    "penalty_asymmetry": extraction.get("penalty_asymmetry"),
                    "auto_renewal": int(extraction.get("auto_renewal", False)),
                    "bezodplatne": int(extraction.get("bezodplatne", False)),
                    "funding_type": extraction.get("funding_source", {}).get("type"),
                    "grant_amount": str(extraction.get("funding_source", {}).get("grant_amount")) if extraction.get("funding_source", {}).get("grant_amount") is not None else None,
                    "hidden_entity_count": len(extraction.get("hidden_entities", [])),
                    "penalty_count": len(extraction.get("penalties", [])),
                    "iban_count": len(extraction.get("bank_accounts", [])),
                    "extraction_json": json.dumps(extraction, ensure_ascii=False),
                    "model": extraction.get("_model"),
                    "subcontracting_mentioned": int(extraction.get("subcontracting_mentioned", False)),
                    "subcontractor_count": len(subcontractors),
                    "subcontractor_max_percentage": str(max(sub_pcts)) if sub_pcts else None,
                })

                pbar.set_postfix(ok=ok, fail=fail)

    pbar.close()

    # Batch upsert all extractions
    if extraction_rows:
        delta_upsert("extractions", extraction_rows, "zmluva_id")

    print(f"  {ok} extracted, {fail} failed")
    return ok


# ---------------------------------------------------------------------------
# Step 6: Flag contracts (red_flags)
# ---------------------------------------------------------------------------

def step_flag(dates: list[date]) -> int:
    """Run flag rules against new contracts and upsert red_flags into Delta."""
    import duckdb

    conn = duckdb.connect()
    conn.execute("INSTALL delta; LOAD delta;")

    # Load all needed tables
    for name in ["zmluvy", "extractions", "prilohy", "flag_rules", "red_flags"]:
        tpath = TABLES_DIR / name
        if (tpath / "_delta_log").exists():
            conn.execute(f"CREATE TABLE {name} AS SELECT * FROM delta_scan('{tpath}')")
        else:
            conn.execute(f"CREATE TABLE {name} (id INTEGER)")  # empty stub

    date_from = min(dates).isoformat()
    date_to = max(dates).isoformat() + " 23:59:59"

    # Get enabled rules
    rules = conn.execute("""
        SELECT id, sql_condition, needs_extraction FROM flag_rules WHERE enabled = 1
    """).fetchall()

    if not rules:
        print("  No enabled flag rules found")
        return 0

    new_flags = []
    now = datetime.now().isoformat()

    for rule_id, sql_condition, needs_extraction in rules:
        try:
            query = f"""
                SELECT z.id as zmluva_id
                FROM zmluvy z
                LEFT JOIN extractions e ON z.id = e.zmluva_id
                LEFT JOIN (
                    SELECT zmluva_id, count(*) as prilohy_count
                    FROM prilohy GROUP BY zmluva_id
                ) p ON z.id = p.zmluva_id
                WHERE z.datum_zverejnenia >= $1
                  AND z.datum_zverejnenia <= $2
                  AND ({sql_condition})
            """
            flagged = conn.execute(query, [date_from, date_to]).fetchall()

            for (zmluva_id,) in flagged:
                new_flags.append({
                    "id": None,  # will be auto-assigned
                    "zmluva_id": zmluva_id,
                    "flag_type": rule_id,
                    "detail": None,
                    "created_at": now,
                })

        except Exception as e:
            print(f"  Rule {rule_id} failed: {e}")

    if not new_flags:
        print("  No new flags")
        return 0

    # Assign IDs — get max existing ID
    red_flags_path = TABLES_DIR / "red_flags"
    if (red_flags_path / "_delta_log").exists():
        max_id = conn.execute(f"SELECT COALESCE(MAX(id), 0) FROM delta_scan('{red_flags_path}')").fetchone()[0]
    else:
        max_id = 0

    # Deduplicate: don't re-flag (zmluva_id, flag_type) pairs that already exist
    existing_pairs = set()
    if (red_flags_path / "_delta_log").exists():
        existing = conn.execute(f"""
            SELECT zmluva_id, flag_type FROM delta_scan('{red_flags_path}')
        """).fetchall()
        existing_pairs = set(existing)

    deduped = []
    for flag in new_flags:
        pair = (flag["zmluva_id"], flag["flag_type"])
        if pair not in existing_pairs:
            max_id += 1
            flag["id"] = max_id
            deduped.append(flag)
            existing_pairs.add(pair)

    if deduped:
        delta_upsert("red_flags", deduped, "id")

    print(f"  {len(deduped)} new flags from {len(rules)} rules")
    return len(deduped)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_dates(args) -> list[date]:
    """Parse date arguments into a list of dates."""
    if args.date:
        return [date.fromisoformat(args.date)]

    if args.date_from:
        d_from = date.fromisoformat(
            args.date_from + "-01" if len(args.date_from) == 7 else args.date_from
        )
        if args.date_to:
            d_to = date.fromisoformat(
                args.date_to + "-01" if len(args.date_to) == 7 else args.date_to
            )
            if len(args.date_to) == 7:
                # Month: go to last day
                if d_to.month == 12:
                    d_to = date(d_to.year + 1, 1, 1) - timedelta(days=1)
                else:
                    d_to = date(d_to.year, d_to.month + 1, 1) - timedelta(days=1)
        else:
            d_to = d_from

        dates = []
        d = d_from
        while d <= d_to:
            dates.append(d)
            d += timedelta(days=1)
        return dates

    return [date.today()]


def main():
    parser = argparse.ArgumentParser(description="CRZ Delta Lake ingestion pipeline")
    parser.add_argument("--date", type=str, help="Single date (YYYY-MM-DD)")
    parser.add_argument("--from", type=str, dest="date_from", help="Start date (YYYY-MM-DD or YYYY-MM)")
    parser.add_argument("--to", type=str, dest="date_to", help="End date (YYYY-MM-DD or YYYY-MM)")
    parser.add_argument(
        "--step",
        type=str,
        choices=ALL_STEPS,
        help="Run only one step (default: all steps)",
    )
    parser.add_argument("--workers", type=int, default=8, help="Parallel workers (default: 8)")
    parser.add_argument("--limit", type=int, default=0, help="Limit items per step (0=all)")
    parser.add_argument("--model", type=str, help="LLM model for extraction")
    parser.add_argument("--force", action="store_true", help="Re-process even if output exists")
    args = parser.parse_args()

    dates = parse_dates(args)
    steps = [args.step] if args.step else ALL_STEPS
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Dates: {dates[0]} → {dates[-1]} ({len(dates)} days)")
    print(f"Steps: {', '.join(steps)}")
    print(f"Tables: {TABLES_DIR}")
    print()

    if "download" in steps:
        print("Step 1/6: Download daily XML exports")
        xml_paths = step_download(dates, DATA_DIR)
        print(f"  → {len(xml_paths)} XML files\n")
    else:
        # Discover existing XMLs for subsequent steps
        xml_dir = DATA_DIR / "xml"
        xml_paths = [xml_dir / f"{d}.xml" for d in dates if (xml_dir / f"{d}.xml").exists()]

    if "parse" in steps:
        print("Step 2/6: Parse XML → Delta tables")
        if not xml_paths:
            print("  No XML files to parse\n")
        else:
            n_c, n_a = step_parse(xml_paths)
            print(f"  → {n_c} contracts, {n_a} attachments upserted\n")

    if "pdf" in steps:
        print("Step 3/6: Download PDFs")
        n = step_pdf(dates, workers=args.workers, limit=args.limit)
        print(f"  → {n} PDFs downloaded\n")

    if "text" in steps:
        print("Step 4/6: Convert PDFs to text")
        n = step_text(dates, workers=args.workers, force=args.force)
        print(f"  → {n} texts converted\n")

    if "extract" in steps:
        print("Step 5/6: LLM extraction")
        n = step_extract(
            dates,
            workers=args.workers,
            model=args.model,
            force=args.force,
            limit=args.limit,
        )
        print(f"  → {n} contracts extracted\n")

    if "flag" in steps:
        print("Step 6/6: Flag contracts")
        n = step_flag(dates)
        print(f"  → {n} new flags\n")

    print("Done!")


if __name__ == "__main__":
    main()
