"""Benchmark: SQLite (Datasette) vs Delta Lake (DuckDB+FastAPI) server performance.

Both servers must be running:
    uv run python server/serve.py --port 8001
    uv run python delta_store/serve.py --port 8002

Run:
    uv run python delta_store/tests/benchmark.py
    uv run python delta_store/tests/benchmark.py --rounds 5
"""

import argparse
import json
import statistics
import time
import sys

import httpx

SQLITE_URL = "http://localhost:8001"
DELTA_URL = "http://localhost:8002"

BENCHMARKS = [
    # (name, path, params, category)
    ("Row count (zmluvy)", "/data/crz.json",
     {"sql": "SELECT count(*) as cnt FROM zmluvy", "_shape": "array"}, "sql"),

    ("Aggregate SUM/AVG", "/data/crz.json",
     {"sql": "SELECT count(*) as n, sum(suma) as total, avg(suma) as avg_val FROM zmluvy WHERE suma IS NOT NULL", "_shape": "array"}, "sql"),

    ("GROUP BY rezort (top 20)", "/data/crz.json",
     {"sql": "SELECT rezort, count(*) as cnt, sum(suma) as total FROM zmluvy WHERE rezort != '' GROUP BY rezort ORDER BY cnt DESC LIMIT 20", "_shape": "array"}, "sql"),

    ("JOIN zmluvy+red_flags", "/data/crz.json",
     {"sql": "SELECT z.id, z.dodavatel, z.suma, count(rf.id) as flags FROM zmluvy z LEFT JOIN red_flags rf ON rf.zmluva_id = z.id WHERE z.suma > 1000000 GROUP BY z.id, z.dodavatel, z.suma ORDER BY flags DESC LIMIT 20", "_shape": "array"}, "sql"),

    ("Correlated subquery (dormant firms)", "/data/crz.json",
     {"sql": """SELECT z.dodavatel_ico, count(*) as cnt, sum(z.suma) as total
        FROM zmluvy z
        WHERE z.dodavatel_ico IN (
            SELECT cin FROM ruz_entities WHERE terminated_on IS NOT NULL
        ) AND z.suma IS NOT NULL
        GROUP BY z.dodavatel_ico
        ORDER BY total DESC LIMIT 10""", "_shape": "array"}, "sql"),

    ("Date range filter", "/data/crz.json",
     {"sql": "SELECT count(*) as cnt, sum(suma) as total FROM zmluvy WHERE datum_zverejnenia >= '2026-02-01' AND datum_zverejnenia < '2026-03-01'", "_shape": "array"}, "sql"),

    ("Multi-table JOIN (supplier profile)", "/data/crz.json",
     {"sql": """SELECT z.dodavatel_ico, count(*) as contracts,
        sum(z.suma) as total_value,
        count(DISTINCT rf.flag_type) as distinct_flags
        FROM zmluvy z
        LEFT JOIN red_flags rf ON rf.zmluva_id = z.id
        WHERE z.dodavatel_ico != '' AND z.suma IS NOT NULL
        GROUP BY z.dodavatel_ico
        ORDER BY total_value DESC LIMIT 10""", "_shape": "array"}, "sql"),

    ("LIKE search (text scan)", "/data/crz.json",
     {"sql": "SELECT count(*) as cnt FROM zmluvy WHERE nazov_zmluvy LIKE '%bezpečnost%' OR popis LIKE '%bezpečnost%'", "_shape": "array"}, "sql"),

    # Dashboard API endpoints
    ("API /api/summary", "/api/summary", {}, "api"),
    ("API /api/summary (filtered)", "/api/summary",
     {"date_from": "2026-01-01", "date_to": "2026-01-31"}, "api"),
    ("API /api/timeline", "/api/timeline", {}, "api"),
    ("API /api/top_contracts", "/api/top_contracts", {}, "api"),
    ("API /api/anomalies", "/api/anomalies", {}, "api"),
    ("API /api/flags", "/api/flags", {}, "api"),
    ("API /api/flags_top", "/api/flags_top", {}, "api"),
    ("API /api/browse (100 rows)", "/api/browse", {"limit": "100"}, "api"),
    ("API /api/browse (sorted)", "/api/browse",
     {"limit": "100", "sort": "suma", "sort_dir": "desc"}, "api"),
    ("API /api/search", "/api/search", {"q": "ministerstvo", "limit": "50"}, "api"),
    ("API /api/detail (contract)", "/api/detail", {"id": "11760561"}, "api"),
    ("API /api/investigation_categories", "/api/investigation_categories", {}, "api"),
]


def timed_fetch(base_url, path, params, timeout=60):
    """Fetch and return (elapsed_ms, success)."""
    start = time.perf_counter()
    try:
        r = httpx.get(f"{base_url}{path}", params=params, timeout=timeout)
        elapsed = (time.perf_counter() - start) * 1000
        return elapsed, r.status_code == 200
    except Exception:
        elapsed = (time.perf_counter() - start) * 1000
        return elapsed, False


def run_benchmark(rounds=3):
    results = []

    # Warmup both servers
    print("Warming up...")
    for url in [SQLITE_URL, DELTA_URL]:
        for _ in range(2):
            httpx.get(f"{url}/data/crz.json",
                      params={"sql": "SELECT 1", "_shape": "array"}, timeout=30)

    for name, path, params, category in BENCHMARKS:
        sqlite_times = []
        delta_times = []

        for _ in range(rounds):
            st, s_ok = timed_fetch(SQLITE_URL, path, params)
            dt, d_ok = timed_fetch(DELTA_URL, path, params)
            if s_ok:
                sqlite_times.append(st)
            if d_ok:
                delta_times.append(dt)

        s_med = statistics.median(sqlite_times) if sqlite_times else float('inf')
        d_med = statistics.median(delta_times) if delta_times else float('inf')

        if s_med > 0 and d_med > 0:
            speedup = s_med / d_med
        else:
            speedup = 0

        results.append({
            "name": name,
            "category": category,
            "sqlite_ms": round(s_med, 1),
            "delta_ms": round(d_med, 1),
            "speedup": round(speedup, 2),
            "sqlite_ok": len(sqlite_times) == rounds,
            "delta_ok": len(delta_times) == rounds,
        })

        winner = "DELTA" if speedup > 1 else "SQLite"
        icon = ">" if speedup > 1.2 else "<" if speedup < 0.8 else "="
        print(f"  {name:45s}  SQLite {s_med:8.1f}ms  Delta {d_med:8.1f}ms  {icon} {speedup:.2f}x  [{winner}]")

    return results


def print_summary(results):
    print("\n" + "=" * 100)
    print(f"{'Benchmark':45s}  {'SQLite':>10s}  {'Delta':>10s}  {'Speedup':>8s}  Winner")
    print("-" * 100)

    for r in results:
        s = f"{r['sqlite_ms']:.0f}ms" if r['sqlite_ok'] else "FAIL"
        d = f"{r['delta_ms']:.0f}ms" if r['delta_ok'] else "FAIL"
        sp = f"{r['speedup']:.2f}x"
        winner = "Delta" if r['speedup'] > 1 else "SQLite"
        marker = "***" if r['speedup'] > 2 or r['speedup'] < 0.5 else ""
        print(f"  {r['name']:45s}  {s:>10s}  {d:>10s}  {sp:>8s}  {winner} {marker}")

    print("-" * 100)

    # Category summaries
    for cat in ["sql", "api"]:
        cat_results = [r for r in results if r["category"] == cat and r["sqlite_ok"] and r["delta_ok"]]
        if cat_results:
            avg_speedup = statistics.mean(r["speedup"] for r in cat_results)
            delta_wins = sum(1 for r in cat_results if r["speedup"] > 1)
            print(f"  {cat.upper():6s} queries: avg speedup {avg_speedup:.2f}x, Delta wins {delta_wins}/{len(cat_results)}")

    all_ok = [r for r in results if r["sqlite_ok"] and r["delta_ok"]]
    if all_ok:
        overall = statistics.mean(r["speedup"] for r in all_ok)
        print(f"\n  Overall avg speedup: {overall:.2f}x ({'Delta faster' if overall > 1 else 'SQLite faster'})")


def main():
    parser = argparse.ArgumentParser(description="Benchmark SQLite vs Delta Lake")
    parser.add_argument("--rounds", type=int, default=3, help="Rounds per benchmark (default: 3)")
    args = parser.parse_args()

    # Check both servers are reachable
    for name, url in [("SQLite", SQLITE_URL), ("Delta", DELTA_URL)]:
        try:
            r = httpx.get(f"{url}/data/crz.json",
                          params={"sql": "SELECT 1", "_shape": "array"}, timeout=5)
            r.raise_for_status()
        except Exception as e:
            print(f"ERROR: {name} server at {url} not reachable: {e}")
            sys.exit(1)

    print(f"Benchmarking {len(BENCHMARKS)} queries, {args.rounds} rounds each\n")
    results = run_benchmark(rounds=args.rounds)
    print_summary(results)


if __name__ == "__main__":
    main()
