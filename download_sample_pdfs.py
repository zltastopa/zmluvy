"""Download PDF attachments from CRZ for extraction.

Usage:
    python download_sample_pdfs.py                  # default: 1000 March 2026 PDFs
    python download_sample_pdfs.py --limit 500      # limit count
    python download_sample_pdfs.py --month 2026-02  # different month
    python download_sample_pdfs.py --all             # all PDFs for the month
"""
import sqlite_utils
import httpx
import os
import argparse
from datetime import date

from settings import get_env, get_path


def main():
    parser = argparse.ArgumentParser(description="Download CRZ PDF attachments")
    default_limit = int(get_env("CRZ_DOWNLOAD_LIMIT", "1000"))
    parser.add_argument(
        "--limit",
        type=int,
        default=default_limit,
        help=f"Max PDFs to download (default: {default_limit}, 0=unlimited)",
    )
    default_month = get_env("CRZ_DOWNLOAD_MONTH", date.today().strftime("%Y-%m"))
    parser.add_argument(
        "--month",
        type=str,
        default=default_month,
        help=f"Month to download (YYYY-MM, default: {default_month})",
    )
    parser.add_argument("--all", action="store_true", help="Download all PDFs for the month (ignores --limit)")
    args = parser.parse_args()

    limit = 0 if args.all else args.limit

    db = sqlite_utils.Database(get_path("CRZ_DB_PATH", "crz.db"))
    out_dir = get_path("CRZ_PDF_DIR", "data/pdfs")
    os.makedirs(out_dir, exist_ok=True)

    # Already downloaded files
    existing = set(f for f in os.listdir(out_dir) if f.endswith(".pdf") and os.path.getsize(os.path.join(out_dir, f)) > 0)

    query = '''
        select p.url, p.subor, z.nazov_zmluvy, z.suma, z.rezort, z.id as zmluva_id
        from prilohy p
        join zmluvy z on p.zmluva_id = z.id
        where p.subor like '%.pdf'
          and z.datum_zverejnenia >= ? and z.datum_zverejnenia < date(?, '+1 month')
        group by z.id
        order by random()
    '''
    params = [args.month + "-01", args.month + "-01"]
    if limit > 0:
        query += " limit ?"
        params.append(limit + len(existing))  # overfetch to account for skips

    rows = db.execute(query, params).fetchall()

    # Filter out already downloaded
    to_download = [(url, subor, nazov, suma, rezort, zid)
                   for url, subor, nazov, suma, rezort, zid in rows
                   if subor not in existing]

    if limit > 0:
        to_download = to_download[:limit]

    already = len(rows) - len(to_download)
    total = len(to_download)
    print(f"Month {args.month}: {len(rows)} PDFs queried, {already} already downloaded, {total} to download")

    if total == 0:
        print("Nothing to download.")
        return

    ok, fail = 0, 0
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        for i, (url, subor, nazov, suma, rezort, zmluva_id) in enumerate(to_download):
            dest = os.path.join(out_dir, subor)
            try:
                resp = client.get(url)
                resp.raise_for_status()
                with open(dest, "wb") as f:
                    f.write(resp.content)
                size_kb = len(resp.content) / 1024
                print(f"  [{i+1}/{total}] {subor} ({size_kb:.0f} KB) - {nazov[:60]}")
                ok += 1
            except Exception as e:
                print(f"  [{i+1}/{total}] FAIL {subor}: {e}")
                fail += 1

    print(f"\nDone: {ok} downloaded, {fail} failed, {already} already had")


if __name__ == "__main__":
    main()
