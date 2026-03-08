"""Convert all downloaded PDF attachments to standardized text files.

Uses pdftotext (poppler) for native text extraction. Stores output as
one .txt file per PDF in data/texts/, with the same filename stem.
Also writes a manifest CSV mapping filenames to contract metadata.
"""

from __future__ import annotations

import confpath  # noqa: F401

import argparse
import csv
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

import sqlite_utils
from tqdm import tqdm

from settings import get_env, get_path


def extract_text(pdf_path: str) -> str | None:
    """Extract text from PDF using pdftotext, return text or None on failure."""
    pdftotext_bin = get_env("PDFTOTEXT_BIN", "pdftotext")
    try:
        result = subprocess.run(
            [pdftotext_bin, "-layout", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None


def load_existing_manifest(manifest_path: str) -> dict[str, dict]:
    """Load an existing manifest so reruns preserve prior rows."""
    if not os.path.exists(manifest_path):
        return {}

    with open(manifest_path, newline="") as f:
        return {row["file"]: row for row in csv.DictReader(f)}


def build_manifest_row(db: sqlite_utils.Database, fname: str, text: str) -> dict | None:
    """Build one manifest row from DB metadata."""
    row = db.execute(
        """
        select z.id, z.nazov_zmluvy, z.dodavatel, z.objednavatel,
               z.suma, z.rezort, z.druh, z.typ, z.crz_url
        from prilohy p join zmluvy z on p.zmluva_id = z.id
        where p.subor = ? limit 1
        """,
        [fname],
    ).fetchone()

    if not row:
        return None

    return {
        "file": fname,
        "txt_file": fname.replace(".pdf", ".txt"),
        "zmluva_id": row[0],
        "nazov": row[1],
        "dodavatel": row[2],
        "objednavatel": row[3],
        "suma": row[4],
        "rezort": row[5],
        "druh": row[6],
        "typ": row[7],
        "crz_url": row[8],
        "text_len": len(text),
        "text_extraction_method": "pdftotext",
    }


def process_pdf(fname: str, pdf_dir: str, text_dir: str, force: bool) -> dict:
    """Convert one PDF to text using pdftotext only."""
    pdf_path = os.path.join(pdf_dir, fname)
    txt_path = os.path.join(text_dir, fname.replace(".pdf", ".txt"))

    if not os.path.exists(pdf_path):
        return {"fname": fname, "status": "fail", "error": "pdf not found"}

    if not force and os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
        with open(txt_path) as f:
            text = f.read()
        return {"fname": fname, "status": "skip", "text": text}

    text = extract_text(pdf_path)
    if not text or not text.strip():
        return {"fname": fname, "status": "fail", "error": "no text extracted"}

    with open(txt_path, "w") as f:
        f.write(text)

    return {"fname": fname, "status": "ok", "text": text}


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PDFs to text with pdftotext")
    parser.add_argument("--limit", type=int, default=0, help="Max PDFs to process (0=all)")
    parser.add_argument("--file", type=str, help="Process one specific PDF file")
    parser.add_argument("--force", action="store_true", help="Rebuild text even if output already exists")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default=get_path("CRZ_PDF_DIR", "data/pdfs"),
        help="Directory containing PDFs",
    )
    parser.add_argument(
        "--text-dir",
        type=str,
        default=get_path("CRZ_TEXT_DIR", "data/texts"),
        help="Directory for text outputs",
    )
    args = parser.parse_args()

    pdf_dir = args.pdf_dir
    text_dir = args.text_dir
    os.makedirs(text_dir, exist_ok=True)

    db = sqlite_utils.Database(get_path("CRZ_DB_PATH", "crz.db"))
    manifest_path = os.path.join(text_dir, "manifest.csv")
    manifest_rows = load_existing_manifest(manifest_path)

    if args.file:
        pdf_files = [args.file]
    else:
        pdf_files = sorted(f for f in os.listdir(pdf_dir) if f.endswith(".pdf"))

    if args.limit > 0:
        pdf_files = pdf_files[: args.limit]

    print(f"Found {len(pdf_files)} PDFs to convert")

    ok, fail, skip = 0, 0, 0

    pbar = tqdm(total=len(pdf_files), desc="PDF→text", unit="pdf")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(process_pdf, fname, pdf_dir, text_dir, args.force): fname
            for fname in pdf_files
        }

        for future in as_completed(futures):
            result = future.result()
            fname = result["fname"]
            status = result["status"]
            pbar.update(1)

            if status == "skip":
                skip += 1
            elif status == "ok":
                ok += 1
            else:
                fail += 1
                pbar.write(f"  FAIL {fname}: {result.get('error', 'unknown error')}")
                pbar.set_postfix(ok=ok, fail=fail, skip=skip)
                continue

            manifest_row = build_manifest_row(db=db, fname=fname, text=result["text"])
            if manifest_row:
                manifest_rows[fname] = manifest_row

            pbar.set_postfix(ok=ok, fail=fail, skip=skip)
    pbar.close()

    manifest = [manifest_rows[key] for key in sorted(manifest_rows)]
    if manifest:
        with open(manifest_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=manifest[0].keys())
            writer.writeheader()
            writer.writerows(manifest)

    print(f"\nDone: {ok} converted, {fail} failed, {skip} skipped")
    print(f"Text files in {text_dir}/")
    print(f"Manifest: {manifest_path}")
    print(f"Using pdftotext binary: {get_env('PDFTOTEXT_BIN', 'pdftotext')}")


if __name__ == "__main__":
    main()
