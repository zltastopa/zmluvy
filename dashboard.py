"""Interactive CRZ dashboard.

Usage:
    uv run python dashboard.py              # http://localhost:8001
    uv run python dashboard.py --port 9000  # custom port
"""

import argparse
import json
import socket
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from settings import get_path

DB_PATH = get_path("CRZ_DB_PATH", "crz.db")
DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def build_where(params):
    """Build WHERE clause and bindings from query parameters."""
    clauses = []
    bindings = []

    if params.get("date_from"):
        clauses.append("z.datum_zverejnenia >= ?")
        bindings.append(params["date_from"])
    if params.get("date_to"):
        clauses.append("z.datum_zverejnenia <= ?")
        bindings.append(params["date_to"] + " 23:59:59")
    if params.get("suma_min"):
        clauses.append("z.suma >= ?")
        bindings.append(float(params["suma_min"]))
    if params.get("suma_max"):
        clauses.append("z.suma <= ?")
        bindings.append(float(params["suma_max"]))
    if params.get("rezort_id"):
        clauses.append("z.rezort_id = ?")
        bindings.append(params["rezort_id"])
    if params.get("typ"):
        clauses.append("z.typ = ?")
        bindings.append(params["typ"])
    if params.get("stav"):
        clauses.append("z.stav = ?")
        bindings.append(params["stav"])
    if params.get("service_category"):
        clauses.append("e.service_category = ?")
        bindings.append(params["service_category"])

    where = " AND ".join(clauses) if clauses else "1=1"
    return where, bindings


def needs_extraction_join(params):
    return bool(params.get("service_category"))


def api_filters(db):
    """Return available filter values."""
    rezorty = db.execute(
        "SELECT DISTINCT rezort_id, rezort FROM zmluvy WHERE rezort != '' ORDER BY rezort"
    ).fetchall()
    categories = db.execute(
        "SELECT DISTINCT service_category FROM extractions WHERE service_category IS NOT NULL ORDER BY service_category"
    ).fetchall()
    return {
        "rezorty": [{"id": r["rezort_id"], "nazov": r["rezort"]} for r in rezorty],
        "categories": [r["service_category"] for r in categories],
    }


def api_summary(db, params):
    """Aggregate summary stats."""
    where, bindings = build_where(params)
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id" if needs_extraction_join(params) else ""
    row = db.execute(
        f"""SELECT
            count(*) as total,
            count(z.suma) as with_amount,
            coalesce(sum(z.suma), 0) as total_value,
            coalesce(avg(z.suma), 0) as avg_value,
            coalesce(max(z.suma), 0) as max_value,
            coalesce(min(z.suma), 0) as min_value,
            count(CASE WHEN z.typ = 'dodatok' THEN 1 END) as amendments,
            count(CASE WHEN z.stav = 'zrušená' THEN 1 END) as cancelled
        FROM zmluvy z {join}
        WHERE {where}""",
        bindings,
    ).fetchone()
    return dict(row)


def api_timeline(db, params):
    """Monthly contract counts and values."""
    where, bindings = build_where(params)
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id" if needs_extraction_join(params) else ""
    rows = db.execute(
        f"""SELECT
            substr(z.datum_zverejnenia, 1, 7) as month,
            count(*) as count,
            coalesce(sum(z.suma), 0) as total_value,
            coalesce(avg(z.suma), 0) as avg_value
        FROM zmluvy z {join}
        WHERE {where} AND z.datum_zverejnenia != ''
        GROUP BY month
        ORDER BY month""",
        bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_by_rezort(db, params):
    """Breakdown by rezort."""
    where, bindings = build_where(params)
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id" if needs_extraction_join(params) else ""
    rows = db.execute(
        f"""SELECT
            z.rezort as name,
            count(*) as count,
            coalesce(sum(z.suma), 0) as total_value,
            coalesce(avg(z.suma), 0) as avg_value
        FROM zmluvy z {join}
        WHERE {where} AND z.rezort != ''
        GROUP BY z.rezort
        ORDER BY count DESC
        LIMIT 20""",
        bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_by_category(db, params):
    """Breakdown by service category (from extractions)."""
    where, bindings = build_where(params)
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id"
    rows = db.execute(
        f"""SELECT
            e.service_category as category,
            count(*) as count,
            coalesce(sum(z.suma), 0) as total_value,
            coalesce(avg(z.suma), 0) as avg_value
        FROM zmluvy z {join}
        WHERE {where} AND e.service_category IS NOT NULL
        GROUP BY e.service_category
        ORDER BY count DESC""",
        bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_penalties(db, params):
    """Penalty asymmetry distribution."""
    where, bindings = build_where(params)
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id"
    rows = db.execute(
        f"""SELECT
            e.penalty_asymmetry as asymmetry,
            count(*) as count
        FROM zmluvy z {join}
        WHERE {where} AND e.penalty_asymmetry IS NOT NULL
        GROUP BY e.penalty_asymmetry
        ORDER BY count DESC""",
        bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_top_contracts(db, params):
    """Top contracts by amount."""
    where, bindings = build_where(params)
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id" if needs_extraction_join(params) else ""
    rows = db.execute(
        f"""SELECT
            z.id, z.nazov_zmluvy, z.dodavatel, z.objednavatel,
            z.suma, z.suma_celkom, z.datum_zverejnenia, z.rezort,
            z.typ, z.crz_url
        FROM zmluvy z {join}
        WHERE {where} AND z.suma IS NOT NULL
        ORDER BY z.suma DESC
        LIMIT 25""",
        bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_anomalies(db, params):
    """Detect data anomalies in the filtered set."""
    where, bindings = build_where(params)
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id" if needs_extraction_join(params) else ""

    anomalies = []

    # Contracts with no amount
    row = db.execute(
        f"SELECT count(*) as cnt FROM zmluvy z {join} WHERE {where} AND z.suma IS NULL",
        bindings,
    ).fetchone()
    if row["cnt"] > 0:
        anomalies.append({
            "type": "missing_amount",
            "label": "Zmluvy bez uvedenej sumy",
            "count": row["cnt"],
            "severity": "info",
        })

    # Very high value contracts (>1M EUR)
    row = db.execute(
        f"SELECT count(*) as cnt FROM zmluvy z {join} WHERE {where} AND z.suma > 1000000",
        bindings,
    ).fetchone()
    if row["cnt"] > 0:
        anomalies.append({
            "type": "high_value",
            "label": "Zmluvy nad 1 mil. EUR",
            "count": row["cnt"],
            "severity": "warning",
        })

    # Missing supplier ICO
    row = db.execute(
        f"SELECT count(*) as cnt FROM zmluvy z {join} WHERE {where} AND (z.dodavatel_ico = '' OR z.dodavatel_ico IS NULL)",
        bindings,
    ).fetchone()
    if row["cnt"] > 0:
        anomalies.append({
            "type": "missing_ico",
            "label": "Dodavatel bez ICO",
            "count": row["cnt"],
            "severity": "info",
        })

    # Cancelled contracts
    row = db.execute(
        f"SELECT count(*) as cnt FROM zmluvy z {join} WHERE {where} AND z.stav = 'zrušená'",
        bindings,
    ).fetchone()
    if row["cnt"] > 0:
        anomalies.append({
            "type": "cancelled",
            "label": "Zrusene zmluvy",
            "count": row["cnt"],
            "severity": "warning",
        })

    # Supplier advantage in penalties (rare, potentially suspicious)
    row = db.execute(
        f"""SELECT count(*) as cnt FROM zmluvy z
            LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE {where} AND e.penalty_asymmetry = 'supplier_advantage'""",
        bindings,
    ).fetchone()
    if row["cnt"] > 0:
        anomalies.append({
            "type": "supplier_advantage",
            "label": "Pokuty zvyhodnujuce dodavatela (neobvykle)",
            "count": row["cnt"],
            "severity": "warning",
        })

    # Bezodplatne (gratuitous) contracts
    row = db.execute(
        f"""SELECT count(*) as cnt FROM zmluvy z
            LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE {where} AND e.bezodplatne = 1""",
        bindings,
    ).fetchone()
    if row["cnt"] > 0:
        anomalies.append({
            "type": "bezodplatne",
            "label": "Bezodplatne zmluvy",
            "count": row["cnt"],
            "severity": "info",
        })

    # Amount distribution stats for histogram
    rows = db.execute(
        f"""SELECT
            CASE
                WHEN z.suma < 1000 THEN '< 1 tis.'
                WHEN z.suma < 10000 THEN '1-10 tis.'
                WHEN z.suma < 100000 THEN '10-100 tis.'
                WHEN z.suma < 1000000 THEN '100 tis.-1 mil.'
                ELSE '> 1 mil.'
            END as bucket,
            count(*) as count
        FROM zmluvy z {join}
        WHERE {where} AND z.suma IS NOT NULL
        GROUP BY bucket
        ORDER BY min(z.suma)""",
        bindings,
    ).fetchall()
    amount_distribution = [dict(r) for r in rows]

    return {"anomalies": anomalies, "amount_distribution": amount_distribution}


ROUTES = {
    "/api/filters": lambda db, p: api_filters(db),
    "/api/summary": api_summary,
    "/api/timeline": api_timeline,
    "/api/by_rezort": api_by_rezort,
    "/api/by_category": api_by_category,
    "/api/penalties": api_penalties,
    "/api/top_contracts": api_top_contracts,
    "/api/anomalies": api_anomalies,
}


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/dashboard":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.read_bytes())
            return

        if path in ROUTES:
            qs = parse_qs(parsed.query)
            params = {k: v[0] for k, v in qs.items()}
            db = get_db()
            try:
                handler = ROUTES[path]
                result = handler(db, params)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
            finally:
                db.close()
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet


def main():
    parser = argparse.ArgumentParser(description="CRZ Dashboard")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    class ReusableHTTPServer(HTTPServer):
        allow_reuse_address = True
        allow_reuse_port = True

    server = ReusableHTTPServer(("0.0.0.0", args.port), DashboardHandler)
    print(f"CRZ Dashboard: http://localhost:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
