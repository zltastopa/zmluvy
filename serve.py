"""Unified CRZ server — dashboard + datasette on a single port.

Usage:
    uv run python serve.py              # http://localhost:8001
    uv run python serve.py --port 9000  # custom port
"""

import argparse
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import yaml
from datasette.app import Datasette

from settings import get_path

import csv
import io

ROOT = Path(__file__).parent
DB_PATH = get_path("CRZ_DB_PATH", "crz.db")
DASHBOARD_HTML_PATH = ROOT / "dashboard.html"
DETAIL_HTML_PATH = ROOT / "detail.html"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def build_where(params):
    clauses, bindings = [], []
    if params.get("date_from"):
        clauses.append("z.datum_zverejnenia >= ?"); bindings.append(params["date_from"])
    if params.get("date_to"):
        clauses.append("z.datum_zverejnenia <= ?"); bindings.append(params["date_to"] + " 23:59:59")
    if params.get("suma_min"):
        clauses.append("z.suma >= ?"); bindings.append(float(params["suma_min"]))
    if params.get("suma_max"):
        clauses.append("z.suma <= ?"); bindings.append(float(params["suma_max"]))
    if params.get("rezort_id"):
        clauses.append("z.rezort_id = ?"); bindings.append(params["rezort_id"])
    if params.get("typ"):
        clauses.append("z.typ = ?"); bindings.append(params["typ"])
    if params.get("stav"):
        clauses.append("z.stav = ?"); bindings.append(params["stav"])
    if params.get("service_category"):
        clauses.append("e.service_category = ?"); bindings.append(params["service_category"])
    if params.get("suma_null") == "1":
        clauses.append("z.suma IS NULL")
    if params.get("suma_gt"):
        clauses.append("z.suma > ?"); bindings.append(float(params["suma_gt"]))
    if params.get("ico_missing") == "1":
        clauses.append("(z.dodavatel_ico = '' OR z.dodavatel_ico IS NULL)")
    if params.get("penalty_asymmetry"):
        clauses.append("e.penalty_asymmetry = ?"); bindings.append(params["penalty_asymmetry"])
    if params.get("bezodplatne") == "1":
        clauses.append("e.bezodplatne = 1")
    if params.get("flag"):
        clauses.append("z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = ?)")
        bindings.append(params["flag"])
    return " AND ".join(clauses) if clauses else "1=1", bindings


EJOIN = "LEFT JOIN extractions e ON e.zmluva_id = z.id"


def _join(params, extraction=False):
    """Return extraction JOIN clause when needed by params or forced."""
    need = extraction or params.get("service_category") or params.get(
        "penalty_asymmetry") or params.get("bezodplatne")
    return EJOIN if need else ""


# ---------------------------------------------------------------------------
# API handlers — each returns a JSON-serialisable object
# ---------------------------------------------------------------------------

def api_filters(db, params):
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
    where, bindings = build_where(params)
    row = db.execute(
        f"""SELECT count(*) as total, count(z.suma) as with_amount,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value,
            coalesce(max(z.suma),0) as max_value, coalesce(min(z.suma),0) as min_value,
            count(CASE WHEN z.typ='dodatok' THEN 1 END) as amendments,
            count(CASE WHEN z.stav='zrušená' THEN 1 END) as cancelled
        FROM zmluvy z {_join(params)} WHERE {where}""", bindings).fetchone()
    return dict(row)


def api_timeline(db, params):
    where, bindings = build_where(params)
    rows = db.execute(
        f"""SELECT substr(z.datum_zverejnenia,1,7) as month, count(*) as count,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value
        FROM zmluvy z {_join(params)} WHERE {where} AND z.datum_zverejnenia!=''
        GROUP BY month ORDER BY month""", bindings).fetchall()
    return [dict(r) for r in rows]


def api_by_rezort(db, params):
    where, bindings = build_where(params)
    rows = db.execute(
        f"""SELECT z.rezort as name, count(*) as count,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value
        FROM zmluvy z {_join(params)} WHERE {where} AND z.rezort!=''
        GROUP BY z.rezort ORDER BY count DESC LIMIT 20""", bindings).fetchall()
    return [dict(r) for r in rows]


def api_by_category(db, params):
    where, bindings = build_where(params)
    rows = db.execute(
        f"""SELECT e.service_category as category, count(*) as count,
            coalesce(sum(z.suma),0) as total_value, coalesce(avg(z.suma),0) as avg_value
        FROM zmluvy z {EJOIN} WHERE {where} AND e.service_category IS NOT NULL
        GROUP BY e.service_category ORDER BY count DESC""", bindings).fetchall()
    return [dict(r) for r in rows]


def api_penalties(db, params):
    where, bindings = build_where(params)
    rows = db.execute(
        f"""SELECT e.penalty_asymmetry as asymmetry, count(*) as count
        FROM zmluvy z {EJOIN} WHERE {where} AND e.penalty_asymmetry IS NOT NULL
        GROUP BY e.penalty_asymmetry ORDER BY count DESC""", bindings).fetchall()
    return [dict(r) for r in rows]


def api_top_contracts(db, params):
    where, bindings = build_where(params)
    rows = db.execute(
        f"""SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
            z.objednavatel, z.objednavatel_ico,
            z.suma, z.suma_celkom, z.datum_zverejnenia, z.rezort, z.rezort_id,
            z.typ, z.crz_url, e.actual_subject
        FROM zmluvy z {_join(params, extraction=True)} WHERE {where} AND z.suma IS NOT NULL
        ORDER BY z.suma DESC LIMIT 25""", bindings).fetchall()
    return [dict(r) for r in rows]


def api_anomalies(db, params):
    where, bindings = build_where(params)
    j = _join(params)
    anomalies = []

    for query, atype, label, severity in [
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {where} AND z.suma IS NULL",
         "missing_amount", "Zmluvy bez uvedenej sumy", "info"),
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {where} AND z.suma > 1000000",
         "high_value", "Zmluvy nad 1 mil. EUR", "warning"),
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {where} AND (z.dodavatel_ico='' OR z.dodavatel_ico IS NULL)",
         "missing_ico", "Dodavatel bez ICO", "info"),
        (f"SELECT count(*) FROM zmluvy z {j} WHERE {where} AND z.stav='zrušená'",
         "cancelled", "Zrusene zmluvy", "warning"),
    ]:
        cnt = db.execute(query, bindings).fetchone()[0]
        if cnt > 0:
            anomalies.append({"type": atype, "label": label, "count": cnt, "severity": severity})

    # Extraction-based anomalies (always need join)
    for query, atype, label, severity in [
        (f"SELECT count(*) FROM zmluvy z {EJOIN} WHERE {where} AND e.penalty_asymmetry='supplier_advantage'",
         "supplier_advantage", "Pokuty zvyhodnujuce dodavatela (neobvykle)", "warning"),
        (f"SELECT count(*) FROM zmluvy z {EJOIN} WHERE {where} AND e.bezodplatne=1",
         "bezodplatne", "Bezodplatne zmluvy", "info"),
    ]:
        cnt = db.execute(query, bindings).fetchone()[0]
        if cnt > 0:
            anomalies.append({"type": atype, "label": label, "count": cnt, "severity": severity})

    rows = db.execute(
        f"""SELECT
            CASE WHEN z.suma<1000 THEN '< 1 tis.'
                 WHEN z.suma<10000 THEN '1-10 tis.'
                 WHEN z.suma<100000 THEN '10-100 tis.'
                 WHEN z.suma<1000000 THEN '100 tis.-1 mil.'
                 ELSE '> 1 mil.' END as bucket, count(*) as count
        FROM zmluvy z {j} WHERE {where} AND z.suma IS NOT NULL
        GROUP BY bucket ORDER BY min(z.suma)""", bindings).fetchall()

    return {"anomalies": anomalies, "amount_distribution": [dict(r) for r in rows]}


def api_detail(db, params):
    """Detail view for a single entity: contract, supplier, buyer, or rezort."""

    if params.get("id"):
        # Single contract detail
        row = db.execute(
            "SELECT * FROM zmluvy WHERE id = ?", [int(params["id"])]
        ).fetchone()
        if not row:
            return {"error": "not_found"}
        contract = dict(row)

        # Extraction data
        ext = db.execute(
            "SELECT * FROM extractions WHERE zmluva_id = ?", [int(params["id"])]
        ).fetchone()
        contract["extraction"] = dict(ext) if ext else None

        # Attachments
        atts = db.execute(
            "SELECT * FROM prilohy WHERE zmluva_id = ?", [int(params["id"])]
        ).fetchall()
        contract["prilohy"] = [dict(a) for a in atts]

        # Other contracts with same supplier
        related = db.execute(
            """SELECT z.id, z.nazov_zmluvy, z.suma, z.datum_zverejnenia, z.typ, e.actual_subject
            FROM zmluvy z LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE z.dodavatel_ico = ? AND z.dodavatel_ico != '' AND z.id != ?
            ORDER BY z.datum_zverejnenia DESC LIMIT 10""",
            [contract["dodavatel_ico"], int(params["id"])]
        ).fetchall()
        contract["related_supplier_contracts"] = [dict(r) for r in related]

        # Red flags
        flags = db.execute(
            """SELECT rf.flag_type, fr.label, fr.severity, fr.description, rf.detail
            FROM red_flags rf JOIN flag_rules fr ON fr.id = rf.flag_type
            WHERE rf.zmluva_id = ? ORDER BY fr.severity DESC""",
            [int(params["id"])]
        ).fetchall()
        contract["red_flags"] = [dict(f) for f in flags]

        # Tax reliability for both parties
        for ico_col, key in [("dodavatel_ico", "dodavatel_tax_status"),
                             ("objednavatel_ico", "objednavatel_tax_status")]:
            ico_val = contract.get(ico_col)
            if ico_val:
                tr = db.execute(
                    "SELECT status FROM tax_reliability WHERE ico = ?", [ico_val]
                ).fetchone()
                contract[key] = tr["status"] if tr else None
            else:
                contract[key] = None

        return {"kind": "contract", "data": contract}

    # Supplier or buyer detail — same logic, different columns
    for role, ico_col, other_col, other_ico_col in [
        ("dodavatel", "dodavatel_ico", "objednavatel", "objednavatel_ico"),
        ("objednavatel", "objednavatel_ico", "dodavatel", "dodavatel_ico"),
    ]:
        ico = params.get(ico_col)
        if not ico:
            continue
        rows = db.execute(
            f"""SELECT id, nazov_zmluvy, dodavatel, objednavatel, suma, suma_celkom,
                datum_zverejnenia, rezort, typ, stav, crz_url
            FROM zmluvy WHERE {ico_col} = ?
            ORDER BY datum_zverejnenia DESC""", [ico]
        ).fetchall()
        contracts = [dict(r) for r in rows]
        if not contracts:
            return {"error": "not_found"}

        stats = db.execute(
            f"""SELECT count(*) as total, coalesce(sum(suma),0) as total_value,
                coalesce(avg(suma),0) as avg_value, count(suma) as with_amount,
                min(datum_zverejnenia) as first_contract, max(datum_zverejnenia) as last_contract,
                count(DISTINCT {other_ico_col}) as unique_counterparties
            FROM zmluvy WHERE {ico_col} = ?""", [ico]
        ).fetchone()

        top_counterparties = db.execute(
            f"""SELECT {other_col} as name, {other_ico_col} as ico, count(*) as count,
                coalesce(sum(suma),0) as total_value
            FROM zmluvy WHERE {ico_col} = ? AND {other_col} != ''
            GROUP BY {other_ico_col} ORDER BY count DESC LIMIT 10""", [ico]
        ).fetchall()

        return {
            "kind": role,
            "ico": ico,
            "name": contracts[0][role],
            "stats": dict(stats),
            "top_counterparties": [dict(r) for r in top_counterparties],
            "contracts": contracts[:50],
        }

    if params.get("rezort_id"):
        rid = params["rezort_id"]
        rows = db.execute(
            """SELECT id, nazov_zmluvy, dodavatel, objednavatel, suma, suma_celkom,
                datum_zverejnenia, typ, stav, crz_url
            FROM zmluvy WHERE rezort_id = ?
            ORDER BY datum_zverejnenia DESC""", [rid]
        ).fetchall()
        contracts = [dict(r) for r in rows]

        stats = db.execute(
            """SELECT count(*) as total, coalesce(sum(suma),0) as total_value,
                coalesce(avg(suma),0) as avg_value, count(suma) as with_amount,
                min(datum_zverejnenia) as first_contract, max(datum_zverejnenia) as last_contract,
                count(DISTINCT dodavatel_ico) as unique_suppliers,
                count(DISTINCT objednavatel_ico) as unique_buyers
            FROM zmluvy WHERE rezort_id = ?""", [rid]
        ).fetchone()

        rezort_name = db.execute(
            "SELECT nazov FROM rezorty WHERE id = ?", [rid]
        ).fetchone()

        top_suppliers = db.execute(
            """SELECT dodavatel, dodavatel_ico, count(*) as count,
                coalesce(sum(suma),0) as total_value
            FROM zmluvy WHERE rezort_id = ? AND dodavatel != ''
            GROUP BY dodavatel_ico ORDER BY total_value DESC LIMIT 10""", [rid]
        ).fetchall()

        categories = db.execute(
            """SELECT e.service_category as category, count(*) as count
            FROM zmluvy z LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE z.rezort_id = ? AND e.service_category IS NOT NULL
            GROUP BY e.service_category ORDER BY count DESC LIMIT 10""", [rid]
        ).fetchall()

        return {
            "kind": "rezort",
            "rezort_id": rid,
            "name": rezort_name["nazov"] if rezort_name else rid,
            "stats": dict(stats),
            "top_suppliers": [dict(r) for r in top_suppliers],
            "categories": [dict(r) for r in categories],
            "contracts": contracts[:50],
        }

    return {"error": "missing_param"}


def api_flags(db, params):
    """Red flags summary — counts per flag type, respecting filters."""
    where, bindings = build_where(params)
    j = _join(params, extraction=True)

    # Per-flag counts (filtered)
    rows = db.execute(
        f"""SELECT fr.id, fr.label, fr.severity, fr.description, count(rf.id) as count
        FROM flag_rules fr
        LEFT JOIN red_flags rf ON rf.flag_type = fr.id
        LEFT JOIN zmluvy z ON z.id = rf.zmluva_id
        {j}
        WHERE fr.enabled = 1 AND ({where} OR rf.id IS NULL)
        GROUP BY fr.id
        ORDER BY count DESC""",
        bindings,
    ).fetchall()

    rules = [dict(r) for r in rows]

    # Total flagged contracts (filtered)
    total = db.execute(
        f"""SELECT count(DISTINCT rf.zmluva_id) as total
        FROM red_flags rf
        JOIN zmluvy z ON z.id = rf.zmluva_id
        {j}
        WHERE {where}""",
        bindings,
    ).fetchone()

    return {
        "rules": rules,
        "total_flagged": total["total"] if total else 0,
    }


def api_flags_by_rezort(db, params):
    """Red flag counts broken down by rezort."""
    where, bindings = build_where(params)
    flag_type = params.get("flag_type")
    flag_clause = "AND rf.flag_type = ?" if flag_type else ""
    flag_bindings = [flag_type] if flag_type else []

    rows = db.execute(
        f"""SELECT z.rezort as name, z.rezort_id,
            count(DISTINCT rf.zmluva_id) as flagged,
            count(DISTINCT z.id) as total
        FROM zmluvy z
        LEFT JOIN red_flags rf ON rf.zmluva_id = z.id {flag_clause}
        {_join(params)}
        WHERE {where} AND z.rezort != ''
        GROUP BY z.rezort_id
        HAVING flagged > 0
        ORDER BY flagged DESC
        LIMIT 20""",
        flag_bindings + bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_flags_top(db, params):
    """Contracts with the most red flags."""
    where, bindings = build_where(params)
    rows = db.execute(
        f"""SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
            z.objednavatel, z.objednavatel_ico, z.suma,
            z.datum_zverejnenia, z.rezort, z.rezort_id, z.crz_url,
            count(rf.id) as flag_count,
            group_concat(fr.label, ', ') as flag_labels
        FROM red_flags rf
        JOIN zmluvy z ON z.id = rf.zmluva_id
        JOIN flag_rules fr ON fr.id = rf.flag_type
        {_join(params)}
        WHERE {where}
        GROUP BY z.id
        ORDER BY flag_count DESC, z.suma DESC
        LIMIT 50""",
        bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_flags_timeline(db, params):
    """Monthly flag counts."""
    where, bindings = build_where(params)
    flag_type = params.get("flag_type")
    flag_clause = "AND rf.flag_type = ?" if flag_type else ""
    flag_bindings = [flag_type] if flag_type else []

    rows = db.execute(
        f"""SELECT substr(z.datum_zverejnenia, 1, 7) as month,
            count(DISTINCT rf.zmluva_id) as flagged,
            count(DISTINCT z.id) as total
        FROM zmluvy z
        LEFT JOIN red_flags rf ON rf.zmluva_id = z.id {flag_clause}
        {_join(params)}
        WHERE {where} AND z.datum_zverejnenia != ''
        GROUP BY month
        ORDER BY month""",
        flag_bindings + bindings,
    ).fetchall()
    return [dict(r) for r in rows]


def api_investigation_categories(db, params):
    """Investigative categories with counts and sample contracts."""
    where, bindings = build_where(params)
    base_cte = f"WITH base AS (SELECT DISTINCT z.id FROM zmluvy z {EJOIN} WHERE {where})"

    def q_count(sql):
        row = db.execute(base_cte + " " + sql, bindings).fetchone()
        return row[0] if row else 0

    def q_rows(sql):
        rows = db.execute(base_cte + " " + sql, bindings).fetchall()
        return [dict(r) for r in rows]

    categories = []

    # 1) Date anomalies
    date_condition = """
        z.datum_ucinnosti = '0000-00-00'
        OR CAST(substr(z.datum_podpisu, 1, 4) AS INTEGER) < 1990
        OR CAST(substr(z.datum_podpisu, 1, 4) AS INTEGER) > 2030
        OR CAST(substr(z.datum_ucinnosti, 1, 4) AS INTEGER) > 2030
        OR (
            date(z.datum_podpisu) IS NOT NULL
            AND date(z.datum_zverejnenia) IS NOT NULL
            AND (julianday(date(z.datum_podpisu)) - julianday(date(z.datum_zverejnenia))) > 30
        )
        OR (
            date(z.datum_ucinnosti) IS NOT NULL
            AND date(z.datum_zverejnenia) IS NOT NULL
            AND (julianday(date(z.datum_ucinnosti)) - julianday(date(z.datum_zverejnenia))) < 0
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
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            WHERE {date_condition}
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC
            LIMIT 8"""
        ),
    })

    # 2) Hidden price but grant amount exists in extraction
    hidden_grant_condition = "z.suma IS NULL AND e.grant_amount IS NOT NULL AND trim(e.grant_amount) != ''"
    categories.append({
        "id": "hidden_price_grants",
        "title": "Hidden price with grant amount",
        "description": "No sum in CRZ amount fields, but extracted text includes grant amount.",
        "severity": "danger",
        "count": q_count(
            f"""SELECT count(*)
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id
            WHERE {hidden_grant_condition}"""
        ),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy,
                e.grant_amount, e.funding_type
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id
            WHERE {hidden_grant_condition}
            ORDER BY z.datum_zverejnenia DESC
            LIMIT 8"""
        ),
    })

    # 3) Generic titles
    generic_condition = """
        lower(trim(z.nazov_zmluvy)) IN (
            'zmluva o dielo',
            'rámcová zmluva',
            'zmluva o spolupráci',
            'zmluva o poskytovaní služieb',
            'kúpna zmluva',
            'darovacia zmluva',
            'nájomná zmluva'
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
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            WHERE {generic_condition}
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC
            LIMIT 8"""
        ),
    })

    # 4) Off-hours publication of high-value contracts
    offhours_condition = """
        CAST(strftime('%H', z.datum_zverejnenia) AS INTEGER) IN (0, 1, 2, 3, 4, 5, 22, 23)
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
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            WHERE {offhours_condition}
            ORDER BY z.suma DESC
            LIMIT 8"""
        ),
    })

    # 5) Supplier-advantage penalties
    categories.append({
        "id": "supplier_advantage_penalties",
        "title": "Supplier-advantage penalties",
        "description": "Extracted penalty clauses indicate supplier-side advantage.",
        "severity": "danger",
        "count": q_count(
            """SELECT count(*)
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.penalty_asymmetry = 'supplier_advantage'"""
        ),
        "sample": q_rows(
            """SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy,
                e.penalty_count, e.service_category
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.penalty_asymmetry = 'supplier_advantage'
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC
            LIMIT 8"""
        ),
    })

    # 6) Mirrored bilateral postings (aggregated directional check)
    mirror_cte = f"""WITH base AS (SELECT DISTINCT z.id FROM zmluvy z {EJOIN} WHERE {where}),
        contracts AS (
            SELECT
                z.id,
                z.datum_zverejnenia,
                z.objednavatel,
                z.dodavatel,
                z.suma,
                z.nazov_zmluvy,
                date(z.datum_zverejnenia) AS d,
                round(z.suma, 2) AS amt,
                lower(trim(z.objednavatel)) AS buyer_key,
                lower(trim(z.dodavatel)) AS supplier_key,
                CASE
                    WHEN lower(trim(z.objednavatel)) <= lower(trim(z.dodavatel)) THEN lower(trim(z.objednavatel))
                    ELSE lower(trim(z.dodavatel))
                END AS p1,
                CASE
                    WHEN lower(trim(z.objednavatel)) <= lower(trim(z.dodavatel)) THEN lower(trim(z.dodavatel))
                    ELSE lower(trim(z.objednavatel))
                END AS p2
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            WHERE z.suma IS NOT NULL
              AND trim(z.objednavatel) != ''
              AND trim(z.dodavatel) != ''
        ),
        mirror_groups AS (
            SELECT
                d, amt, p1, p2, count(*) AS n,
                SUM(CASE WHEN buyer_key < supplier_key THEN 1 ELSE 0 END) AS dir_ab,
                SUM(CASE WHEN buyer_key > supplier_key THEN 1 ELSE 0 END) AS dir_ba
            FROM contracts
            GROUP BY d, amt, p1, p2
            HAVING dir_ab > 0 AND dir_ba > 0
        )"""
    mirror_count = db.execute(
        mirror_cte + " SELECT COALESCE(SUM(n), 0) FROM mirror_groups",
        bindings,
    ).fetchone()[0]
    mirror_rows = db.execute(
        mirror_cte + """
        SELECT c.id, NULL AS pair_id, c.datum_zverejnenia, c.objednavatel, c.dodavatel, c.suma, c.nazov_zmluvy
        FROM contracts c
        JOIN mirror_groups g ON c.d = g.d AND c.amt = g.amt AND c.p1 = g.p1 AND c.p2 = g.p2
        ORDER BY c.suma DESC, c.datum_zverejnenia DESC
        LIMIT 8
        """,
        bindings,
    ).fetchall()
    categories.append({
        "id": "mirror_postings",
        "title": "Mirrored bilateral postings",
        "description": "Same-day, same-amount records where buyer/supplier are swapped.",
        "severity": "warning",
        "count": mirror_count,
        "sample": [dict(r) for r in mirror_rows],
    })

    # 7) Entity identity quality
    ico_quality_condition = """
        (z.dodavatel_ico IS NULL OR trim(z.dodavatel_ico) = '' OR z.dodavatel_ico NOT GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
        OR
        (z.objednavatel_ico IS NULL OR trim(z.objednavatel_ico) = '' OR z.objednavatel_ico NOT GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
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
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            WHERE {ico_quality_condition}
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC
            LIMIT 8"""
        ),
    })

    # 8) Repeated amount fingerprints
    amount_pattern_condition = "ROUND(z.suma, 2) IN (10759.80, 5379.88, 5379.90)"
    categories.append({
        "id": "amount_fingerprints",
        "title": "Repeated amount fingerprints",
        "description": "Recurring exact amounts often tied to template-based funding flows.",
        "severity": "info",
        "count": q_count(
            f"SELECT count(*) FROM zmluvy z JOIN base b ON b.id = z.id WHERE z.suma IS NOT NULL AND {amount_pattern_condition}"
        ),
        "sample": q_rows(
            f"""SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            WHERE z.suma IS NOT NULL AND {amount_pattern_condition}
            ORDER BY z.datum_zverejnenia DESC
            LIMIT 8"""
        ),
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
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            WHERE {uvo_gap_condition}
            ORDER BY z.suma DESC
            LIMIT 8"""
        ),
    })

    # 10) Extraction blind spots
    categories.append({
        "id": "extraction_blind_spot",
        "title": "Extraction blind spots",
        "description": "Contracts with no extraction enrichment available.",
        "severity": "warning",
        "count": q_count(
            """SELECT count(*)
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.zmluva_id IS NULL"""
        ),
        "sample": q_rows(
            """SELECT z.id, z.datum_zverejnenia, z.objednavatel, z.dodavatel, z.suma, z.nazov_zmluvy
            FROM zmluvy z
            JOIN base b ON b.id = z.id
            LEFT JOIN extractions e ON e.zmluva_id = z.id
            WHERE e.zmluva_id IS NULL
            ORDER BY COALESCE(z.suma, 0) DESC, z.datum_zverejnenia DESC
            LIMIT 8"""
        ),
    })

    return {"categories": categories}


def api_contracts(db, params):
    """Filtered contract list — returns all matching contracts (up to 200)."""
    where, bindings = build_where(params)
    j = _join(params)
    rows = db.execute(
        f"""SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
            z.objednavatel, z.objednavatel_ico,
            z.suma, z.suma_celkom, z.datum_zverejnenia, z.rezort, z.rezort_id,
            z.typ, z.stav, z.crz_url
        FROM zmluvy z {j}
        WHERE {where}
        ORDER BY z.datum_zverejnenia DESC
        LIMIT 200""", bindings).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Browse API — full-field filterable table
# ---------------------------------------------------------------------------

# Allowed sort columns (whitelist to prevent SQL injection)
_BROWSE_SORT_COLS = {
    'id', 'nazov_zmluvy', 'cislo_zmluvy', 'dodavatel', 'dodavatel_ico',
    'objednavatel', 'objednavatel_ico', 'suma', 'suma_celkom',
    'datum_zverejnenia', 'datum_podpisu', 'datum_ucinnosti', 'platnost_do',
    'typ', 'stav', 'druh', 'rezort', 'zdroj',
    'service_category', 'actual_subject', 'penalty_asymmetry',
    'auto_renewal', 'bezodplatne', 'funding_type', 'grant_amount',
    'hidden_entity_count', 'penalty_count', 'iban_count',
    'flag_count', 'dodavatel_tax_status',
}


def _browse_where(params):
    """Build WHERE clause for browse — supports all fields."""
    clauses, bindings = [], []

    # Text LIKE filters
    for col in ('nazov_zmluvy', 'cislo_zmluvy', 'dodavatel', 'dodavatel_ico',
                'objednavatel', 'objednavatel_ico', 'poznamka', 'popis',
                'zdroj', 'actual_subject'):
        v = params.get(col)
        if v:
            prefix = 'e' if col in ('actual_subject',) else 'z'
            clauses.append(f"{prefix}.{col} LIKE ?")
            bindings.append(f"%{v}%")

    # Exact match filters
    for col in ('typ', 'stav', 'druh', 'rezort_id'):
        v = params.get(col)
        if v:
            clauses.append(f"z.{col} = ?")
            bindings.append(v)

    for col in ('service_category', 'penalty_asymmetry', 'funding_type'):
        v = params.get(col)
        if v:
            clauses.append(f"e.{col} = ?")
            bindings.append(v)

    # Boolean extraction filters
    for col in ('auto_renewal', 'bezodplatne'):
        v = params.get(col)
        if v in ('0', '1'):
            clauses.append(f"e.{col} = ?")
            bindings.append(int(v))

    # Numeric range filters
    for col, prefix in [('suma', 'z'), ('suma_celkom', 'z')]:
        v_min = params.get(f"{col}_min")
        v_max = params.get(f"{col}_max")
        if v_min:
            clauses.append(f"{prefix}.{col} >= ?")
            bindings.append(float(v_min))
        if v_max:
            clauses.append(f"{prefix}.{col} <= ?")
            bindings.append(float(v_max))

    # Date range filters
    for db_col, param_prefix in [
        ('datum_zverejnenia', 'date'),
        ('datum_podpisu', 'podpis'),
        ('datum_ucinnosti', 'ucinnost'),
    ]:
        v_from = params.get(f"{param_prefix}_from")
        v_to = params.get(f"{param_prefix}_to")
        if v_from:
            clauses.append(f"z.{db_col} >= ?")
            bindings.append(v_from)
        if v_to:
            clauses.append(f"z.{db_col} <= ?")
            bindings.append(v_to + " 23:59:59")

    # Extraction numeric minimums
    for col in ('hidden_entity_count', 'penalty_count', 'iban_count'):
        param = col.replace('_count', '_min') if col != 'hidden_entity_count' else 'hidden_entity_min'
        v = params.get(param)
        if v:
            clauses.append(f"e.{col} >= ?")
            bindings.append(int(v))

    # Dashboard anomaly compat filters
    if params.get('suma_null') == '1':
        clauses.append("z.suma IS NULL")
    if params.get('suma_gt'):
        clauses.append("z.suma > ?")
        bindings.append(float(params['suma_gt']))
    if params.get('ico_missing') == '1':
        clauses.append("(z.dodavatel_ico = '' OR z.dodavatel_ico IS NULL)")

    # Has extraction
    v = params.get('has_extraction')
    if v == '1':
        clauses.append("e.zmluva_id IS NOT NULL")
    elif v == '0':
        clauses.append("e.zmluva_id IS NULL")

    # Tax reliability
    v = params.get('dodavatel_tax_status')
    if v:
        clauses.append("z.dodavatel_ico IN (SELECT ico FROM tax_reliability WHERE status = ?)")
        bindings.append(v)

    # Red flags
    if params.get('flag'):
        clauses.append("z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = ?)")
        bindings.append(params['flag'])
    if params.get('has_flag') == '1':
        clauses.append("z.id IN (SELECT zmluva_id FROM red_flags)")
    elif params.get('has_flag') == '0':
        clauses.append("z.id NOT IN (SELECT zmluva_id FROM red_flags)")

    where = " AND ".join(clauses) if clauses else "1=1"
    return where, bindings


def _browse_needs_extraction(params):
    """Check if any extraction-related filter is active."""
    ext_params = (
        'service_category', 'actual_subject', 'penalty_asymmetry', 'funding_type',
        'auto_renewal', 'bezodplatne', 'hidden_entity_min', 'penalty_count_min',
        'iban_count_min', 'has_extraction',
    )
    return any(params.get(p) for p in ext_params)


def api_browse(db, params):
    """Full browse endpoint with all fields, pagination, sorting."""
    where, bindings = _browse_where(params)

    # Always join extractions + red flag counts + tax reliability for the browse view
    join = """LEFT JOIN extractions e ON e.zmluva_id = z.id
              LEFT JOIN (
                  SELECT zmluva_id, count(*) as flag_count,
                         group_concat(flag_type, ', ') as flag_labels
                  FROM red_flags GROUP BY zmluva_id
              ) rf ON rf.zmluva_id = z.id
              LEFT JOIN tax_reliability tr ON tr.ico = z.dodavatel_ico"""

    # Sort
    sort_col = params.get('sort', 'datum_zverejnenia')
    if sort_col not in _BROWSE_SORT_COLS:
        sort_col = 'datum_zverejnenia'
    sort_dir = 'ASC' if params.get('sort_dir') == 'asc' else 'DESC'
    # Map sort col to table prefix
    if sort_col in ('service_category', 'actual_subject', 'penalty_asymmetry',
                     'auto_renewal', 'bezodplatne', 'funding_type', 'grant_amount',
                     'hidden_entity_count', 'penalty_count', 'iban_count'):
        sort_expr = f"e.{sort_col}"
    elif sort_col == 'flag_count':
        sort_expr = "rf.flag_count"
    elif sort_col == 'dodavatel_tax_status':
        sort_expr = "tr.status"
    else:
        sort_expr = f"z.{sort_col}"

    # Pagination
    limit = min(int(params.get('limit', 100)), 10000)
    offset = int(params.get('offset', 0))

    # Count
    count_row = db.execute(
        f"SELECT count(*) FROM zmluvy z {join} WHERE {where}", bindings
    ).fetchone()
    total = count_row[0]

    # Data
    rows = db.execute(
        f"""SELECT z.*,
            e.service_category, e.actual_subject, e.penalty_asymmetry,
            e.auto_renewal, e.bezodplatne, e.funding_type, e.grant_amount,
            e.hidden_entity_count, e.penalty_count, e.iban_count,
            e.extraction_json,
            COALESCE(rf.flag_count, 0) as flag_count,
            rf.flag_labels,
            tr.status as dodavatel_tax_status
        FROM zmluvy z {join}
        WHERE {where}
        ORDER BY {sort_expr} {sort_dir}
        LIMIT ? OFFSET ?""",
        bindings + [limit, offset],
    ).fetchall()

    result_rows = [dict(r) for r in rows]
    # Extract signatories as flat string, then remove extraction_json (too large)
    for r in result_rows:
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

    # CSV export
    if params.get('format') == 'csv':
        return _browse_csv(result_rows)

    return {"rows": result_rows, "total": total}


def _browse_csv(rows):
    """Return CSV string for export."""
    if not rows:
        return {"csv": ""}
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return {"__csv__": output.getvalue()}


def api_browse_filters(db, params):
    """Return filter options for the browse page."""
    rezorty = db.execute(
        "SELECT DISTINCT rezort_id, rezort FROM zmluvy WHERE rezort != '' ORDER BY rezort"
    ).fetchall()
    categories = db.execute(
        "SELECT DISTINCT service_category FROM extractions WHERE service_category IS NOT NULL ORDER BY service_category"
    ).fetchall()
    funding = db.execute(
        "SELECT DISTINCT funding_type FROM extractions WHERE funding_type IS NOT NULL AND funding_type != '' ORDER BY funding_type"
    ).fetchall()
    flags = db.execute(
        "SELECT id, label FROM flag_rules WHERE enabled = 1 ORDER BY label"
    ).fetchall()
    return {
        "rezorty": [{"id": r["rezort_id"], "nazov": r["rezort"]} for r in rezorty],
        "categories": [r["service_category"] for r in categories],
        "funding_types": [r["funding_type"] for r in funding],
        "flag_rules": [{"id": r["id"], "label": r["label"]} for r in flags],
    }


API_ROUTES = {
    "/api/filters": api_filters,
    "/api/summary": api_summary,
    "/api/timeline": api_timeline,
    "/api/by_rezort": api_by_rezort,
    "/api/by_category": api_by_category,
    "/api/penalties": api_penalties,
    "/api/top_contracts": api_top_contracts,
    "/api/anomalies": api_anomalies,
    "/api/detail": api_detail,
    "/api/flags": api_flags,
    "/api/flags_by_rezort": api_flags_by_rezort,
    "/api/flags_top": api_flags_top,
    "/api/flags_timeline": api_flags_timeline,
    "/api/investigation_categories": api_investigation_categories,
    "/api/contracts": api_contracts,
    "/api/browse": api_browse,
    "/api/browse_filters": api_browse_filters,
}


# ---------------------------------------------------------------------------
# ASGI helpers
# ---------------------------------------------------------------------------

async def send_response(send, status, content_type, body):
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            [b"content-type", content_type.encode()],
            [b"cache-control", b"no-cache"],
        ],
    })
    await send({"type": "http.response.body", "body": body})


async def handle_dashboard(scope, receive, send):
    body = DASHBOARD_HTML_PATH.read_bytes()
    await send_response(send, 200, "text/html; charset=utf-8", body)


async def handle_browse(scope, receive, send):
    body = DASHBOARD_HTML_PATH.read_bytes()
    await send_response(send, 200, "text/html; charset=utf-8", body)


async def handle_detail(scope, receive, send):
    body = DETAIL_HTML_PATH.read_bytes()
    await send_response(send, 200, "text/html; charset=utf-8", body)


async def handle_api(path, scope, receive, send):
    qs = parse_qs(scope.get("query_string", b"").decode())
    params = {k: v[0] for k, v in qs.items()}
    handler = API_ROUTES[path]
    db = get_db()
    try:
        result = handler(db, params)
        # CSV export support
        if isinstance(result, dict) and "__csv__" in result:
            body = result["__csv__"].encode("utf-8-sig")
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"text/csv; charset=utf-8"],
                    [b"content-disposition", b"attachment; filename=crz_export.csv"],
                ],
            })
            await send({"type": "http.response.body", "body": body})
        else:
            body = json.dumps(result, ensure_ascii=False).encode()
            await send_response(send, 200, "application/json; charset=utf-8", body)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Combined ASGI application
# ---------------------------------------------------------------------------

class CRZApp:
    """Mounts dashboard at / and datasette at /data."""

    def __init__(self, datasette_app):
        self.datasette = datasette_app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.datasette(scope, receive, send)
            return

        path = scope["path"]

        # Dashboard HTML
        if path == "/" or path == "/dashboard":
            await handle_dashboard(scope, receive, send)
            return

        # Browse page
        if path == "/browse":
            await handle_browse(scope, receive, send)
            return

        # Detail page — /browse/{id}
        if path.startswith("/browse/") and len(path.split("/")) == 3:
            await handle_detail(scope, receive, send)
            return

        # Dashboard API
        if path in API_ROUTES:
            await handle_api(path, scope, receive, send)
            return

        # Datasette — strip /data prefix so datasette sees root paths
        if path.startswith("/data"):
            scope = dict(scope)
            scope["path"] = path[5:] or "/"
            raw_path = scope.get("raw_path", b"")
            if raw_path:
                scope["raw_path"] = raw_path[5:] or b"/"
            await self.datasette(scope, receive, send)
            return

        # Fallback: try datasette for its static assets (/-/static/...)
        await self.datasette(scope, receive, send)


def create_app():
    with open(ROOT / "metadata.yaml") as f:
        metadata = yaml.safe_load(f)
    ds = Datasette(
        files=[DB_PATH],
        metadata=metadata,
        settings={"base_url": "/data/"},
    )
    return CRZApp(ds.app())


def main():
    parser = argparse.ArgumentParser(description="CRZ Server (dashboard + datasette)")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    import uvicorn
    app = create_app()
    print(f"CRZ Server: http://{args.host}:{args.port}")
    print(f"  Dashboard:  http://{args.host}:{args.port}/")
    print(f"  Datasette:  http://{args.host}:{args.port}/data")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
