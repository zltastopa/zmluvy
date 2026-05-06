"""Post a daily red-flag report to Discord via webhook.

Reports flags on contracts published in the last day (default: yesterday).
Reads DISCORD_WEBHOOK_URL from .env and uses Delta tables on disk.

Usage:
    uv run python -m delta_store.discord_report                  # report on yesterday
    uv run python -m delta_store.discord_report --date 2026-05-05
    uv run python -m delta_store.discord_report --dry-run        # print, don't post
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import duckdb
import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from settings import get_env  # noqa: E402

TABLES_DIR = Path(__file__).resolve().parent / "tables"
DASHBOARD_URL = "https://zmluvy.zltastopa.sk"
TOP_N_CONTRACTS = 10


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def fmt_money(amount: float | None) -> str:
    if amount is None:
        return "—"
    return f"{amount:,.0f} €".replace(",", " ")


def build_report(report_date: date) -> dict | None:
    """Build a Discord embed payload for the given publication date."""
    con = duckdb.connect()
    con.execute("INSTALL delta; LOAD delta;")

    zmluvy_path = str(TABLES_DIR / "zmluvy")
    flags_path = str(TABLES_DIR / "red_flags")

    iso = report_date.isoformat()
    date_from_ts = f"{iso} 00:00:00"
    date_to_ts = f"{iso} 23:59:59"

    # Total flag and contract counts
    totals = con.execute(
        f"""
        SELECT
            COUNT(*) AS flag_count,
            COUNT(DISTINCT f.zmluva_id) AS contract_count
        FROM delta_scan('{flags_path}') f
        JOIN delta_scan('{zmluvy_path}') z ON z.id = f.zmluva_id
        WHERE z.datum_zverejnenia >= ? AND z.datum_zverejnenia <= ?
        """,
        [date_from_ts, date_to_ts],
    ).fetchone()
    flag_count, contract_count = totals

    if flag_count == 0:
        return None

    # Per-rule summary
    rule_rows = con.execute(
        f"""
        SELECT f.flag_type, COUNT(*) AS cnt
        FROM delta_scan('{flags_path}') f
        JOIN delta_scan('{zmluvy_path}') z ON z.id = f.zmluva_id
        WHERE z.datum_zverejnenia >= ? AND z.datum_zverejnenia <= ?
        GROUP BY f.flag_type
        ORDER BY cnt DESC
        """,
        [date_from_ts, date_to_ts],
    ).fetchall()

    # Top contracts by suma (with at least one flag)
    top_rows = con.execute(
        f"""
        SELECT
            z.id, z.nazov_zmluvy, z.dodavatel, z.objednavatel, z.suma,
            string_agg(DISTINCT f.flag_type, ', ') AS flags
        FROM delta_scan('{flags_path}') f
        JOIN delta_scan('{zmluvy_path}') z ON z.id = f.zmluva_id
        WHERE z.datum_zverejnenia >= ? AND z.datum_zverejnenia <= ?
          AND z.suma IS NOT NULL
        GROUP BY z.id, z.nazov_zmluvy, z.dodavatel, z.objednavatel, z.suma
        ORDER BY z.suma DESC
        LIMIT {TOP_N_CONTRACTS}
        """,
        [date_from_ts, date_to_ts],
    ).fetchall()

    dashboard_link = (
        f"{DASHBOARD_URL}/?date_from={iso}&date_to={iso}&has_flag=1"
    )

    # Build description: top contracts list
    lines = []
    for zid, nazov, dodavatel, objednavatel, suma, flags in top_rows:
        title = (nazov or "(bez názvu)").strip()
        if len(title) > 80:
            title = title[:77] + "…"
        lines.append(
            f"**[{title}]({DASHBOARD_URL}/browse/{zid})** — {fmt_money(suma)}\n"
            f"  {dodavatel or '?'} → {objednavatel or '?'}\n"
            f"  🚩 {flags}"
        )
    top_block = "\n\n".join(lines) if lines else "_Žiadne zmluvy so sumou_"

    # Per-rule field (compact)
    rule_lines = [f"`{fmt_int(cnt):>6}`  {rule}" for rule, cnt in rule_rows]
    rule_block = "\n".join(rule_lines)
    if len(rule_block) > 1000:
        # Trim to fit Discord field value limit (1024)
        rule_block = "\n".join(rule_lines[:30]) + f"\n_…+{len(rule_lines) - 30} more_"

    embed = {
        "title": f"🚩 Red flags za {iso}",
        "url": dashboard_link,
        "description": (
            f"**{fmt_int(flag_count)}** flagov na **{fmt_int(contract_count)}** zmluvách\n\n"
            f"**Top {len(top_rows)} podľa sumy:**\n\n{top_block}"
        ),
        "color": 0xE74C3C,
        "fields": [
            {
                "name": f"Podľa typu flagu ({len(rule_rows)})",
                "value": rule_block,
                "inline": False,
            }
        ],
    }
    return {"embeds": [embed]}


def post_to_discord(webhook_url: str, payload: dict) -> None:
    resp = httpx.post(webhook_url, json=payload, timeout=30)
    resp.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Post daily red-flag report to Discord")
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=date.today() - timedelta(days=1),
        help="Publication date to report on (default: yesterday, format: YYYY-MM-DD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload instead of posting",
    )
    args = parser.parse_args()

    payload = build_report(args.date)
    if payload is None:
        print(f"No flags for {args.date}, skipping.")
        return

    if args.dry_run:
        import json
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    webhook = get_env("DISCORD_WEBHOOK_URL", "")
    if not webhook:
        sys.exit("ERROR: DISCORD_WEBHOOK_URL not set in .env")

    post_to_discord(webhook, payload)
    print(f"Posted report for {args.date} to Discord.")


if __name__ == "__main__":
    main()
