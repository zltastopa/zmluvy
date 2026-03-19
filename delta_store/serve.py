"""CRZ server backed by Delta Lake + DuckDB.

Parallel alternative to server/serve.py (SQLite + Datasette).
Provides the same API endpoints + dashboard + a Datasette-compatible SQL API.

Usage:
    uv run python delta_store/serve.py                   # http://localhost:8002
    uv run python delta_store/serve.py --port 9000
    uv run python delta_store/serve.py --tables delta_store/tables
"""

import argparse
import csv
import io
import json
import re
import threading
from pathlib import Path

import duckdb
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.staticfiles import StaticFiles

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from settings import normalize_company_name

TABLES_DIR = Path(__file__).parent / "tables"
DASHBOARD_HTML_PATH = REPO_ROOT / "frontend" / "dashboard.html"
DETAIL_HTML_PATH = REPO_ROOT / "frontend" / "detail.html"
ASSETS_DIR = REPO_ROOT / "assets"

app = FastAPI(title="CRZ Delta Lake Server")

# Mount static assets
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# ---------------------------------------------------------------------------
# DuckDB connection — registers Delta tables as views
# ---------------------------------------------------------------------------

_conn = None
_db_lock = threading.Lock()


def get_db() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        _conn = duckdb.connect()
        _conn.execute("INSTALL delta; LOAD delta;")
        # Materialize Delta tables into DuckDB native tables.
        # This avoids delta_scan serialization limitations in complex CTEs
        # while keeping Parquet/Delta as the source of truth on disk.
        tables_dir = TABLES_DIR
        for table_path in sorted(tables_dir.iterdir()):
            if table_path.is_dir() and (table_path / "_delta_log").exists():
                name = table_path.name
                if name == "ruz_entities":
                    continue  # handled separately below
                _conn.execute(
                    f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM delta_scan('{table_path}')"
                )
        # RUZ optimization: materialize only CRZ-connected entities (slim columns)
        # Full table has ~1.8M rows but only ~31k appear in CRZ contracts.
        ruz_path = tables_dir / "ruz_entities"
        if ruz_path.is_dir() and (ruz_path / "_delta_log").exists():
            _conn.execute(f"""
                CREATE OR REPLACE TABLE ruz_entities AS
                SELECT cin, name, terminated_on, established_on,
                       organization_size_id, organization_size,
                       legal_form_id, legal_form,
                       region, nace_code, nace_category
                FROM delta_scan('{ruz_path}')
                WHERE cin IN (
                    SELECT DISTINCT dodavatel_ico FROM zmluvy
                    WHERE dodavatel_ico IS NOT NULL
                    UNION
                    SELECT DISTINCT objednavatel_ico FROM zmluvy
                    WHERE objednavatel_ico IS NOT NULL
                )
            """)
            # Full view for detail page and SQL API (reads Parquet on demand)
            _conn.execute(
                f"CREATE OR REPLACE VIEW ruz_entities_full AS SELECT * FROM delta_scan('{ruz_path}')"
            )
        # Create FTS index on zmluvy
        try:
            _conn.execute("INSTALL fts; LOAD fts;")
            _conn.execute("""
                PRAGMA create_fts_index('zmluvy', 'id',
                    'nazov_zmluvy', 'dodavatel', 'objednavatel',
                    'poznamka', 'popis', 'dodavatel_adresa',
                    overwrite=1
                )
            """)
        except Exception:
            pass  # FTS creation may fail if zmluvy not loaded yet
    return _conn


def q(sql: str, params=None) -> list[dict]:
    """Execute SQL and return list of dicts."""
    with _db_lock:
        db = get_db()
        if params:
            result = db.execute(sql, params)
        else:
            result = db.execute(sql)
        cols = [desc[0] for desc in result.description]
        return [dict(zip(cols, row)) for row in result.fetchall()]


def q1(sql: str, params=None) -> dict | None:
    """Execute SQL and return single row as dict, or None."""
    rows = q(sql, params)
    return rows[0] if rows else None


def qval(sql: str, params=None):
    """Execute SQL and return single scalar value."""
    with _db_lock:
        db = get_db()
        if params:
            result = db.execute(sql, params)
        else:
            result = db.execute(sql)
        row = result.fetchone()
        return row[0] if row else None


# ---------------------------------------------------------------------------
# Filter helpers — DuckDB uses $1, $2 positional params
# ---------------------------------------------------------------------------

def build_where(params: dict) -> tuple[str, list]:
    clauses, bindings = [], []

    def add(clause, val):
        bindings.append(val)
        clauses.append(clause.replace("?", f"${len(bindings)}"))

    if params.get("date_from"):
        add("z.datum_zverejnenia >= ?", params["date_from"])
    if params.get("date_to"):
        add("z.datum_zverejnenia <= ?", params["date_to"] + " 23:59:59")
    if params.get("suma_min"):
        add("z.suma >= ?", float(params["suma_min"]))
    if params.get("suma_max"):
        add("z.suma <= ?", float(params["suma_max"]))
    if params.get("rezort_id"):
        add("z.rezort_id = ?", params["rezort_id"])
    if params.get("typ"):
        add("z.typ = ?", params["typ"])
    if params.get("stav"):
        add("z.stav = ?", params["stav"])
    if params.get("service_category"):
        add("e.service_category = ?", params["service_category"])
    if params.get("suma_null") == "1":
        clauses.append("z.suma IS NULL")
    if params.get("suma_gt"):
        add("z.suma > ?", float(params["suma_gt"]))
    if params.get("ico_missing") == "1":
        clauses.append("(z.dodavatel_ico = '' OR z.dodavatel_ico IS NULL)")
    if params.get("penalty_asymmetry"):
        add("e.penalty_asymmetry = ?", params["penalty_asymmetry"])
    if params.get("bezodplatne") == "1":
        clauses.append("e.bezodplatne = 1")
    if params.get("flag"):
        add("z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = ?)", params["flag"])
    return " AND ".join(clauses) if clauses else "1=1", bindings


EJOIN = "LEFT JOIN extractions e ON e.zmluva_id = z.id"


def _join(params, extraction=False):
    need = extraction or params.get("service_category") or params.get(
        "penalty_asymmetry") or params.get("bezodplatne")
    return EJOIN if need else ""


def _sql(template: str, bindings: list) -> str:
    """Replace $N placeholders with actual values for DuckDB.

    DuckDB's Python API supports positional params natively,
    so we just return the template as-is and pass bindings separately.
    """
    return template


# ---------------------------------------------------------------------------
# Dashboard API endpoints
# ---------------------------------------------------------------------------

@app.get("/api/filters")
def api_filters(request: Request):
    params = dict(request.query_params)
    rezorty = q("SELECT DISTINCT rezort_id, rezort FROM zmluvy WHERE rezort != '' ORDER BY rezort")
    categories = q("SELECT DISTINCT service_category FROM extractions WHERE service_category IS NOT NULL ORDER BY service_category")
    return {
        "rezorty": [{"id": r["rezort_id"], "nazov": r["rezort"]} for r in rezorty],
        "categories": [r["service_category"] for r in categories],
    }


@app.get("/api/summary")
def api_summary(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    j = _join(params)
    row = q1(
        f"""SELECT count(*) as total, count(z.suma) as with_amount,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value,
            coalesce(max(z.suma),0) as max_value, coalesce(min(z.suma),0) as min_value,
            count(CASE WHEN z.typ='dodatok' THEN 1 END) as amendments,
            count(CASE WHEN z.stav='zrušená' THEN 1 END) as cancelled
        FROM zmluvy z {j} WHERE {where}""", bindings)

    debt_flags = ('vszp_debtor', 'socpoist_debtor', 'tax_unreliable')
    # debt_flags go first as $1,$2,$3 — renumber where clause params
    placeholders = ','.join(f'${i + 1}' for i in range(len(debt_flags)))
    where_renumbered = where
    for i in range(len(bindings), 0, -1):
        where_renumbered = where_renumbered.replace(f"${i}", f"${i + len(debt_flags)}")
    debt_row = q1(
        f"""SELECT count(DISTINCT rf.zmluva_id) as debtor_contracts,
            coalesce(sum(DISTINCT z.suma), 0) as debtor_value
        FROM red_flags rf
        JOIN zmluvy z ON z.id = rf.zmluva_id
        {j}
        WHERE rf.flag_type IN ({placeholders}) AND ({where_renumbered})""",
        list(debt_flags) + list(bindings),
    )
    result = row or {}
    result["debtor_contracts"] = debt_row["debtor_contracts"] if debt_row else 0
    result["debtor_value"] = debt_row["debtor_value"] if debt_row else 0
    return result


@app.get("/api/timeline")
def api_timeline(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    return q(
        f"""SELECT substr(z.datum_zverejnenia,1,7) as month, count(*) as count,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value
        FROM zmluvy z {_join(params)} WHERE {where} AND z.datum_zverejnenia!=''
        GROUP BY month ORDER BY month""", bindings)


@app.get("/api/by_rezort")
def api_by_rezort(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    return q(
        f"""SELECT z.rezort as name, count(*) as count,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value
        FROM zmluvy z {_join(params)} WHERE {where} AND z.rezort!=''
        GROUP BY z.rezort ORDER BY count DESC LIMIT 20""", bindings)


@app.get("/api/by_category")
def api_by_category(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    return q(
        f"""SELECT e.service_category as category, count(*) as count,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value
        FROM zmluvy z {EJOIN} WHERE {where} AND e.service_category IS NOT NULL
        GROUP BY e.service_category ORDER BY count DESC""", bindings)


@app.get("/api/penalties")
def api_penalties(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    return q(
        f"""SELECT e.penalty_asymmetry as asymmetry, count(*) as count
        FROM zmluvy z {EJOIN} WHERE {where} AND e.penalty_asymmetry IS NOT NULL
        GROUP BY e.penalty_asymmetry ORDER BY count DESC""", bindings)


@app.get("/api/top_contracts")
def api_top_contracts(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    return q(
        f"""SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
            z.objednavatel, z.objednavatel_ico,
            z.suma, z.suma_celkom, z.datum_zverejnenia, z.rezort, z.rezort_id,
            z.typ, z.crz_url, e.actual_subject
        FROM zmluvy z {_join(params, extraction=True)} WHERE {where} AND z.suma IS NOT NULL
        ORDER BY z.suma DESC LIMIT 25""", bindings)


@app.get("/api/anomalies")
def api_anomalies(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    j = _join(params)
    anomalies = []

    for sql_tpl, atype, label, severity in [
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {{where}} AND z.suma IS NULL",
         "missing_amount", "Zmluvy bez uvedenej sumy", "info"),
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {{where}} AND z.suma > 1000000",
         "high_value", "Zmluvy nad 1 mil. EUR", "warning"),
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {{where}} AND (z.dodavatel_ico='' OR z.dodavatel_ico IS NULL)",
         "missing_ico", "Dodavatel bez ICO", "info"),
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {{where}} AND z.stav='zrušená'",
         "cancelled", "Zrusene zmluvy", "warning"),
    ]:
        cnt = qval(sql_tpl.format(where=where), bindings)
        if cnt and cnt > 0:
            anomalies.append({"type": atype, "label": label, "count": cnt, "severity": severity})

    for sql_tpl, atype, label, severity in [
        (f"SELECT count(*) FROM zmluvy z {EJOIN} WHERE {{where}} AND e.penalty_asymmetry='supplier_advantage'",
         "supplier_advantage", "Pokuty zvyhodnujuce dodavatela (neobvykle)", "warning"),
        (f"SELECT count(*) FROM zmluvy z {EJOIN} WHERE {{where}} AND e.bezodplatne=1",
         "bezodplatne", "Bezodplatne zmluvy", "info"),
    ]:
        cnt = qval(sql_tpl.format(where=where), bindings)
        if cnt and cnt > 0:
            anomalies.append({"type": atype, "label": label, "count": cnt, "severity": severity})

    rows = q(
        f"""SELECT
            CASE WHEN z.suma<1000 THEN '< 1 tis.'
                 WHEN z.suma<10000 THEN '1-10 tis.'
                 WHEN z.suma<100000 THEN '10-100 tis.'
                 WHEN z.suma<1000000 THEN '100 tis.-1 mil.'
                 ELSE '> 1 mil.' END as bucket, count(*) as count
        FROM zmluvy z {j} WHERE {where} AND z.suma IS NOT NULL
        GROUP BY bucket ORDER BY min(z.suma)""", bindings)

    return {"anomalies": anomalies, "amount_distribution": rows}


@app.get("/api/detail")
def api_detail(request: Request):
    params = dict(request.query_params)

    if params.get("id"):
        cid = int(params["id"])
        row = q1("SELECT * FROM zmluvy WHERE id = $1", [cid])
        if not row:
            return {"error": "not_found"}
        contract = row

        ext = q1("SELECT * FROM extractions WHERE zmluva_id = $1", [cid])
        contract["extraction"] = ext

        contract["prilohy"] = q("SELECT * FROM prilohy WHERE zmluva_id = $1", [cid])

        contract["related_supplier_contracts"] = q(
            """SELECT z.id, z.nazov_zmluvy, z.suma, z.datum_zverejnenia, z.typ, e.actual_subject
            FROM zmluvy z LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE z.dodavatel_ico = $1 AND z.dodavatel_ico != '' AND z.id != $2
            ORDER BY z.datum_zverejnenia DESC LIMIT 10""",
            [contract["dodavatel_ico"], cid])

        stats = q1(
            """SELECT count(*) as total_count, coalesce(sum(suma), 0) as total_sum
            FROM zmluvy WHERE dodavatel_ico = $1 AND dodavatel_ico != ''""",
            [contract["dodavatel_ico"]])
        contract["supplier_total_count"] = stats["total_count"] if stats else 0
        contract["supplier_total_sum"] = stats["total_sum"] if stats else 0

        contract["red_flags"] = q(
            """SELECT rf.flag_type, fr.label, fr.severity, fr.description, rf.detail
            FROM red_flags rf JOIN flag_rules fr ON fr.id = rf.flag_type
            WHERE rf.zmluva_id = $1 ORDER BY fr.severity DESC""", [cid])

        for ico_col, key in [("dodavatel_ico", "dodavatel_tax_status"),
                             ("objednavatel_ico", "objednavatel_tax_status")]:
            ico_val = contract.get(ico_col)
            if ico_val:
                tr = q1("SELECT status FROM tax_reliability WHERE ico = $1", [ico_val])
                contract[key] = tr["status"] if tr else None
            else:
                contract[key] = None

        ico_val = contract.get("dodavatel_ico")
        if ico_val:
            vszp = q1(
                "SELECT name, amount, payer_type FROM vszp_debtors WHERE cin = $1 ORDER BY amount DESC LIMIT 1",
                [ico_val])
            contract["dodavatel_vszp_debt"] = vszp
        else:
            contract["dodavatel_vszp_debt"] = None

        dodavatel = contract.get("dodavatel") or ""
        if dodavatel:
            norm_name = normalize_company_name(dodavatel)
            socpoist = q1(
                "SELECT name, amount FROM socpoist_debtors WHERE name_normalized = $1 ORDER BY amount DESC LIMIT 1",
                [norm_name])
            contract["dodavatel_socpoist_debt"] = socpoist
        else:
            contract["dodavatel_socpoist_debt"] = None

        if ico_val:
            ruz = q1(
                """SELECT name, city, street, region, district, established_on, terminated_on,
                    legal_form, nace_category, nace_code, organization_size, ownership_type
                FROM ruz_entities_full WHERE cin = $1 LIMIT 1""", [ico_val])
            contract["dodavatel_ruz"] = ruz
        else:
            contract["dodavatel_ruz"] = None

        return {"kind": "contract", "data": contract}

    # Supplier or buyer detail
    for role, ico_col, other_col, other_ico_col in [
        ("dodavatel", "dodavatel_ico", "objednavatel", "objednavatel_ico"),
        ("objednavatel", "objednavatel_ico", "dodavatel", "dodavatel_ico"),
    ]:
        ico = params.get(ico_col)
        if not ico:
            continue
        contracts = q(
            f"""SELECT id, nazov_zmluvy, dodavatel, objednavatel, suma, suma_celkom,
                datum_zverejnenia, rezort, typ, stav, crz_url
            FROM zmluvy WHERE {ico_col} = $1
            ORDER BY datum_zverejnenia DESC""", [ico])
        if not contracts:
            return {"error": "not_found"}

        stats = q1(
            f"""SELECT count(*) as total, coalesce(sum(suma),0) as total_value,
                coalesce(avg(suma),0) as avg_value, count(suma) as with_amount,
                min(datum_zverejnenia) as first_contract, max(datum_zverejnenia) as last_contract,
                count(DISTINCT {other_ico_col}) as unique_counterparties
            FROM zmluvy WHERE {ico_col} = $1""", [ico])

        top_counterparties = q(
            f"""SELECT {other_col} as name, {other_ico_col} as ico, count(*) as count,
                coalesce(sum(suma),0) as total_value
            FROM zmluvy WHERE {ico_col} = $1 AND {other_col} != ''
            GROUP BY {other_ico_col} ORDER BY count DESC LIMIT 10""", [ico])

        return {
            "kind": role,
            "ico": ico,
            "name": contracts[0][role],
            "stats": stats,
            "top_counterparties": top_counterparties,
            "contracts": contracts[:50],
        }

    if params.get("rezort_id"):
        rid = params["rezort_id"]
        contracts = q(
            """SELECT id, nazov_zmluvy, dodavatel, objednavatel, suma, suma_celkom,
                datum_zverejnenia, typ, stav, crz_url
            FROM zmluvy WHERE rezort_id = $1
            ORDER BY datum_zverejnenia DESC""", [rid])

        stats = q1(
            """SELECT count(*) as total, coalesce(sum(suma),0) as total_value,
                coalesce(avg(suma),0) as avg_value, count(suma) as with_amount,
                min(datum_zverejnenia) as first_contract, max(datum_zverejnenia) as last_contract,
                count(DISTINCT dodavatel_ico) as unique_suppliers,
                count(DISTINCT objednavatel_ico) as unique_buyers
            FROM zmluvy WHERE rezort_id = $1""", [rid])

        rezort_name = q1("SELECT nazov FROM rezorty WHERE id = $1", [rid])

        top_suppliers = q(
            """SELECT dodavatel, dodavatel_ico, count(*) as count,
                coalesce(sum(suma),0) as total_value
            FROM zmluvy WHERE rezort_id = $1 AND dodavatel != ''
            GROUP BY dodavatel_ico ORDER BY total_value DESC LIMIT 10""", [rid])

        categories = q(
            """SELECT e.service_category as category, count(*) as count
            FROM zmluvy z LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE z.rezort_id = $1 AND e.service_category IS NOT NULL
            GROUP BY e.service_category ORDER BY count DESC LIMIT 10""", [rid])

        return {
            "kind": "rezort",
            "rezort_id": rid,
            "name": rezort_name["nazov"] if rezort_name else rid,
            "stats": stats,
            "top_suppliers": top_suppliers,
            "categories": categories,
            "contracts": contracts[:50],
        }

    return {"error": "missing_param"}


@app.get("/api/flags")
def api_flags(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    j = _join(params, extraction=True)

    rules = q(
        f"""SELECT fr.id, fr.label, fr.severity, fr.description, count(rf.id) as count
        FROM flag_rules fr
        LEFT JOIN red_flags rf ON rf.flag_type = fr.id
        LEFT JOIN zmluvy z ON z.id = rf.zmluva_id
        {j}
        WHERE fr.enabled = 1 AND ({where} OR rf.id IS NULL)
        GROUP BY fr.id, fr.label, fr.severity, fr.description
        ORDER BY count DESC""", bindings)

    total = q1(
        f"""SELECT count(DISTINCT rf.zmluva_id) as total
        FROM red_flags rf
        JOIN zmluvy z ON z.id = rf.zmluva_id
        {j}
        WHERE {where}""", bindings)

    return {
        "rules": rules,
        "total_flagged": total["total"] if total else 0,
    }


@app.get("/api/flags_by_rezort")
def api_flags_by_rezort(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    flag_type = params.get("flag_type")
    flag_clause = ""
    if flag_type:
        bindings = [flag_type] + bindings
        flag_clause = "AND rf.flag_type = $1"
        # Renumber the where clause params
        where_renumbered = where
        for i in range(len(bindings) - 1, 0, -1):
            where_renumbered = where_renumbered.replace(f"${i}", f"${i + 1}")
        where = where_renumbered

    return q(
        f"""SELECT z.rezort as name, z.rezort_id,
            count(DISTINCT rf.zmluva_id) as flagged,
            count(DISTINCT z.id) as total
        FROM zmluvy z
        LEFT JOIN red_flags rf ON rf.zmluva_id = z.id {flag_clause}
        {_join(params)}
        WHERE {where} AND z.rezort != ''
        GROUP BY z.rezort_id, z.rezort
        HAVING count(DISTINCT rf.zmluva_id) > 0
        ORDER BY flagged DESC
        LIMIT 20""", bindings)


@app.get("/api/flags_top")
def api_flags_top(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    return q(
        f"""SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
            z.objednavatel, z.objednavatel_ico, z.suma,
            z.datum_zverejnenia, z.rezort, z.rezort_id, z.crz_url,
            count(rf.id) as flag_count,
            string_agg(fr.label, ', ') as flag_labels
        FROM red_flags rf
        JOIN zmluvy z ON z.id = rf.zmluva_id
        JOIN flag_rules fr ON fr.id = rf.flag_type
        {_join(params)}
        WHERE {where}
        GROUP BY z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
            z.objednavatel, z.objednavatel_ico, z.suma,
            z.datum_zverejnenia, z.rezort, z.rezort_id, z.crz_url
        ORDER BY flag_count DESC, z.suma DESC
        LIMIT 50""", bindings)


@app.get("/api/flags_timeline")
def api_flags_timeline(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    flag_type = params.get("flag_type")
    flag_clause = ""
    if flag_type:
        bindings = [flag_type] + bindings
        flag_clause = "AND rf.flag_type = $1"
        where_renumbered = where
        for i in range(len(bindings) - 1, 0, -1):
            where_renumbered = where_renumbered.replace(f"${i}", f"${i + 1}")
        where = where_renumbered

    return q(
        f"""SELECT substr(z.datum_zverejnenia, 1, 7) as month,
            count(DISTINCT rf.zmluva_id) as flagged,
            count(DISTINCT z.id) as total
        FROM zmluvy z
        LEFT JOIN red_flags rf ON rf.zmluva_id = z.id {flag_clause}
        {_join(params)}
        WHERE {where} AND z.datum_zverejnenia != ''
        GROUP BY month
        ORDER BY month""", bindings)


@app.get("/api/investigation_categories")
def api_investigation_categories(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    base_cte = f"WITH base AS (SELECT DISTINCT z.id FROM zmluvy z {EJOIN} WHERE {where})"

    def q_count(sql):
        return qval(base_cte + " " + sql, bindings) or 0

    def q_rows(sql):
        return q(base_cte + " " + sql, bindings)

    categories = []

    # 1) Date anomalies — DuckDB uses TRY_CAST and date functions differently
    date_condition = """
        z.datum_ucinnosti = '0000-00-00'
        OR TRY_CAST(substr(z.datum_podpisu, 1, 4) AS INTEGER) < 1990
        OR TRY_CAST(substr(z.datum_podpisu, 1, 4) AS INTEGER) > 2030
        OR TRY_CAST(substr(z.datum_ucinnosti, 1, 4) AS INTEGER) > 2030
        OR (
            TRY_CAST(z.datum_podpisu AS DATE) IS NOT NULL
            AND TRY_CAST(z.datum_zverejnenia AS DATE) IS NOT NULL
            AND (TRY_CAST(z.datum_podpisu AS DATE) - TRY_CAST(z.datum_zverejnenia AS DATE)) > 30
        )
        OR (
            TRY_CAST(z.datum_ucinnosti AS DATE) IS NOT NULL
            AND TRY_CAST(z.datum_zverejnenia AS DATE) IS NOT NULL
            AND (TRY_CAST(z.datum_ucinnosti AS DATE) - TRY_CAST(z.datum_zverejnenia AS DATE)) < 0
        )
    """
    categories.append({
        "id": "impossible_dates",
        "title": "Date anomalies",
        "description": "Suspicious signature/effect dates, impossible years, or timeline inconsistencies.",
        "severity": "danger",
        "count": q_count(f"SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id WHERE {date_condition}"),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma,
                z.nazov_zmluvy, z.datum_podpisu, z.datum_ucinnosti
            FROM zmluvy z JOIN base b ON b.id = z.id
            WHERE {date_condition}
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC
            LIMIT 8"""),
    })

    # 2) Hidden price but grant amount
    hidden_grant_condition = "z.suma IS NULL AND e.grant_amount IS NOT NULL AND trim(e.grant_amount) != ''"
    categories.append({
        "id": "hidden_price_grants",
        "title": "Hidden price with grant amount",
        "description": "No sum in CRZ amount fields, but extracted text includes grant amount.",
        "severity": "danger",
        "count": q_count(
            f"""SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id WHERE {hidden_grant_condition}"""),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy,
                e.grant_amount, e.funding_type
            FROM zmluvy z JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id
            WHERE {hidden_grant_condition}
            ORDER BY z.datum_zverejnenia DESC LIMIT 8"""),
    })

    # 3) Generic titles
    generic_condition = """
        lower(trim(z.nazov_zmluvy)) IN (
            'zmluva o dielo', 'rámcová zmluva', 'zmluva o spolupráci',
            'zmluva o poskytovaní služieb', 'kúpna zmluva',
            'darovacia zmluva', 'nájomná zmluva'
        )
    """
    categories.append({
        "id": "generic_titles",
        "title": "Generic contract titles",
        "description": "Broad titles that hide the real purpose of a contract.",
        "severity": "warning",
        "count": q_count(f"SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id WHERE {generic_condition}"),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy
            FROM zmluvy z JOIN base b ON b.id = z.id WHERE {generic_condition}
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC LIMIT 8"""),
    })

    # 4) Off-hours high-value — DuckDB: extract hour
    offhours_condition = """
        CAST(strftime(TRY_CAST(z.datum_zverejnenia AS TIMESTAMP), '%H') AS INTEGER) IN (0, 1, 2, 3, 4, 5, 22, 23)
        AND COALESCE(z.suma, 0) >= 100000
    """
    categories.append({
        "id": "offhours_high_value",
        "title": "Off-hours high-value publications",
        "description": "High-value contracts published late at night or very early morning.",
        "severity": "warning",
        "count": q_count(f"SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id WHERE {offhours_condition}"),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy
            FROM zmluvy z JOIN base b ON b.id = z.id WHERE {offhours_condition}
            ORDER BY z.suma DESC LIMIT 8"""),
    })

    # 5) Supplier-advantage penalties
    categories.append({
        "id": "supplier_advantage_penalties",
        "title": "Supplier-advantage penalties",
        "description": "Extracted penalty clauses indicate supplier-side advantage.",
        "severity": "danger",
        "count": q_count(
            """SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.penalty_asymmetry = 'supplier_advantage'"""),
        "sample": q_rows(
            """SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy,
                e.penalty_count, e.service_category
            FROM zmluvy z JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.penalty_asymmetry = 'supplier_advantage'
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC LIMIT 8"""),
    })

    # 6) Mirror postings
    mirror_cte = f"""WITH base AS (SELECT DISTINCT z.id FROM zmluvy z {EJOIN} WHERE {where}),
        contracts AS (
            SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy,
                TRY_CAST(z.datum_zverejnenia AS DATE) AS d,
                round(z.suma, 2) AS amt,
                lower(trim(z.objednavatel)) AS buyer_key,
                lower(trim(z.dodavatel)) AS supplier_key,
                CASE WHEN lower(trim(z.objednavatel)) <= lower(trim(z.dodavatel))
                     THEN lower(trim(z.objednavatel)) ELSE lower(trim(z.dodavatel)) END AS p1,
                CASE WHEN lower(trim(z.objednavatel)) <= lower(trim(z.dodavatel))
                     THEN lower(trim(z.dodavatel)) ELSE lower(trim(z.objednavatel)) END AS p2
            FROM zmluvy z JOIN base b ON b.id = z.id
            WHERE z.suma IS NOT NULL AND trim(z.objednavatel) != '' AND trim(z.dodavatel) != ''
        ),
        mirror_groups AS (
            SELECT d, amt, p1, p2, count(*) AS n,
                SUM(CASE WHEN buyer_key < supplier_key THEN 1 ELSE 0 END) AS dir_ab,
                SUM(CASE WHEN buyer_key > supplier_key THEN 1 ELSE 0 END) AS dir_ba
            FROM contracts GROUP BY d, amt, p1, p2
            HAVING dir_ab > 0 AND dir_ba > 0
        )"""
    mirror_count = qval(mirror_cte + " SELECT COALESCE(SUM(n), 0) FROM mirror_groups", bindings) or 0
    mirror_rows = q(
        mirror_cte + """
        SELECT c.id, NULL AS pair_id, c.datum_zverejnenia, c.objednavatel, c.dodavatel, c.suma, c.nazov_zmluvy
        FROM contracts c
        JOIN mirror_groups g ON c.d = g.d AND c.amt = g.amt AND c.p1 = g.p1 AND c.p2 = g.p2
        ORDER BY c.suma DESC, c.datum_zverejnenia DESC LIMIT 8""", bindings)
    categories.append({
        "id": "mirror_postings",
        "title": "Mirrored bilateral postings",
        "description": "Same-day, same-amount records where buyer/supplier are swapped.",
        "severity": "warning",
        "count": mirror_count,
        "sample": mirror_rows,
    })

    # 7) Identity quality — DuckDB uses regexp_matches instead of GLOB
    ico_quality_condition = """
        (z.dodavatel_ico IS NULL OR trim(z.dodavatel_ico) = '' OR NOT regexp_matches(z.dodavatel_ico, '^[0-9]{8}$'))
        OR
        (z.objednavatel_ico IS NULL OR trim(z.objednavatel_ico) = '' OR NOT regexp_matches(z.objednavatel_ico, '^[0-9]{8}$'))
    """
    categories.append({
        "id": "identity_quality",
        "title": "Identity quality issues",
        "description": "Missing or malformed ICO values that can obscure entity-level analysis.",
        "severity": "warning",
        "count": q_count(f"SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id WHERE {ico_quality_condition}"),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.objednavatel_ico,
                z.dodavatel, z.dodavatel_ico, z.suma, z.nazov_zmluvy
            FROM zmluvy z JOIN base b ON b.id = z.id WHERE {ico_quality_condition}
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC LIMIT 8"""),
    })

    # 8) Amount fingerprints
    amount_pattern_condition = "ROUND(z.suma, 2) IN (10759.80, 5379.88, 5379.90)"
    categories.append({
        "id": "amount_fingerprints",
        "title": "Repeated amount fingerprints",
        "description": "Recurring exact amounts often tied to template-based funding flows.",
        "severity": "info",
        "count": q_count(
            f"SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id WHERE z.suma IS NOT NULL AND {amount_pattern_condition}"),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy
            FROM zmluvy z JOIN base b ON b.id = z.id
            WHERE z.suma IS NOT NULL AND {amount_pattern_condition}
            ORDER BY z.datum_zverejnenia DESC LIMIT 8"""),
    })

    # 9) UVO traceability gap
    uvo_gap_condition = """
        COALESCE(z.suma, 0) >= 100000
        AND (z.uvo_url IS NULL OR trim(z.uvo_url) = '' OR lower(trim(z.uvo_url)) NOT LIKE 'http%')
    """
    categories.append({
        "id": "uvo_traceability_gap",
        "title": "High-value UVO traceability gap",
        "description": "High-value contracts with missing or non-link procurement references.",
        "severity": "danger",
        "count": q_count(f"SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id WHERE {uvo_gap_condition}"),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.uvo_url, z.nazov_zmluvy
            FROM zmluvy z JOIN base b ON b.id = z.id WHERE {uvo_gap_condition}
            ORDER BY z.suma DESC LIMIT 8"""),
    })

    # 10) Extraction blind spots
    categories.append({
        "id": "extraction_blind_spot",
        "title": "Extraction blind spots",
        "description": "Contracts with no extraction enrichment available.",
        "severity": "warning",
        "count": q_count(
            """SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id
            LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.zmluva_id IS NULL"""),
        "sample": q_rows(
            """SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy
            FROM zmluvy z JOIN base b ON b.id = z.id
            LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.zmluva_id IS NULL
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC LIMIT 8"""),
    })

    return {"categories": categories}


@app.get("/api/contracts")
def api_contracts(request: Request):
    params = dict(request.query_params)
    where, bindings = build_where(params)
    j = _join(params)
    return q(
        f"""SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
            z.objednavatel, z.objednavatel_ico,
            z.suma, z.suma_celkom, z.datum_zverejnenia, z.rezort, z.rezort_id,
            z.typ, z.stav, z.crz_url
        FROM zmluvy z {j} WHERE {where}
        ORDER BY z.datum_zverejnenia DESC LIMIT 200""", bindings)


# ---------------------------------------------------------------------------
# Browse API
# ---------------------------------------------------------------------------

_BROWSE_SORT_COLS = {
    'id', 'nazov_zmluvy', 'cislo_zmluvy', 'dodavatel', 'dodavatel_ico',
    'objednavatel', 'objednavatel_ico', 'suma', 'suma_celkom',
    'datum_zverejnenia', 'datum_podpisu', 'datum_ucinnosti', 'platnost_do',
    'typ', 'stav', 'druh', 'rezort', 'zdroj',
    'service_category', 'actual_subject', 'penalty_asymmetry',
    'auto_renewal', 'bezodplatne', 'funding_type', 'grant_amount',
    'hidden_entity_count', 'penalty_count', 'iban_count',
    'subcontracting_mentioned', 'subcontractor_count', 'subcontractor_max_percentage',
    'flag_count', 'dodavatel_tax_status', 'vszp_debt',
    'ruz_established', 'ruz_org_size_id',
}


def _browse_where(params):
    clauses, bindings = [], []

    def add(clause, val):
        bindings.append(val)
        clauses.append(clause.replace("?", f"${len(bindings)}"))

    for col in ('nazov_zmluvy', 'cislo_zmluvy', 'dodavatel', 'dodavatel_ico',
                'objednavatel', 'objednavatel_ico', 'poznamka', 'popis',
                'zdroj', 'actual_subject'):
        v = params.get(col)
        if v:
            prefix = 'e' if col in ('actual_subject',) else 'z'
            add(f"{prefix}.{col} LIKE ?", f"%{v}%")

    for col in ('typ', 'stav', 'druh', 'rezort_id'):
        v = params.get(col)
        if v:
            add(f"z.{col} = ?", v)

    for col in ('service_category', 'penalty_asymmetry', 'funding_type'):
        v = params.get(col)
        if v:
            add(f"e.{col} = ?", v)

    for col in ('auto_renewal', 'bezodplatne'):
        v = params.get(col)
        if v in ('0', '1'):
            add(f"e.{col} = ?", int(v))

    for col, prefix in [('suma', 'z'), ('suma_celkom', 'z')]:
        v_min = params.get(f"{col}_min")
        v_max = params.get(f"{col}_max")
        if v_min:
            add(f"{prefix}.{col} >= ?", float(v_min))
        if v_max:
            add(f"{prefix}.{col} <= ?", float(v_max))

    for db_col, param_prefix in [
        ('datum_zverejnenia', 'date'),
        ('datum_podpisu', 'podpis'),
        ('datum_ucinnosti', 'ucinnost'),
    ]:
        v_from = params.get(f"{param_prefix}_from")
        v_to = params.get(f"{param_prefix}_to")
        if v_from:
            add(f"z.{db_col} >= ?", v_from)
        if v_to:
            add(f"z.{db_col} <= ?", v_to + " 23:59:59")

    for col in ('hidden_entity_count', 'penalty_count', 'iban_count'):
        param = col.replace('_count', '_min') if col != 'hidden_entity_count' else 'hidden_entity_min'
        v = params.get(param)
        if v:
            add(f"e.{col} >= ?", int(v))

    if params.get('suma_null') == '1':
        clauses.append("z.suma IS NULL")
    if params.get('suma_gt'):
        add("z.suma > ?", float(params['suma_gt']))
    if params.get('ico_missing') == '1':
        clauses.append("(z.dodavatel_ico = '' OR z.dodavatel_ico IS NULL)")

    v = params.get('has_extraction')
    if v == '1':
        clauses.append("e.zmluva_id IS NOT NULL")
    elif v == '0':
        clauses.append("e.zmluva_id IS NULL")

    v = params.get('dodavatel_tax_status')
    if v:
        add("z.dodavatel_ico IN (SELECT ico FROM tax_reliability WHERE status = ?)", v)

    v = params.get('debtor')
    if v == 'vszp':
        clauses.append("z.dodavatel_ico IN (SELECT cin FROM vszp_debtors WHERE cin IS NOT NULL)")
    elif v == 'socpoist':
        clauses.append("z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = 'socpoist_debtor')")
    elif v == 'any':
        clauses.append("(z.dodavatel_ico IN (SELECT cin FROM vszp_debtors WHERE cin IS NOT NULL) OR z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = 'socpoist_debtor'))")

    if params.get('ruz_terminated') == '1':
        clauses.append("ruz.terminated_on IS NOT NULL")
    if params.get('ruz_fresh') == '1':
        clauses.append("z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = 'fresh_company')")
    if params.get('ruz_micro') == '1':
        clauses.append("ruz.organization_size_id IN (1, 2)")

    if params.get('flag'):
        add("z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = ?)", params['flag'])
    if params.get('has_flag') == '1':
        clauses.append("z.id IN (SELECT zmluva_id FROM red_flags)")
    elif params.get('has_flag') == '0':
        clauses.append("z.id NOT IN (SELECT zmluva_id FROM red_flags)")

    where = " AND ".join(clauses) if clauses else "1=1"
    return where, bindings


@app.get("/api/browse")
def api_browse(request: Request):
    params = dict(request.query_params)
    where, bindings = _browse_where(params)

    join = """LEFT JOIN extractions e ON e.zmluva_id = z.id
              LEFT JOIN (
                  SELECT zmluva_id, count(*) as flag_count,
                         string_agg(flag_type, ', ') as flag_labels
                  FROM red_flags GROUP BY zmluva_id
              ) rf ON rf.zmluva_id = z.id
              LEFT JOIN tax_reliability tr ON tr.ico = z.dodavatel_ico
              LEFT JOIN (
                  SELECT cin, max(amount) as max_debt FROM vszp_debtors WHERE cin IS NOT NULL GROUP BY cin
              ) vd ON vd.cin = z.dodavatel_ico
              LEFT JOIN (
                  SELECT zmluva_id, detail FROM red_flags WHERE flag_type = 'socpoist_debtor'
              ) spd ON spd.zmluva_id = z.id
              LEFT JOIN ruz_entities ruz ON ruz.cin = z.dodavatel_ico"""

    sort_col = params.get('sort', 'datum_zverejnenia')
    if sort_col not in _BROWSE_SORT_COLS:
        sort_col = 'datum_zverejnenia'
    sort_dir = 'ASC' if params.get('sort_dir') == 'asc' else 'DESC'

    if sort_col in ('service_category', 'actual_subject', 'penalty_asymmetry',
                     'auto_renewal', 'bezodplatne', 'funding_type', 'grant_amount',
                     'hidden_entity_count', 'penalty_count', 'iban_count',
                     'subcontracting_mentioned', 'subcontractor_count',
                     'subcontractor_max_percentage'):
        sort_expr = f"e.{sort_col}"
    elif sort_col == 'flag_count':
        sort_expr = "rf.flag_count"
    elif sort_col == 'dodavatel_tax_status':
        sort_expr = "tr.status"
    elif sort_col == 'vszp_debt':
        sort_expr = "vd.max_debt"
    elif sort_col in ('ruz_established', 'ruz_org_size_id'):
        sort_expr = f"ruz.{'established_on' if sort_col == 'ruz_established' else 'organization_size_id'}"
    else:
        sort_expr = f"z.{sort_col}"

    limit = min(int(params.get('limit', 100)), 10000)
    offset = int(params.get('offset', 0))

    total = qval(f"SELECT count(*) FROM zmluvy z {join} WHERE {where}", bindings) or 0

    n = len(bindings)
    rows = q(
        f"""SELECT z.*,
            e.service_category, e.actual_subject, e.penalty_asymmetry,
            e.auto_renewal, e.bezodplatne, e.funding_type, e.grant_amount,
            e.hidden_entity_count, e.penalty_count, e.iban_count,
            e.subcontracting_mentioned, e.subcontractor_count,
            e.subcontractor_max_percentage,
            e.extraction_json,
            COALESCE(rf.flag_count, 0) as flag_count,
            rf.flag_labels,
            tr.status as dodavatel_tax_status,
            vd.max_debt as vszp_debt,
            spd.detail as socpoist_debt_detail,
            ruz.established_on as ruz_established,
            ruz.terminated_on as ruz_terminated,
            ruz.legal_form as ruz_legal_form,
            ruz.organization_size as ruz_org_size,
            ruz.organization_size_id as ruz_org_size_id,
            ruz.nace_category as ruz_nace
        FROM zmluvy z {join}
        WHERE {where}
        ORDER BY {sort_expr} {sort_dir}
        LIMIT ${n + 1} OFFSET ${n + 2}""",
        bindings + [limit, offset])

    for r in rows:
        detail = r.pop('socpoist_debt_detail', None)
        if detail:
            m = re.search(r'dlh:\s*([\d,]+\.\d+)', detail)
            r['socpoist_debt'] = float(m.group(1).replace(',', '')) if m else None
        else:
            r['socpoist_debt'] = None

        ej_raw = r.pop('extraction_json', None)
        sigs = ''
        if ej_raw:
            try:
                ej_data = json.loads(ej_raw)
                names = [s['name'] for s in (ej_data.get('signatories') or []) if s.get('name')]
                sigs = ', '.join(names)
            except Exception:
                pass
        r['signatories'] = sigs

    if params.get('format') == 'csv':
        return _browse_csv(rows)

    return {"rows": rows, "total": total}


def _browse_csv(rows):
    if not rows:
        return Response(content="", media_type="text/csv")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=crz_export.csv"},
    )


@app.get("/api/browse_filters")
def api_browse_filters(request: Request):
    rezorty = q("SELECT DISTINCT rezort_id, rezort FROM zmluvy WHERE rezort != '' ORDER BY rezort")
    categories = q("SELECT DISTINCT service_category FROM extractions WHERE service_category IS NOT NULL ORDER BY service_category")
    funding = q("SELECT DISTINCT funding_type FROM extractions WHERE funding_type IS NOT NULL AND funding_type != '' ORDER BY funding_type")
    flags = q("SELECT id, label FROM flag_rules WHERE enabled = 1 ORDER BY label")
    return {
        "rezorty": [{"id": r["rezort_id"], "nazov": r["rezort"]} for r in rezorty],
        "categories": [r["service_category"] for r in categories],
        "funding_types": [r["funding_type"] for r in funding],
        "flag_rules": [{"id": r["id"], "label": r["label"]} for r in flags],
    }


@app.get("/api/search")
def api_search(request: Request):
    params = dict(request.query_params)
    query = (params.get("q") or "").strip()
    if not query:
        return {"rows": [], "total": 0, "query": ""}

    limit = min(int(params.get("limit", 50)), 200)
    offset = int(params.get("offset", 0))
    like_pat = f"%{query}%"

    # DuckDB FTS via fts_main_zmluvy.match_bm25
    try:
        fts_source = f"""
            SELECT id AS zid, 'text' AS src FROM (
                SELECT *, fts_main_zmluvy.match_bm25(id, $1) AS score
                FROM zmluvy
            ) sub WHERE score IS NOT NULL
        """
        # Test if FTS works
        with _db_lock:
            get_db().execute(f"SELECT fts_main_zmluvy.match_bm25(1, $1)", [query])
        use_fts = True
    except Exception:
        use_fts = False

    if use_fts:
        text_source = f"""
            SELECT id AS zid, 'text' AS src FROM (
                SELECT id, fts_main_zmluvy.match_bm25(id, $1) AS score FROM zmluvy
            ) sub WHERE score IS NOT NULL
        """
    else:
        text_source = """
            SELECT id AS zid, 'text' AS src FROM zmluvy
            WHERE nazov_zmluvy LIKE $1 OR dodavatel LIKE $1 OR objednavatel LIKE $1
                OR poznamka LIKE $1 OR popis LIKE $1
        """

    sources_sql = f"""
        {text_source}
        UNION
        SELECT zmluva_id, 'subject' FROM extractions WHERE actual_subject LIKE $1
        UNION
        SELECT id, 'ico' FROM zmluvy WHERE dodavatel_ico LIKE $1 OR objednavatel_ico LIKE $1
        UNION
        SELECT zmluva_id, 'extraction' FROM extractions WHERE extraction_json LIKE $1
        UNION
        SELECT zmluva_id, 'attachment' FROM prilohy WHERE nazov LIKE $1
        UNION
        SELECT z2.id, 'vszp_debtor' FROM zmluvy z2
            JOIN vszp_debtors vd2 ON vd2.cin = z2.dodavatel_ico
            WHERE vd2.name LIKE $1 OR vd2.cin LIKE $1
        UNION
        SELECT z3.id, 'socpoist_debtor' FROM zmluvy z3
            JOIN red_flags rf3 ON rf3.zmluva_id = z3.id AND rf3.flag_type = 'socpoist_debtor'
            WHERE rf3.detail LIKE $1
    """

    search_param = like_pat if not use_fts else query
    # For FTS + LIKE mixed: use query for FTS source, like_pat for LIKE sources
    # Simplify: use like_pat for everything (FTS will use $1 which is like_pat)
    # Actually, FTS needs the raw query, not LIKE pattern. Let's bind both.
    # Use $1 = raw query (for FTS), $2 = like pattern (for LIKE)
    if use_fts:
        text_source = f"""
            SELECT id AS zid, 'text' AS src FROM (
                SELECT id, fts_main_zmluvy.match_bm25(id, $1) AS score FROM zmluvy
            ) sub WHERE score IS NOT NULL
        """
        sources_sql = f"""
            {text_source}
            UNION
            SELECT zmluva_id, 'subject' FROM extractions WHERE actual_subject LIKE $2
            UNION
            SELECT id, 'ico' FROM zmluvy WHERE dodavatel_ico LIKE $2 OR objednavatel_ico LIKE $2
            UNION
            SELECT zmluva_id, 'extraction' FROM extractions WHERE extraction_json LIKE $2
            UNION
            SELECT zmluva_id, 'attachment' FROM prilohy WHERE nazov LIKE $2
            UNION
            SELECT z2.id, 'vszp_debtor' FROM zmluvy z2
                JOIN vszp_debtors vd2 ON vd2.cin = z2.dodavatel_ico
                WHERE vd2.name LIKE $2 OR vd2.cin LIKE $2
            UNION
            SELECT z3.id, 'socpoist_debtor' FROM zmluvy z3
                JOIN red_flags rf3 ON rf3.zmluva_id = z3.id AND rf3.flag_type = 'socpoist_debtor'
                WHERE rf3.detail LIKE $2
        """
        base_bindings = [query, like_pat]
    else:
        base_bindings = [like_pat]

    result_sql = f"""
        WITH matched_ids AS ({sources_sql}),
        agg AS (
            SELECT zid, string_agg(DISTINCT src, ',') AS match_sources
            FROM matched_ids GROUP BY zid
        )
        SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
               z.objednavatel, z.objednavatel_ico, z.suma,
               z.datum_zverejnenia, z.typ, z.stav, z.rezort, z.crz_url,
               e.actual_subject, e.service_category,
               e.hidden_entity_count, e.penalty_asymmetry,
               COALESCE(rf.flag_count, 0) AS flag_count,
               tr.status AS dodavatel_tax_status,
               agg.match_sources
        FROM agg
        JOIN zmluvy z ON z.id = agg.zid
        LEFT JOIN extractions e ON e.zmluva_id = z.id
        LEFT JOIN (
            SELECT zmluva_id, count(*) AS flag_count FROM red_flags GROUP BY zmluva_id
        ) rf ON rf.zmluva_id = z.id
        LEFT JOIN tax_reliability tr ON tr.ico = z.dodavatel_ico
        ORDER BY rf.flag_count DESC NULLS LAST, z.datum_zverejnenia DESC
        LIMIT ${len(base_bindings) + 1} OFFSET ${len(base_bindings) + 2}
    """

    rows = q(result_sql, base_bindings + [limit, offset])

    count_sql = f"SELECT count(DISTINCT zid) FROM ({sources_sql})"
    total = qval(count_sql, base_bindings) or len(rows)

    return {"rows": rows, "total": total, "query": query}


# ---------------------------------------------------------------------------
# Datasette-compatible SQL API
# ---------------------------------------------------------------------------

# DuckDB functions/keywords that can read files, write data, or escape the sandbox
_FORBIDDEN_SQL_PATTERNS = re.compile(
    r"""(?ix)                     # case-insensitive, verbose
    \b(?:
        read_csv | read_csv_auto | read_parquet | read_json | read_json_auto |
        read_blob | read_text |
        write_csv | write_parquet |
        copy\s | export\s |
        attach | detach |
        install | load |
        create\s | drop\s | alter\s | truncate\s |
        insert\s | update\s | delete\s | merge\s |
        call\s | pragma\s | set\s |
        delta_scan | parquet_scan | parquet_metadata | parquet_schema |
        csv_scan | json_scan |
        glob\s*\( | list_files\b | ls\s*\( |
        read_ndjson | read_ndjson_auto |
        query_table | information_schema |
        getenv | current_setting |
        httpfs | http_get | http_post |
        postgres_scan | sqlite_scan | mysql_scan |
        sniff_csv
    )
    """,
)

# Tables that agents are allowed to query
_ALLOWED_TABLES = {
    "zmluvy", "extractions", "red_flags", "flag_rules", "prilohy",
    "tax_reliability", "ruz_entities", "ruz_entities_full", "ruz_equity",
    "vszp_debtors", "socpoist_debtors", "fs_tax_debtors",
    "fs_vat_deregistered", "fs_vat_dereg_reasons", "fs_corporate_tax",
    "rezorty",
}


def _validate_sql(sql: str) -> str | None:
    """Return an error message if the SQL is unsafe, or None if OK."""
    sql_stripped = sql.strip()
    sql_upper = sql_stripped.upper()

    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        return "Only SELECT queries allowed"

    if ";" in sql_stripped.rstrip(";"):
        return "Multiple statements not allowed"

    if _FORBIDDEN_SQL_PATTERNS.search(sql_stripped):
        return "Query contains forbidden functions or keywords"

    return None


@app.get("/data/crz.json")
def datasette_sql_api(sql: str = Query(default=""), _shape: str = Query(default="array")):
    """Datasette-compatible SQL endpoint for agent compatibility."""
    if not sql.strip():
        return JSONResponse({"ok": False, "error": "No SQL provided"}, status_code=400)

    error = _validate_sql(sql)
    if error:
        return JSONResponse({"ok": False, "error": error}, status_code=403)

    try:
        rows = q(sql)
        if _shape == "array":
            return rows
        return {"ok": True, "rows": rows}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


# ---------------------------------------------------------------------------
# Dashboard HTML routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/browse", response_class=HTMLResponse)
@app.get("/search", response_class=HTMLResponse)
@app.get("/methodology", response_class=HTMLResponse)
def serve_dashboard():
    return DASHBOARD_HTML_PATH.read_text(encoding="utf-8")


@app.get("/browse/{contract_id}", response_class=HTMLResponse)
def serve_detail(contract_id: str):
    return DETAIL_HTML_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CRZ Delta Lake Server")
    parser.add_argument("--port", type=int, default=8002)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--tables", default=None, help="Path to Delta tables directory")
    args = parser.parse_args()

    global TABLES_DIR
    if args.tables:
        TABLES_DIR = Path(args.tables)

    import uvicorn
    print(f"CRZ Delta Lake Server: http://{args.host}:{args.port}")
    print(f"  Dashboard:  http://{args.host}:{args.port}/")
    print(f"  SQL API:    http://{args.host}:{args.port}/data/crz.json?sql=SELECT+count(*)+FROM+zmluvy")
    print(f"  Tables dir: {TABLES_DIR}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
