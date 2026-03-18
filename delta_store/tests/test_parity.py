"""Cross-check: SQLite (Datasette) server vs Delta Lake (FastAPI) server.

Both servers must be running:
    SQLite:     uv run python server/serve.py --port 8001
    Delta Lake: uv run python delta_store/serve.py --port 8002

Run:
    uv run pytest delta_store/tests/test_parity.py -v
    uv run pytest delta_store/tests/test_parity.py -v -k test_sql_api

Environment variables:
    SQLITE_URL=http://localhost:8001  (default)
    DELTA_URL=http://localhost:8002   (default)
"""

import json
import math
import os

import httpx
import pytest

SQLITE_URL = os.getenv("SQLITE_URL", "http://localhost:8001")
DELTA_URL = os.getenv("DELTA_URL", "http://localhost:8002")

# Tolerance for floating-point comparisons
FLOAT_TOLERANCE = 0.01


def approx_equal(a, b, tol=FLOAT_TOLERANCE):
    """Compare values, handling floats, None, and nested structures."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return abs(a - b) <= tol * max(1, abs(a), abs(b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tol * max(1, abs(float(a)), abs(float(b)))
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(approx_equal(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(approx_equal(x, y, tol) for x, y in zip(a, b))
    return a == b


def fetch(base_url, path, params=None):
    """Fetch JSON from a server."""
    r = httpx.get(f"{base_url}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def compare_responses(path, params=None, key_sort=None):
    """Fetch from both servers and compare results."""
    sqlite_resp = fetch(SQLITE_URL, path, params)
    delta_resp = fetch(DELTA_URL, path, params)

    # Sort lists by a key if specified (order may differ between engines)
    if key_sort and isinstance(sqlite_resp, list):
        sqlite_resp = sorted(sqlite_resp, key=lambda x: x.get(key_sort, ""))
        delta_resp = sorted(delta_resp, key=lambda x: x.get(key_sort, ""))

    assert approx_equal(sqlite_resp, delta_resp), (
        f"Mismatch on {path}:\n"
        f"SQLite: {json.dumps(sqlite_resp, ensure_ascii=False, default=str)[:500]}\n"
        f"Delta:  {json.dumps(delta_resp, ensure_ascii=False, default=str)[:500]}"
    )
    return sqlite_resp


# ---------------------------------------------------------------------------
# SQL API parity
# ---------------------------------------------------------------------------

SQL_QUERIES = [
    "SELECT count(*) as cnt FROM zmluvy",
    "SELECT count(*) as cnt FROM red_flags",
    "SELECT count(*) as cnt FROM extractions",
    "SELECT count(*) as cnt FROM prilohy",
    "SELECT count(*) as cnt FROM flag_rules",
    "SELECT count(*) as cnt FROM tax_reliability",
    "SELECT count(*) as cnt FROM vszp_debtors",
    "SELECT count(*) as cnt FROM socpoist_debtors",
    "SELECT count(*) as cnt FROM fs_tax_debtors",
    "SELECT count(*) as cnt FROM ruz_entities",
    "SELECT count(*) as cnt FROM rezorty",
]


@pytest.mark.parametrize("sql", SQL_QUERIES, ids=[s.split("FROM ")[-1].split()[0] for s in SQL_QUERIES])
def test_sql_api_counts(sql):
    """Row counts must match across all tables."""
    sqlite_resp = fetch(SQLITE_URL, "/data/crz.json", {"sql": sql, "_shape": "array"})
    delta_resp = fetch(DELTA_URL, "/data/crz.json", {"sql": sql, "_shape": "array"})
    assert sqlite_resp == delta_resp, f"SQL count mismatch for: {sql}"


# ---------------------------------------------------------------------------
# Dashboard API parity
# ---------------------------------------------------------------------------

def test_api_filters():
    compare_responses("/api/filters")


def test_api_summary():
    compare_responses("/api/summary")


def test_api_summary_filtered():
    compare_responses("/api/summary", {"date_from": "2026-01-01", "date_to": "2026-01-31"})


def test_api_timeline():
    compare_responses("/api/timeline")


def test_api_by_rezort():
    compare_responses("/api/by_rezort")


def test_api_by_category():
    compare_responses("/api/by_category", key_sort="category")


def test_api_penalties():
    compare_responses("/api/penalties")


def test_api_top_contracts():
    """Top contracts — verify same amounts returned (IDs may differ on ties)."""
    sqlite_resp = fetch(SQLITE_URL, "/api/top_contracts")
    delta_resp = fetch(DELTA_URL, "/api/top_contracts")
    assert len(sqlite_resp) == len(delta_resp), "top_contracts length mismatch"
    # Top 10 by value should match (beyond that, ties cause divergence)
    sqlite_top = sorted(sqlite_resp, key=lambda r: -(r["suma"] or 0))[:10]
    delta_top = sorted(delta_resp, key=lambda r: -(r["suma"] or 0))[:10]
    for s, d in zip(sqlite_top, delta_top):
        assert s["id"] == d["id"], f"top contract mismatch: {s['id']} vs {d['id']}"


def test_api_anomalies():
    resp = compare_responses("/api/anomalies")
    assert "anomalies" in resp
    assert "amount_distribution" in resp


def test_api_detail_contract():
    """Fetch a specific contract detail and compare."""
    # Get any contract ID first
    rows = fetch(SQLITE_URL, "/data/crz.json", {"sql": "SELECT id FROM zmluvy LIMIT 1", "_shape": "array"})
    if not rows:
        pytest.skip("No contracts in database")
    cid = rows[0]["id"]
    compare_responses("/api/detail", {"id": str(cid)})


def test_api_flags():
    """Flags — compare rule counts and total_flagged."""
    sqlite_resp = fetch(SQLITE_URL, "/api/flags")
    delta_resp = fetch(DELTA_URL, "/api/flags")
    assert sqlite_resp["total_flagged"] == delta_resp["total_flagged"], "total_flagged mismatch"
    sqlite_rules = {r["id"]: r["count"] for r in sqlite_resp["rules"]}
    delta_rules = {r["id"]: r["count"] for r in delta_resp["rules"]}
    assert sqlite_rules == delta_rules, f"Rule counts differ: {sqlite_rules} vs {delta_rules}"


def test_api_flags_by_rezort():
    """Flags by rezort — compare flagged counts per rezort."""
    sqlite_resp = fetch(SQLITE_URL, "/api/flags_by_rezort")
    delta_resp = fetch(DELTA_URL, "/api/flags_by_rezort")
    sqlite_map = {r["rezort_id"]: r["flagged"] for r in sqlite_resp}
    delta_map = {r["rezort_id"]: r["flagged"] for r in delta_resp}
    assert sqlite_map == delta_map, "flags_by_rezort counts differ"


def test_api_flags_top():
    """Flags top — same set, order may differ on ties."""
    sqlite_resp = fetch(SQLITE_URL, "/api/flags_top")
    delta_resp = fetch(DELTA_URL, "/api/flags_top")
    assert len(sqlite_resp) == len(delta_resp), "flags_top length mismatch"
    sqlite_ids = sorted(r["id"] for r in sqlite_resp)
    delta_ids = sorted(r["id"] for r in delta_resp)
    assert sqlite_ids == delta_ids, f"flags_top IDs differ"


def test_api_flags_timeline():
    compare_responses("/api/flags_timeline")


def test_api_contracts():
    """Contracts — same count, same set (order may differ on ties)."""
    sqlite_resp = fetch(SQLITE_URL, "/api/contracts", {"date_from": "2026-03-01", "date_to": "2026-03-07"})
    delta_resp = fetch(DELTA_URL, "/api/contracts", {"date_from": "2026-03-01", "date_to": "2026-03-07"})
    assert len(sqlite_resp) == len(delta_resp), "contracts length mismatch"
    # Both should return 200 rows (LIMIT), verify overlap is high
    sqlite_ids = set(r["id"] for r in sqlite_resp)
    delta_ids = set(r["id"] for r in delta_resp)
    overlap = len(sqlite_ids & delta_ids) / len(sqlite_ids) if sqlite_ids else 1
    assert overlap > 0.95, f"contracts overlap too low: {overlap:.0%}"


def test_api_browse():
    sqlite_resp = fetch(SQLITE_URL, "/api/browse", {"limit": "5"})
    delta_resp = fetch(DELTA_URL, "/api/browse", {"limit": "5"})
    assert sqlite_resp["total"] == delta_resp["total"], "Browse total mismatch"
    assert len(sqlite_resp["rows"]) == len(delta_resp["rows"]), "Browse row count mismatch"


def test_api_browse_filters():
    compare_responses("/api/browse_filters")


def test_api_search():
    """Search totals may differ due to FTS tokenization differences — allow 10% tolerance."""
    sqlite_resp = fetch(SQLITE_URL, "/api/search", {"q": "ministerstvo", "limit": "10"})
    delta_resp = fetch(DELTA_URL, "/api/search", {"q": "ministerstvo", "limit": "10"})
    s_total = sqlite_resp["total"]
    d_total = delta_resp["total"]
    diff_pct = abs(s_total - d_total) / max(s_total, 1)
    assert diff_pct < 0.10, (
        f"Search total diff too large: sqlite={s_total}, delta={d_total} ({diff_pct:.0%})"
    )


def test_api_investigation_categories():
    """Investigation categories — counts may differ slightly due to engine differences.

    DuckDB's lower()/trim() and date casting differ from SQLite on edge cases.
    Allow 5% tolerance per category.
    """
    sqlite_resp = fetch(SQLITE_URL, "/api/investigation_categories")
    delta_resp = fetch(DELTA_URL, "/api/investigation_categories")
    sqlite_cats = {c["id"]: c["count"] for c in sqlite_resp["categories"]}
    delta_cats = {c["id"]: c["count"] for c in delta_resp["categories"]}
    assert set(sqlite_cats.keys()) == set(delta_cats.keys()), "Category IDs differ"
    for cat_id in sqlite_cats:
        s, d = sqlite_cats[cat_id], delta_cats[cat_id]
        diff_pct = abs(s - d) / max(s, 1)
        assert diff_pct < 0.05, (
            f"Category {cat_id} count diff too large: sqlite={s}, delta={d} ({diff_pct:.0%})"
        )
