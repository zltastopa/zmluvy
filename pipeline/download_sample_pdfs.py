"""Download PDF attachments from CRZ for extraction.

Usage:
    python download_sample_pdfs.py                          # default: 1000 PDFs for current month
    python download_sample_pdfs.py --limit 500              # limit count
    python download_sample_pdfs.py --month 2026-02          # single month
    python download_sample_pdfs.py --from 2026-01-01 --to 2026-01-15  # date range
    python download_sample_pdfs.py --from 2026-01 --to 2026-03        # month range
    python download_sample_pdfs.py --all                    # all PDFs for the period (ignores --limit)
"""
import confpath  # noqa: F401

import sqlite_utils
import httpx
import os
import argparse
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

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
        help=f"Month to download (YYYY-MM, default: {default_month}). Ignored if --from is used.",
    )
    parser.add_argument(
        "--from",
        type=str,
        dest="date_from",
        help="Start date (YYYY-MM-DD) or month (YYYY-MM). Inclusive.",
    )
    parser.add_argument(
        "--to",
        type=str,
        dest="date_to",
        help="End date (YYYY-MM-DD) or month (YYYY-MM). Inclusive.",
    )
    parser.add_argument("--all", action="store_true", help="Download all PDFs for the period (ignores --limit)")
    parser.add_argument("--workers", type=int, default=16, help="Parallel workers (default: 16)")
    args = parser.parse_args()

    limit = 0 if args.all else args.limit

    # Resolve date range
    if args.date_from:
        date_from = args.date_from + "-01" if len(args.date_from) == 7 else args.date_from
        if args.date_to:
            # If --to is a month (YYYY-MM), make it the last day by using first of next month
            if len(args.date_to) == 7:
                date_to_exclusive = args.date_to + "-01"
                use_date_to_month = True
            else:
                # Specific date — make it inclusive by adding 1 day
                date_to_exclusive = args.date_to
                use_date_to_month = False
        else:
            # Only --from given, use single day or month
            if len(args.date_from) == 7:
                date_to_exclusive = args.date_from + "-01"
                use_date_to_month = True
            else:
                date_to_exclusive = args.date_from
                use_date_to_month = False
        period_label = f"{args.date_from} to {args.date_to or args.date_from}"
    else:
        date_from = args.month + "-01"
        date_to_exclusive = args.month + "-01"
        use_date_to_month = True
        period_label = args.month

    db = sqlite_utils.Database(get_path("CRZ_DB_PATH", "crz.db"))
    out_dir = get_path("CRZ_PDF_DIR", "data/pdfs")
    os.makedirs(out_dir, exist_ok=True)

    # Already downloaded files
    existing = set(f for f in os.listdir(out_dir) if f.endswith(".pdf") and os.path.getsize(os.path.join(out_dir, f)) > 0)

    if use_date_to_month:
        date_filter = "z.datum_zverejnenia >= ? AND z.datum_zverejnenia < date(?, '+1 month')"
    else:
        date_filter = "z.datum_zverejnenia >= ? AND z.datum_zverejnenia < date(?, '+1 day')"

    query = f'''
        select p.url, p.subor, z.nazov_zmluvy, z.suma, z.rezort, z.id as zmluva_id
        from prilohy p
        join zmluvy z on p.zmluva_id = z.id
        where p.subor like '%.pdf'
          and {date_filter}
        group by z.id
        order by random()
    '''
    params = [date_from, date_to_exclusive]
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
    print(f"Period {period_label}: {len(rows)} PDFs queried, {already} already downloaded, {total} to download")

    if total == 0:
        print("Nothing to download.")
        return

    ok, fail = 0, 0
    total_bytes = 0

    def download_one(item):
        url, subor, nazov, suma, rezort, zmluva_id = item
        dest = os.path.join(out_dir, subor)
        try:
            resp = client.get(url)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                f.write(resp.content)
            return (subor, len(resp.content), None)
        except Exception as e:
            return (subor, 0, str(e))

    pbar = tqdm(total=total, desc="Downloading", unit="pdf")

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
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
    print(f"\nDone: {ok} downloaded, {fail} failed, {already} already had, {total_bytes/1024/1024:.0f} MB total")


if __name__ == "__main__":
    main()
