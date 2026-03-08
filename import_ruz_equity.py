"""Fetch equity (vlastné imanie) data from RegisterUZ for CRZ contract suppliers.

Queries the RegisterUZ public API to get the latest financial statement for each
supplier ICO, extracts "Vlastné imanie" from the balance sheet, and stores it
in the `ruz_equity` table in crz.db.

The API has no official rate limits but we add small delays to be respectful.

Usage:
    uv run python import_ruz_equity.py             # fetch all missing
    uv run python import_ruz_equity.py --limit 500  # fetch up to 500
    uv run python import_ruz_equity.py --refresh    # re-fetch all
"""

import argparse
import json
import sqlite3
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

from settings import get_path

DB_PATH = get_path("CRZ_DB_PATH", "crz.db")
API_BASE = "https://www.registeruz.sk/cruz-public/api"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_table(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS ruz_equity (
            ico TEXT PRIMARY KEY,
            ruz_id INTEGER,
            nazov TEXT,
            obdobie TEXT,
            vlastne_imanie REAL,
            zakladne_imanie REAL,
            vysledok_hospodarenia REAL,
            celkove_pasiva REAL,
            uz_id INTEGER,
            vykaz_id INTEGER,
            fetched_at TEXT DEFAULT (datetime('now'))
        )
    """)
    db.commit()


def _fetch_json(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
        })
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
        return None


def _extract_equity_from_vykaz(obsah):
    """Extract equity from standard Slovak balance sheet (podvojné účtovníctvo).

    In template 699 (and similar), the 'Strana pasív' table has data array where:
      [0] = SPOLU PASÍVA (bežné)
      [1] = SPOLU PASÍVA (minulé)
      [2] = A. Vlastné imanie (bežné)
      [3] = A. Vlastné imanie (minulé)
      [4] = A.I. Základné imanie (bežné)
      [5] = A.I. Základné imanie (minulé)
    """
    tabulky = obsah.get("tabulky", [])
    for tab in tabulky:
        nazov = tab.get("nazov", {})
        # Look for the liabilities/equity table
        if isinstance(nazov, dict):
            name_sk = nazov.get("sk", "")
        else:
            name_sk = str(nazov)

        if "pasív" in name_sk.lower() or "liabilities" in name_sk.lower():
            data = tab.get("data", [])
            if len(data) >= 6:
                def _to_float(v):
                    if not v or v == '':
                        return None
                    try:
                        return float(v)
                    except (ValueError, TypeError):
                        return None

                return {
                    "celkove_pasiva": _to_float(data[0]),
                    "vlastne_imanie": _to_float(data[2]),
                    "zakladne_imanie": _to_float(data[4]),
                }

    # Also check for micro-entity templates where structure may differ
    # Try to find "vlastneImanie" key directly in obsah
    if "vlastneImanie" in obsah:
        val = obsah["vlastneImanie"]
        if isinstance(val, dict):
            return {"vlastne_imanie": val.get("bezne") or val.get("netto")}
        return {"vlastne_imanie": val}

    return None


def _extract_vh_from_vykaz(obsah):
    """Extract VH (výsledok hospodárenia) from income statement."""
    tabulky = obsah.get("tabulky", [])
    for tab in tabulky:
        nazov = tab.get("nazov", {})
        if isinstance(nazov, dict):
            name_sk = nazov.get("sk", "")
        else:
            name_sk = str(nazov)

        if "ziskov" in name_sk.lower() or "income" in name_sk.lower():
            data = tab.get("data", [])
            # VH za účtovné obdobie is typically the last row
            # In template 699: position [-2] = bežné, [-1] = minulé
            if len(data) >= 2:
                try:
                    return float(data[-2]) if data[-2] else None
                except (ValueError, TypeError):
                    pass
    return None


def fetch_equity_for_ruz_id(ruz_id):
    """Fetch equity for a single RÚZ entity ID. Returns dict or None."""
    entity = _fetch_json(f"{API_BASE}/uctovna-jednotka?id={ruz_id}")
    if not entity:
        return None

    uz_ids = entity.get("idUctovnychZavierok", [])
    if not uz_ids:
        return None

    # Try from the most recent statement
    for uz_id in reversed(uz_ids[-5:]):
        uz = _fetch_json(f"{API_BASE}/uctovna-zavierka?id={uz_id}")
        if not uz:
            continue

        obdobie = f"{uz.get('obdobieOd', '')}-{uz.get('obdobieDo', '')}"
        vykaz_ids = uz.get("idUctovnychVykazov", [])

        for vid in vykaz_ids:
            v = _fetch_json(f"{API_BASE}/uctovny-vykaz?id={vid}")
            if not v:
                continue

            obsah = v.get("obsah", {})
            if not obsah or not obsah.get("tabulky"):
                continue

            equity = _extract_equity_from_vykaz(obsah)
            if equity and equity.get("vlastne_imanie") is not None:
                vh = _extract_vh_from_vykaz(obsah)
                return {
                    "ico": entity["ico"],
                    "ruz_id": ruz_id,
                    "nazov": entity.get("nazovUJ"),
                    "obdobie": obdobie,
                    "vlastne_imanie": equity.get("vlastne_imanie"),
                    "zakladne_imanie": equity.get("zakladne_imanie"),
                    "vysledok_hospodarenia": vh,
                    "celkove_pasiva": equity.get("celkove_pasiva"),
                    "uz_id": uz_id,
                    "vykaz_id": vid,
                }

    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch equity data from RegisterUZ")
    parser.add_argument("--limit", type=int, default=0, help="Max entities to fetch (0=all)")
    parser.add_argument("--refresh", action="store_true", help="Re-fetch all entities")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers")
    args = parser.parse_args()

    db = get_db()
    init_table(db)

    if args.refresh:
        db.execute("DELETE FROM ruz_equity")
        db.commit()

    # Get supplier ICOs that need fetching, with their ruz_entity IDs
    already = set(r[0] for r in db.execute("SELECT ico FROM ruz_equity").fetchall())

    rows = db.execute("""
        SELECT DISTINCT r.id as ruz_id, r.cin as ico
        FROM ruz_entities r
        WHERE r.cin IN (
            SELECT DISTINCT replace(z.dodavatel_ico, ' ', '')
            FROM zmluvy z
            WHERE length(replace(z.dodavatel_ico, ' ', '')) = 8
        )
        AND r.terminated_on IS NULL
        AND r.cin IS NOT NULL
        ORDER BY r.id
    """).fetchall()

    to_fetch = [(r["ruz_id"], r["ico"]) for r in rows if r["ico"] not in already]
    total = len(to_fetch)

    if args.limit > 0:
        to_fetch = to_fetch[:args.limit]

    print(f"Fetching equity for {len(to_fetch)}/{total} supplier entities ({len(already)} already cached)...")

    fetched = 0
    errors = 0
    negative = 0

    def _worker(item):
        ruz_id, ico = item
        time.sleep(0.05)  # Small delay
        return fetch_equity_for_ruz_id(ruz_id)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(_worker, item): item for item in to_fetch}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result:
                db.execute("""
                    INSERT OR REPLACE INTO ruz_equity
                    (ico, ruz_id, nazov, obdobie, vlastne_imanie, zakladne_imanie,
                     vysledok_hospodarenia, celkove_pasiva, uz_id, vykaz_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result["ico"], result["ruz_id"], result["nazov"],
                    result["obdobie"], result["vlastne_imanie"],
                    result["zakladne_imanie"], result["vysledok_hospodarenia"],
                    result["celkove_pasiva"], result["uz_id"], result["vykaz_id"],
                ))
                fetched += 1
                if result["vlastne_imanie"] is not None and result["vlastne_imanie"] < 0:
                    negative += 1
            else:
                errors += 1

            if (i + 1) % 50 == 0:
                db.commit()
                print(f"  [{i+1}/{len(to_fetch)}] fetched={fetched}, errors={errors}, negative_equity={negative}")

    db.commit()

    total_cached = db.execute("SELECT count(*) FROM ruz_equity").fetchone()[0]
    total_negative = db.execute("SELECT count(*) FROM ruz_equity WHERE vlastne_imanie < 0").fetchone()[0]

    print(f"\nDone: +{fetched} new ({errors} failed), {total_cached} total cached, {total_negative} with negative equity")

    if total_negative > 0:
        print("\nTop negative equity suppliers:")
        neg_rows = db.execute("""
            SELECT e.ico, e.nazov, e.vlastne_imanie, e.obdobie,
                   count(z.id) as contract_count, sum(z.suma) as total_sum
            FROM ruz_equity e
            JOIN zmluvy z ON replace(z.dodavatel_ico, ' ', '') = e.ico
            WHERE e.vlastne_imanie < 0
            GROUP BY e.ico
            ORDER BY e.vlastne_imanie ASC
            LIMIT 10
        """).fetchall()
        for r in neg_rows:
            total_sum = r['total_sum'] or 0
            print(f"  {r['nazov']} (ICO: {r['ico']}): vlastné imanie = {r['vlastne_imanie']:,.0f} EUR, "
                  f"{r['contract_count']} zmluv za {total_sum:,.0f} EUR ({r['obdobie']})")

    db.close()


if __name__ == "__main__":
    main()
