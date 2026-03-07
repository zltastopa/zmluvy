"""Enrich CRZ contract suppliers with financial data from FinStat.sk.

Scrapes key financial indicators for suppliers by IČO and stores them
in the `supplier_financials` table. Then evaluates red flag rules
and writes results to `supplier_red_flags`.

Usage:
    python enrich_suppliers.py                          # enrich top suppliers by contract value
    python enrich_suppliers.py --limit 50               # limit to N suppliers
    python enrich_suppliers.py --ico 51671824           # enrich single company
    python enrich_suppliers.py --from 2026-01 --to 2026-03  # period filter
    python enrich_suppliers.py --flags-only             # skip scraping, just re-evaluate flags
    python enrich_suppliers.py --force                  # re-scrape even if data exists
"""
import argparse
import html
import json
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime

import httpx
from tqdm import tqdm

from settings import get_path

DB_PATH = get_path("CRZ_DB_PATH", "crz.db")

FINSTAT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "sk-SK,sk;q=0.9",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_tables(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS supplier_financials (
            ico TEXT PRIMARY KEY,
            nazov TEXT,
            datum_vzniku TEXT,
            trzby INTEGER,
            zisk INTEGER,
            aktiva INTEGER,
            vlastny_kapital INTEGER,
            celkova_zadlzenost_pct REAL,
            rpvs_status TEXT,
            tax_reliability TEXT,
            scraped_at TEXT DEFAULT (datetime('now')),
            raw_json TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS supplier_red_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ico TEXT NOT NULL,
            zmluva_id INTEGER,
            flag_type TEXT NOT NULL,
            detail TEXT,
            severity TEXT NOT NULL DEFAULT 'warning',
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(ico, zmluva_id, flag_type)
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_srf_ico ON supplier_red_flags(ico)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_srf_zmluva ON supplier_red_flags(zmluva_id)")
    db.commit()


def scrape_finstat(client, ico):
    """Scrape basic financial data from finstat.sk for a given IČO."""
    url = f"https://finstat.sk/{ico}"
    r = client.get(url, headers=FINSTAT_HEADERS, follow_redirects=True)
    text = r.text
    data = {"ico": ico}

    # Company name
    m = re.search(r"<title>(.*?) - zisk", text)
    if m:
        data["nazov"] = html.unescape(m.group(1).strip())

    # Meta description: Zisk, Tržby, Aktíva
    m = re.search(r'og:description.*?content="(.*?)"', text)
    if m:
        desc = html.unescape(m.group(1))
        for pair in desc.split(","):
            pair = pair.strip()
            if ":" in pair:
                k, v = pair.split(":", 1)
                v = v.strip().replace("\xa0", "").replace("€", "").replace(" ", "").strip()
                try:
                    v = int(v)
                except ValueError:
                    v = None
                k = k.strip().lower()
                if "zisk" in k:
                    data["zisk"] = v
                elif "tržby" in k or "trzby" in k:
                    data["trzby"] = v
                elif "aktíva" in k or "aktiva" in k:
                    data["aktiva"] = v

    # Date founded
    m = re.search(r"Dátum vzniku.*?<span>(.*?)</span>", text)
    if m:
        data["datum_vzniku"] = html.unescape(m.group(1).strip())

    # Vlastný kapitál
    m = re.search(r"Vlastn.*?kapit.*?>([\d\s\xa0]+)\s*€", text)
    if m:
        data["vlastny_kapital"] = int(
            m.group(1).replace(" ", "").replace("\xa0", "")
        )

    # Celková zadlženosť
    m = re.search(r'Celkov.*?zadlženosť.*?>([\d,]+)\s*%', text)
    if m:
        data["celkova_zadlzenost_pct"] = float(m.group(1).replace(",", "."))

    # Check if page says 404 / not found
    if "<title>Stránka sa nenašla" in text or r.status_code == 404:
        data["_not_found"] = True

    return data


def parse_datum_vzniku(raw):
    """Parse Slovak date like 'piatok 25. mája 2018' to 'YYYY-MM-DD'."""
    if not raw:
        return None
    months = {
        "januára": 1, "februára": 2, "marca": 3, "apríla": 4,
        "mája": 5, "júna": 6, "júla": 7, "augusta": 8,
        "septembra": 9, "októbra": 10, "novembra": 11, "decembra": 12,
    }
    m = re.search(r"(\d+)\.\s*(\w+)\s+(\d{4})", raw)
    if m:
        day = int(m.group(1))
        month_name = m.group(2).lower()
        year = int(m.group(3))
        month = months.get(month_name)
        if month:
            return f"{year:04d}-{month:02d}-{day:02d}"
    return None


def evaluate_red_flags(db, ico, zmluva_id, suma, datum_podpisu):
    """Evaluate red flag rules for a supplier+contract pair."""
    fin = db.execute(
        "SELECT * FROM supplier_financials WHERE ico = ?", (ico,)
    ).fetchone()
    if not fin:
        return []

    flags = []
    trzby = fin["trzby"]
    zisk = fin["zisk"]
    vlastny_kapital = fin["vlastny_kapital"]
    datum_vzniku_raw = fin["datum_vzniku"]
    tax_rel = fin["tax_reliability"]

    # 1. Hodnota zmluvy > 2× Tržby
    if suma and trzby and trzby > 0 and suma > 2 * trzby:
        flags.append({
            "flag_type": "contract_exceeds_2x_revenue",
            "detail": f"Zmluva {suma:,.0f} EUR > 2× tržby {trzby:,.0f} EUR ({suma/trzby:.1f}×)",
            "severity": "danger",
        })

    # 2. Záporné vlastné imanie
    if vlastny_kapital is not None and vlastny_kapital < 0:
        flags.append({
            "flag_type": "negative_equity",
            "detail": f"Vlastné imanie: {vlastny_kapital:,.0f} EUR",
            "severity": "danger",
        })

    # 3. Vysoký zisk: Zisk > 0.5× Tržby
    if zisk and trzby and trzby > 0 and zisk > 0.5 * trzby:
        flags.append({
            "flag_type": "unusually_high_profit",
            "detail": f"Zisk {zisk:,.0f} EUR > 50% tržieb {trzby:,.0f} EUR ({zisk/trzby*100:.0f}%)",
            "severity": "warning",
        })

    # 4. Vysoká strata: Zisk < -(0.3× Tržby)
    if zisk and trzby and trzby > 0 and zisk < -(0.3 * trzby):
        flags.append({
            "flag_type": "severe_loss",
            "detail": f"Strata {zisk:,.0f} EUR > 30% tržieb {trzby:,.0f} EUR",
            "severity": "danger",
        })

    # 5. Nie je v RPVS (pre zmluvy nad 100K by mal byť)
    # Only flag if we actually checked RPVS (rpvs_status is set)
    rpvs = fin["rpvs_status"]
    if suma and suma > 100000 and rpvs == "not_found":
        flags.append({
            "flag_type": "missing_rpvs",
            "detail": "Nie je v registri partnerov verejného sektora (zmluva > 100K EUR)",
            "severity": "warning",
        })

    # 6. Index daňovej spoľahlivosti = menej spoľahlivý
    if tax_rel and tax_rel == "menej spoľahlivý":
        flags.append({
            "flag_type": "tax_unreliable",
            "detail": "Index daňovej spoľahlivosti: menej spoľahlivý",
            "severity": "danger",
        })

    # 7. Dátum uzavretia zmluvy - Dátum vzniku firmy < 1 rok
    datum_vzniku_iso = parse_datum_vzniku(datum_vzniku_raw)
    if datum_vzniku_iso and datum_podpisu:
        try:
            founded = datetime.strptime(datum_vzniku_iso, "%Y-%m-%d")
            signed = datetime.strptime(datum_podpisu[:10], "%Y-%m-%d")
            age_days = (signed - founded).days
            if 0 < age_days < 365:
                flags.append({
                    "flag_type": "young_company",
                    "detail": f"Firma založená {datum_vzniku_iso}, zmluva podpísaná {datum_podpisu[:10]} ({age_days} dní po založení)",
                    "severity": "warning",
                })
        except (ValueError, TypeError):
            pass

    return flags


def get_top_suppliers(db, date_from, date_to, limit):
    """Get suppliers ranked by total contract value in period."""
    query = """
        SELECT dodavatel_ico as ico,
               dodavatel as nazov,
               count(*) as pocet_zmluv,
               sum(suma) as celkova_suma,
               max(suma) as max_suma
        FROM zmluvy
        WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''
          AND suma IS NOT NULL AND suma > 0
          AND datum_zverejnenia >= ? AND datum_zverejnenia < ?
        GROUP BY dodavatel_ico
        ORDER BY sum(suma) DESC
    """
    params = [date_from, date_to]
    if limit > 0:
        query += " LIMIT ?"
        params.append(limit)
    return db.execute(query, params).fetchall()


def get_contracts_for_supplier(db, ico, date_from, date_to):
    """Get all contracts for a supplier in period."""
    return db.execute("""
        SELECT id, nazov_zmluvy, suma, datum_podpisu, datum_zverejnenia
        FROM zmluvy
        WHERE dodavatel_ico = ?
          AND suma IS NOT NULL AND suma > 0
          AND datum_zverejnenia >= ? AND datum_zverejnenia < ?
        ORDER BY suma DESC
    """, (ico, date_from, date_to)).fetchall()


def resolve_date_range(args):
    """Resolve --from/--to or --month into (date_from, date_to_exclusive) strings."""
    if args.date_from:
        date_from = args.date_from + "-01" if len(args.date_from) == 7 else args.date_from
        if args.date_to:
            if len(args.date_to) == 7:
                # Month end: use SQLite date() +1 month trick at query time
                date_to = args.date_to + "-32"  # will be clamped below
            else:
                date_to = args.date_to
        else:
            date_to = date_from
    else:
        date_from = args.month + "-01"
        date_to = args.month + "-32"

    # For simplicity, use the 32nd day trick: any YYYY-MM-32 > all dates in that month
    return date_from, date_to


def main():
    parser = argparse.ArgumentParser(description="Enrich CRZ suppliers with FinStat data")
    parser.add_argument("--limit", type=int, default=100, help="Max suppliers to enrich (default: 100)")
    parser.add_argument("--ico", type=str, help="Enrich a single IČO")
    parser.add_argument("--month", type=str, default="2026-01",
                        help="Month to analyze (YYYY-MM, default: 2026-01)")
    parser.add_argument("--from", type=str, dest="date_from",
                        help="Start date (YYYY-MM-DD or YYYY-MM)")
    parser.add_argument("--to", type=str, dest="date_to",
                        help="End date (YYYY-MM-DD or YYYY-MM)")
    parser.add_argument("--flags-only", action="store_true",
                        help="Skip scraping, only re-evaluate red flags")
    parser.add_argument("--force", action="store_true",
                        help="Re-scrape even if data exists")
    parser.add_argument("--workers", type=int, default=4,
                        help="Parallel scraping workers (default: 4, be gentle)")
    args = parser.parse_args()

    db = get_db()
    init_tables(db)

    date_from, date_to = resolve_date_range(args)
    period = f"{args.date_from or args.month} to {args.date_to or args.month}"

    if args.ico:
        suppliers = [{"ico": args.ico, "nazov": "", "pocet_zmluv": 0, "celkova_suma": 0}]
    else:
        suppliers = get_top_suppliers(db, date_from, date_to, args.limit)
        print(f"Period {period}: {len(suppliers)} suppliers to process")

    # --- Phase 1: Scrape financial data ---
    if not args.flags_only:
        if args.force:
            to_scrape = [s["ico"] for s in suppliers]
        else:
            existing = set(
                r[0] for r in db.execute(
                    "SELECT ico FROM supplier_financials"
                ).fetchall()
            )
            to_scrape = [s["ico"] for s in suppliers if s["ico"] not in existing]

        print(f"Scraping: {len(to_scrape)} new, {len(suppliers) - len(to_scrape)} cached")

        if to_scrape:
            ok, fail = 0, 0
            pbar = tqdm(total=len(to_scrape), desc="Scraping FinStat", unit="company")

            def scrape_one(ico, client):
                try:
                    data = scrape_finstat(client, ico)
                    time.sleep(0.5)  # be gentle
                    return (ico, data, None)
                except Exception as e:
                    return (ico, None, str(e))

            with httpx.Client(timeout=15) as client:
                with ThreadPoolExecutor(max_workers=args.workers) as pool:
                    futures = {pool.submit(scrape_one, ico, client): ico for ico in to_scrape}
                    for future in as_completed(futures):
                        ico, data, error = future.result()
                        pbar.update(1)
                        if error:
                            pbar.write(f"  FAIL {ico}: {error}")
                            fail += 1
                        elif data.get("_not_found"):
                            pbar.write(f"  NOT FOUND {ico}")
                            fail += 1
                        else:
                            # Enrich with local tax reliability
                            tax_row = db.execute(
                                "SELECT status FROM tax_reliability WHERE ico = ?", (ico,)
                            ).fetchone()
                            data["tax_reliability"] = tax_row["status"] if tax_row else None

                            db.execute("""
                                INSERT OR REPLACE INTO supplier_financials
                                (ico, nazov, datum_vzniku, trzby, zisk, aktiva,
                                 vlastny_kapital, celkova_zadlzenost_pct,
                                 tax_reliability, raw_json)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                data.get("ico"),
                                data.get("nazov"),
                                data.get("datum_vzniku"),
                                data.get("trzby"),
                                data.get("zisk"),
                                data.get("aktiva"),
                                data.get("vlastny_kapital"),
                                data.get("celkova_zadlzenost_pct"),
                                data.get("tax_reliability"),
                                json.dumps(data, ensure_ascii=False),
                            ))
                            db.commit()
                            ok += 1
                        pbar.set_postfix(ok=ok, fail=fail)

            pbar.close()
            print(f"Scraped: {ok} ok, {fail} failed")

    # --- Phase 2: Evaluate red flags ---
    print("\nEvaluating red flags...")
    total_flags = 0

    for s in tqdm(suppliers, desc="Evaluating flags", unit="supplier"):
        ico = s["ico"]
        contracts = get_contracts_for_supplier(db, ico, date_from, date_to)

        for c in contracts:
            flags = evaluate_red_flags(
                db, ico, c["id"], c["suma"], c["datum_podpisu"]
            )
            for f in flags:
                db.execute("""
                    INSERT OR IGNORE INTO supplier_red_flags
                    (ico, zmluva_id, flag_type, detail, severity)
                    VALUES (?, ?, ?, ?, ?)
                """, (ico, c["id"], f["flag_type"], f["detail"], f["severity"]))
                total_flags += 1

    db.commit()

    # --- Phase 3: Summary ---
    print(f"\nTotal new flags inserted: {total_flags}")
    total_in_db = db.execute("SELECT count(*) FROM supplier_red_flags").fetchone()[0]
    print(f"Total flags in DB: {total_in_db}")

    print("\nFlag summary:")
    for row in db.execute("""
        SELECT flag_type, severity, count(*) as cnt
        FROM supplier_red_flags
        GROUP BY flag_type, severity
        ORDER BY cnt DESC
    """).fetchall():
        print(f"  [{row['severity']:7s}] {row['flag_type']:35s} {row['cnt']:>5} flags")

    # Show top flagged suppliers
    print("\nTop flagged suppliers:")
    for row in db.execute("""
        SELECT sf.ico, sf.nazov, count(DISTINCT srf.flag_type) as flag_types,
               count(*) as total_flags,
               group_concat(DISTINCT srf.flag_type) as flags
        FROM supplier_red_flags srf
        JOIN supplier_financials sf ON srf.ico = sf.ico
        GROUP BY srf.ico
        ORDER BY count(DISTINCT srf.flag_type) DESC, count(*) DESC
        LIMIT 15
    """).fetchall():
        nazov = (row['nazov'] or row['ico'])[:50]
        print(f"  {nazov:50s} {row['flag_types']} types, {row['total_flags']:>4} flags  [{row['flags']}]")

    db.close()


if __name__ == "__main__":
    main()
