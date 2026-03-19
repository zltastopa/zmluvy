"""Evaluate žltá stopa rules against contracts and materialize results.

Usage:
    uv run python flag_contracts.py                # run all enabled rules
    uv run python flag_contracts.py --rule hidden_entities  # run one rule
    uv run python flag_contracts.py --init          # seed default rules only
    uv run python flag_contracts.py --list          # show all rules
    uv run python flag_contracts.py --add           # add a new rule interactively
"""

import confpath  # noqa: F401

import argparse
import json
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timedelta

from settings import get_path, normalize_company_name

DB_PATH = get_path("CRZ_DB_PATH", "crz.db")

# -----------------------------------------------------------------------
# Default flag rules — each is a SQL WHERE clause against zmluvy z
# with optional LEFT JOIN to extractions e.
#
# To add a new rule, append to this list or use --add / direct SQL INSERT.
# The sql_condition is a WHERE fragment — it can reference:
#   z.*          (zmluvy columns)
#   e.*          (extractions columns, LEFT JOINed)
#   p.*          (prilohy columns, LEFT JOINed, grouped)
# -----------------------------------------------------------------------

DEFAULT_RULES = [
    {
        "id": "hidden_entities",
        "label": "Skryte entity",
        "description": "Zmluva obsahuje tretie strany okrem hlavnych zmluvnych stran",
        "severity": "warning",
        "sql_condition": "e.hidden_entity_count > 0",
        "needs_extraction": 1,
    },
    {
        "id": "hidden_price",
        "label": "Skryta cena",
        "description": "Zmluva nema uvedenu sumu (suma je NULL)",
        "severity": "warning",
        "sql_condition": "z.suma IS NULL",
        "needs_extraction": 0,
    },
    {
        "id": "missing_expiry",
        "label": "Neuvedena platnost",
        "description": "Zmluva nad 10 000 EUR nema uvedeny datum platnosti (vynimka pre najom, cintorin, vecne bremena, prevod majetku)",
        "severity": "info",
        "sql_condition": "(z.platnost_do IS NULL OR z.platnost_do = '') AND z.suma > 10000 AND (e.service_category IS NULL OR e.service_category NOT IN ('property_lease', 'cemetery', 'easement_encumbrance', 'asset_transfer', 'copyright_royalty'))",
        "needs_extraction": 0,
    },
    {
        "id": "bezodplatne",
        "label": "Bezodplatna zmluva",
        "description": "Zmluva je bezodplatna (bez financnej odplaty)",
        "severity": "warning",
        "sql_condition": "e.bezodplatne = 1",
        "needs_extraction": 1,
    },
    {
        "id": "supplier_advantage",
        "label": "Pokuty zvyhodnuju dodavatela",
        "description": "Zmluvne pokuty su nastavene v prospech dodavatela (neobvykle v statnych zmluvach)",
        "severity": "danger",
        "sql_condition": "e.penalty_asymmetry = 'supplier_advantage'",
        "needs_extraction": 1,
    },
    {
        "id": "missing_ico",
        "label": "Dodavatel bez ICO",
        "description": "Dodavatel nema uvedene ICO (identifikacne cislo organizacie)",
        "severity": "info",
        "sql_condition": "z.dodavatel_ico IS NULL OR z.dodavatel_ico = ''",
        "needs_extraction": 0,
    },
    {
        "id": "tax_unreliable",
        "label": "Danovo nespolahlivy dodavatel",
        "description": "Dodavatel ma status 'menej spolahlivy' podla Financnej spravy SR",
        "severity": "danger",
        "sql_condition": "z.dodavatel_ico IN (SELECT ico FROM tax_reliability WHERE status = 'menej spoľahlivý')",
        "needs_extraction": 0,
    },
    {
        "id": "tax_unreliable_entity",
        "label": "Danovo nespolahlivy subjekt v zmluve",
        "description": "Zmluva obsahuje tretiu stranu (skrytu entitu) s ICO, ktora je 'menej spolahlivy' podla Financnej spravy SR",
        "severity": "danger",
        "sql_condition": "__custom__",
        "needs_extraction": 1,
    },
    {
        "id": "vszp_debtor",
        "label": "Dlznik VSZP",
        "description": "Dodavatel je dlznik Vseobecnej zdravotnej poistovne (podla ICO)",
        "severity": "danger",
        "sql_condition": "z.dodavatel_ico IN (SELECT cin FROM vszp_debtors WHERE cin IS NOT NULL)",
        "needs_extraction": 0,
    },
    {
        "id": "socpoist_debtor",
        "label": "Dlznik Socialnej poistovne",
        "description": "Dodavatel je dlznik Socialnej poistovne (podla nazvu firmy)",
        "severity": "danger",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    {
        "id": "vszp_debtor_entity",
        "label": "Skryta entita dlznik VSZP",
        "description": "Zmluva obsahuje skrytu entitu ktora je dlznikom VSZP (podla ICO)",
        "severity": "danger",
        "sql_condition": "__custom__",
        "needs_extraction": 1,
    },
    {
        "id": "terminated_company",
        "label": "Zrusena firma",
        "description": "Dodavatel je zruseny/zaniknuty podla registra uctovnych zavierok (RUZ)",
        "severity": "danger",
        "sql_condition": "z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != '' AND z.dodavatel_ico IN (SELECT cin FROM ruz_entities WHERE terminated_on IS NOT NULL AND cin IS NOT NULL) AND z.dodavatel_ico NOT IN (SELECT cin FROM ruz_entities WHERE terminated_on IS NULL AND cin IS NOT NULL)",
        "needs_extraction": 0,
    },
    {
        "id": "not_in_ruz",
        "label": "Dodavatel nie je v RUZ",
        "description": "Dodavatel s ICO nie je evidovany v registri uctovnych zavierok",
        "severity": "info",
        "sql_condition": "z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != '' AND length(z.dodavatel_ico) = 8 AND z.dodavatel_ico NOT LIKE '00%' AND z.dodavatel_ico NOT IN (SELECT cin FROM ruz_entities WHERE cin IS NOT NULL)",
        "needs_extraction": 0,
    },
    {
        "id": "micro_supplier_large_contract",
        "label": "Mikro dodavatel, velka zmluva",
        "description": "Dodavatel ma 0-1 zamestnancov podla RUZ, ale zmluva presahuje 100 000 EUR",
        "severity": "warning",
        "sql_condition": "z.suma > 100000 AND z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != '' AND z.dodavatel_ico IN (SELECT cin FROM ruz_entities WHERE organization_size_id IN (1, 2) AND cin IS NOT NULL AND terminated_on IS NULL)",
        "needs_extraction": 0,
    },
    {
        "id": "fresh_company",
        "label": "Cerstve zalozena firma",
        "description": "Dodavatel bol zalozeny menej ako 1 rok pred podpisom zmluvy",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    # --- New flags: contract patterns ---
    {
        "id": "weekend_signing",
        "label": "Podpis cez vikend",
        "description": "Zmluva nad 50 000 EUR bola podpisana v sobotu alebo nedelu (vynimka 1. a posledny den mesiaca)",
        "severity": "info",
        "sql_condition": "z.datum_podpisu IS NOT NULL AND z.datum_podpisu != '' AND cast(strftime('%w', z.datum_podpisu) as integer) IN (0, 6) AND z.suma > 50000 AND cast(strftime('%d', z.datum_podpisu) as integer) NOT IN (1, 28, 29, 30, 31)",
        "needs_extraction": 0,
    },
    {
        "id": "missing_attachment",
        "label": "Chybajuca priloha",
        "description": "Zmluva nema ziadnu prilohu — dokument zmluvy nebol zverejneny",
        "severity": "warning",
        "sql_condition": "z.id NOT IN (SELECT zmluva_id FROM prilohy)",
        "needs_extraction": 0,
    },
    {
        "id": "dodatok_price_inflation",
        "label": "Navysenie ceny dodatkami",
        "description": "Celkova suma zmluvy je o viac ako 50% vyssia nez povodna suma a navysenie presahuje 50 000 EUR",
        "severity": "warning",
        "sql_condition": "z.suma_celkom IS NOT NULL AND z.suma IS NOT NULL AND z.suma > 0 AND z.suma_celkom > z.suma * 1.5 AND (z.suma_celkom - z.suma) > 50000",
        "needs_extraction": 0,
    },
    {
        "id": "contract_splitting",
        "label": "Delenie zakazky",
        "description": "Dodavatel ma 5+ zmluv pod 15 000 EUR s rovnakym objednavatelom za rok, spolu nad 15 000 EUR",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    {
        "id": "supplier_monopoly",
        "label": "Monopolny dodavatel",
        "description": "Dodavatel ma 10+ zmluv s rovnakym objednavatelom",
        "severity": "info",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    {
        "id": "rapid_succession",
        "label": "Zmluvy v rychlom slede",
        "description": "Dodavatel dostal 3+ zmluvy od rovnakeho objednavatela v priebehu 14 dni",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    # --- New flags: RUZ cross-references ---
    {
        "id": "foreign_supplier",
        "label": "Zahranicny dodavatel",
        "description": "Dodavatel je registrovany v zahranici podla registra uctovnych zavierok (RUZ)",
        "severity": "info",
        "sql_condition": "z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != '' AND z.dodavatel_ico IN (SELECT cin FROM ruz_entities WHERE region = 'Zahraničie' AND cin IS NOT NULL)",
        "needs_extraction": 0,
    },
    {
        "id": "nonprofit_large_contract",
        "label": "Neziskovka s velkou zmluvou",
        "description": "Dodavatel je neziskova organizacia, nadacia alebo fond s zmluvou nad 100 000 EUR",
        "severity": "warning",
        "sql_condition": "z.suma > 100000 AND z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != '' AND z.dodavatel_ico IN (SELECT cin FROM ruz_entities WHERE legal_form_id IN (117, 118, 119) AND cin IS NOT NULL)",
        "needs_extraction": 0,
    },
    {
        "id": "nace_mismatch",
        "label": "Nesulad odvetvia",
        "description": "Registrovane odvetvie dodavatela (NACE) nezodpoveda predmetu zmluvy",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 1,
    },
    # --- New flags: extraction cross-references ---
    {
        "id": "signatory_overlap",
        "label": "Zdielany podpisujuci",
        "description": "Osoba podpisujuca zmluvu za dodavatela sa nachadza aj v zmluvach inych dodavatelov (10+ firmy)",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 1,
    },
    {
        "id": "hidden_entity_is_supplier",
        "label": "Skryta entita je dodavatel",
        "description": "Skryta entita v zmluve (ICO) je zaroven dodavatelom v inych zmluvach",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 1,
    },
    {
        "id": "excessive_penalties",
        "label": "Nadmerny pocet pokut",
        "description": "Zmluva obsahuje neobvykle vysoky pocet zmluvnych pokut (viac ako 5)",
        "severity": "info",
        "sql_condition": "e.penalty_count > 5",
        "needs_extraction": 1,
    },
    {
        "id": "amount_outlier",
        "label": "Neobvykle vysoka suma",
        "description": "Suma zmluvy je viac ako 3 standardne odchylky nad priemerom pre danu kategoriu sluzieb",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 1,
    },
    # --- New flags: statistical / dormancy ---
    {
        "id": "dormant_then_active",
        "label": "Spaca firma",
        "description": "Dodavatel nemal ziadnu zmluvu 2+ roky a naraz dostal velku zakazku (nad 50 000 EUR)",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    # --- New flags: multi-source combinations ---
    {
        "id": "fresh_micro_large",
        "label": "Nova mikro firma, velka zmluva",
        "description": "Dodavatel bol zalozeny menej ako 1 rok pred podpisom, ma 0-1 zamestnancov a zmluva je nad 50 000 EUR",
        "severity": "danger",
        "sql_condition": "z.suma > 50000 AND z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = 'fresh_company') AND z.dodavatel_ico IN (SELECT cin FROM ruz_entities WHERE organization_size_id IN (1, 2) AND cin IS NOT NULL AND terminated_on IS NULL)",
        "needs_extraction": 0,
    },
    {
        "id": "high_subcontracting",
        "label": "Vysoka miera subdodavok",
        "description": "Maximalny podiel subdodavatela je 80% a viac — dodavatel vykonava len malu cast zakazky sam",
        "severity": "warning",
        "sql_condition": "CAST(e.subcontractor_max_percentage AS REAL) >= 80",
        "needs_extraction": 1,
    },
    {
        "id": "threshold_gaming",
        "label": "Tesne pod limitom EU sutaze",
        "description": "Suma zmluvy je tesne pod hranicou 215 000 EUR pre povinnu EU sutaz (210-215K banda), co moze naznacovat umyselne vyhybanie sa transparentnejsiemu obstaravaniu",
        "severity": "warning",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    # --- New flags: Finančná správa open data ---
    {
        "id": "fs_tax_debtor",
        "label": "Danovy dlznik FS",
        "description": "Dodavatel je na zozname danovych dlznikov Financnej spravy SR (podla nazvu firmy)",
        "severity": "danger",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    {
        "id": "fs_vat_deregistered",
        "label": "Vymazany z DPH registra",
        "description": "Dodavatel bol vymazany zo zoznamu platitelov DPH (podla ICO)",
        "severity": "danger",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    {
        "id": "fs_vat_dereg_risk",
        "label": "Dovody na zrusenie DPH",
        "description": "U dodavatela nastali dovody na zrusenie registracie pre DPH (podla ICO)",
        "severity": "danger",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
    {
        "id": "negative_equity",
        "label": "Zaporne vlastne imanie",
        "description": "Dodavatel vykazuje zaporne vlastne imanie v poslednej uctovnej zavierke (podla RUZ)",
        "severity": "danger",
        "sql_condition": "__custom__",
        "needs_extraction": 0,
    },
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_tables(db):
    """Create flag_rules and red_flags tables if they don't exist."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS flag_rules (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            description TEXT,
            severity TEXT NOT NULL DEFAULT 'warning',
            sql_condition TEXT NOT NULL,
            needs_extraction INTEGER NOT NULL DEFAULT 0,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS red_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zmluva_id INTEGER NOT NULL REFERENCES zmluvy(id),
            flag_type TEXT NOT NULL REFERENCES flag_rules(id),
            detail TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(zmluva_id, flag_type)
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_red_flags_zmluva ON red_flags(zmluva_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_red_flags_type ON red_flags(flag_type)")
    db.commit()


def seed_rules(db):
    """Insert or update default rules."""
    for rule in DEFAULT_RULES:
        db.execute(
            """INSERT INTO flag_rules
               (id, label, description, severity, sql_condition, needs_extraction)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                   label=excluded.label,
                   description=excluded.description,
                   severity=excluded.severity,
                   sql_condition=excluded.sql_condition,
                   needs_extraction=excluded.needs_extraction""",
            (rule["id"], rule["label"], rule["description"],
             rule["severity"], rule["sql_condition"], rule["needs_extraction"]),
        )
    db.commit()


def evaluate_rule(db, rule):
    """Run a single flag rule and insert matching contracts into red_flags."""
    rule_id = rule["id"]
    condition = rule["sql_condition"]
    needs_ext = rule["needs_extraction"]

    # Custom evaluation for rules that can't be expressed as pure SQL
    if condition == "__custom__":
        return evaluate_custom_rule(db, rule)

    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id" if needs_ext else ""

    # Find contracts matching this rule that don't already have this flag
    query = f"""
        INSERT OR IGNORE INTO red_flags (zmluva_id, flag_type)
        SELECT z.id, ?
        FROM zmluvy z {join}
        WHERE {condition}
    """

    cursor = db.execute(query, (rule_id,))
    inserted = cursor.rowcount

    # Also remove flags for contracts that no longer match
    remove_query = f"""
        DELETE FROM red_flags
        WHERE flag_type = ?
        AND zmluva_id NOT IN (
            SELECT z.id FROM zmluvy z {join} WHERE {condition}
        )
    """
    cursor2 = db.execute(remove_query, (rule_id,))
    removed = cursor2.rowcount

    return inserted, removed


def _insert_remove_flags(db, flag_type, matching_ids, details=None):
    """Insert new flags and remove stale ones. Returns (inserted, removed)."""
    inserted = 0
    for zmluva_id in matching_ids:
        detail = details.get(zmluva_id) if details else None
        cursor = db.execute(
            "INSERT OR IGNORE INTO red_flags (zmluva_id, flag_type, detail) VALUES (?, ?, ?)",
            (zmluva_id, flag_type, detail),
        )
        inserted += cursor.rowcount
        # Update detail if it was NULL (from a previous SQL-based evaluator)
        if cursor.rowcount == 0 and detail:
            db.execute(
                "UPDATE red_flags SET detail = ? WHERE zmluva_id = ? AND flag_type = ? AND detail IS NULL",
                (detail, zmluva_id, flag_type),
            )
    placeholder = ",".join(str(i) for i in matching_ids) if matching_ids else "0"
    cursor2 = db.execute(
        f"DELETE FROM red_flags WHERE flag_type = ? AND zmluva_id NOT IN ({placeholder})",
        (flag_type,),
    )
    return inserted, cursor2.rowcount


_CUSTOM_EVALUATORS = {}


def _custom(rule_id):
    """Decorator to register a custom evaluator."""
    def decorator(fn):
        _CUSTOM_EVALUATORS[rule_id] = fn
        return fn
    return decorator


def evaluate_custom_rule(db, rule):
    """Evaluate custom rules that require Python logic."""
    fn = _CUSTOM_EVALUATORS.get(rule["id"])
    if fn:
        return fn(db)
    raise ValueError(f"Unknown custom rule: {rule['id']}")


def _get_hidden_entities(db):
    """Load all extractions with hidden entities, parsed. Cached-style helper."""
    rows = db.execute("""
        SELECT e.zmluva_id, e.extraction_json
        FROM extractions e
        WHERE e.hidden_entity_count > 0 AND e.extraction_json IS NOT NULL
    """).fetchall()
    results = []
    for row in rows:
        try:
            ej = json.loads(row["extraction_json"])
        except Exception:
            continue
        for he in (ej.get("hidden_entities") or []):
            ico = (he.get("ico") or "").strip()
            results.append((row["zmluva_id"], he.get("name", ""), ico))
    return results


def _parse_date(s):
    """Parse a date string, return datetime or None."""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


# -----------------------------------------------------------------------
# Custom evaluators — registered via @_custom decorator
# -----------------------------------------------------------------------

@_custom("tax_unreliable_entity")
def _eval_tax_unreliable_entity(db):
    unreliable = set(
        r[0] for r in db.execute(
            "SELECT ico FROM tax_reliability WHERE status = 'menej spoľahlivý'"
        ).fetchall()
    )
    matching_ids = set()
    details = {}
    for zmluva_id, name, ico in _get_hidden_entities(db):
        if ico and ico in unreliable:
            matching_ids.add(zmluva_id)
            details[zmluva_id] = f"{name or ico} (ICO: {ico})"
    return _insert_remove_flags(db, "tax_unreliable_entity", matching_ids, details)


@_custom("socpoist_debtor")
def _eval_socpoist_debtor(db):
    socpoist_rows = db.execute(
        "SELECT name_normalized, name, amount FROM socpoist_debtors WHERE name_normalized IS NOT NULL"
    ).fetchall()
    socpoist_map = {}
    for r in socpoist_rows:
        key = r["name_normalized"]
        if key not in socpoist_map or r["amount"] > socpoist_map[key][1]:
            socpoist_map[key] = (r["name"], r["amount"])

    contracts = db.execute(
        "SELECT id, dodavatel FROM zmluvy WHERE dodavatel IS NOT NULL AND dodavatel != ''"
    ).fetchall()

    matching_ids = set()
    details = {}
    for c in contracts:
        norm = normalize_company_name(c["dodavatel"])
        if norm in socpoist_map:
            matching_ids.add(c["id"])
            orig_name, amount = socpoist_map[norm]
            details[c["id"]] = f"{orig_name} (dlh: {amount:,.2f} EUR)"
    return _insert_remove_flags(db, "socpoist_debtor", matching_ids, details)


@_custom("vszp_debtor_entity")
def _eval_vszp_debtor_entity(db):
    vszp_cins = {}
    for r in db.execute("SELECT cin, name, amount FROM vszp_debtors WHERE cin IS NOT NULL").fetchall():
        cin = r["cin"].strip()
        if cin and (cin not in vszp_cins or r["amount"] > vszp_cins[cin][1]):
            vszp_cins[cin] = (r["name"], r["amount"])

    matching_ids = set()
    details = {}
    for zmluva_id, name, ico in _get_hidden_entities(db):
        if ico and ico in vszp_cins:
            matching_ids.add(zmluva_id)
            vname, amount = vszp_cins[ico]
            details[zmluva_id] = f"{name or vname} (ICO: {ico}, dlh VSZP: {amount:,.2f} EUR)"
    return _insert_remove_flags(db, "vszp_debtor_entity", matching_ids, details)


@_custom("fresh_company")
def _eval_fresh_company(db):
    ruz_rows = db.execute(
        "SELECT cin, established_on, name FROM ruz_entities WHERE cin IS NOT NULL AND established_on IS NOT NULL AND terminated_on IS NULL"
    ).fetchall()
    ruz_map = {}
    for r in ruz_rows:
        est = _parse_date(r["established_on"])
        if est and (r["cin"] not in ruz_map or est < ruz_map[r["cin"]][0]):
            ruz_map[r["cin"]] = (est, r["name"])

    contracts = db.execute("""
        SELECT id, dodavatel_ico, datum_podpisu, datum_zverejnenia
        FROM zmluvy WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != '' AND length(dodavatel_ico) = 8
    """).fetchall()

    matching_ids = set()
    details = {}
    for c in contracts:
        ico = c["dodavatel_ico"]
        if ico not in ruz_map:
            continue
        est_date, company_name = ruz_map[ico]
        contract_date = _parse_date(c["datum_podpisu"] or c["datum_zverejnenia"])
        if not contract_date:
            continue
        days_diff = (contract_date - est_date).days
        if 0 <= days_diff < 365:
            matching_ids.add(c["id"])
            details[c["id"]] = f"{company_name} (zalozena {est_date.strftime('%d.%m.%Y')}, {days_diff // 30} mes. pred zmluvou)"
    return _insert_remove_flags(db, "fresh_company", matching_ids, details)


@_custom("contract_splitting")
def _eval_contract_splitting(db):
    """Flag contracts that appear to be split to avoid procurement thresholds."""
    rows = db.execute("""
        SELECT id, dodavatel_ico, objednavatel_ico, suma, datum_podpisu, datum_zverejnenia
        FROM zmluvy
        WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''
        AND objednavatel_ico IS NOT NULL AND objednavatel_ico != ''
        AND suma IS NOT NULL AND suma > 0 AND suma < 15000
        AND typ = 'zmluva'
    """).fetchall()

    # Group by (dodavatel_ico, objednavatel_ico, year)
    groups = defaultdict(list)
    for r in rows:
        date_str = r["datum_podpisu"] or r["datum_zverejnenia"] or ""
        year = date_str[:4] if len(date_str) >= 4 else "0000"
        groups[(r["dodavatel_ico"], r["objednavatel_ico"], year)].append(
            (r["id"], r["suma"])
        )

    matching_ids = set()
    details = {}
    for (dod, obj, year), contracts in groups.items():
        if len(contracts) >= 5:
            total = sum(c[1] for c in contracts)
            if total > 15000:
                for cid, _ in contracts:
                    matching_ids.add(cid)
                    details[cid] = f"{len(contracts)} zmluv za {total:,.0f} EUR v {year} (ICO dod: {dod}, obj: {obj})"
    return _insert_remove_flags(db, "contract_splitting", matching_ids, details)


@_custom("supplier_monopoly")
def _eval_supplier_monopoly(db):
    """Flag contracts where supplier has 10+ contracts with same buyer."""
    rows = db.execute("""
        SELECT dodavatel_ico, objednavatel_ico, count(*) as cnt, group_concat(id) as ids
        FROM zmluvy
        WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''
        AND objednavatel_ico IS NOT NULL AND objednavatel_ico != ''
        GROUP BY dodavatel_ico, objednavatel_ico
        HAVING count(*) >= 10
    """).fetchall()

    matching_ids = set()
    details = {}
    for r in rows:
        for cid_str in r["ids"].split(","):
            cid = int(cid_str)
            matching_ids.add(cid)
            details[cid] = f"{r['cnt']} zmluv medzi ICO {r['dodavatel_ico']} a {r['objednavatel_ico']}"
    return _insert_remove_flags(db, "supplier_monopoly", matching_ids, details)


@_custom("rapid_succession")
def _eval_rapid_succession(db):
    """Flag contracts where same supplier+buyer have 3+ contracts within 14 days."""
    rows = db.execute("""
        SELECT id, dodavatel_ico, objednavatel_ico, datum_podpisu, datum_zverejnenia
        FROM zmluvy
        WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''
        AND objednavatel_ico IS NOT NULL AND objednavatel_ico != ''
        ORDER BY dodavatel_ico, objednavatel_ico, datum_podpisu
    """).fetchall()

    # Group by pair
    groups = defaultdict(list)
    for r in rows:
        dt = _parse_date(r["datum_podpisu"] or r["datum_zverejnenia"])
        if dt:
            groups[(r["dodavatel_ico"], r["objednavatel_ico"])].append((r["id"], dt))

    matching_ids = set()
    details = {}
    for (dod, obj), contracts in groups.items():
        contracts.sort(key=lambda x: x[1])
        # Sliding window: find clusters of 3+ within 14 days
        for i in range(len(contracts)):
            cluster = [contracts[i]]
            for j in range(i + 1, len(contracts)):
                if (contracts[j][1] - contracts[i][1]).days <= 14:
                    cluster.append(contracts[j])
                else:
                    break
            if len(cluster) >= 3:
                for cid, dt in cluster:
                    matching_ids.add(cid)
                    details[cid] = f"{len(cluster)} zmluv za 14 dni (ICO dod: {dod}, obj: {obj})"
    return _insert_remove_flags(db, "rapid_succession", matching_ids, details)


# NACE sector -> compatible service categories
_NACE_COMPATIBLE = {
    'software_it': {58, 59, 60, 61, 62, 63, 70, 71, 72, 74},
    'construction_renovation': {41, 42, 43, 71},
    'legal_services': {69},
    'media_marketing': {58, 59, 60, 63, 70, 73, 74, 90},
    'insurance': {65, 66},
    'transport': {49, 50, 51, 52, 53},
    'transportation': {49, 50, 51, 52, 53},
    'cleaning_facility': {81, 82},
    'pharmaceutical_clinical': {21, 46, 72, 86},
    'property_lease': {68, 77},
    'professional_consulting': {69, 70, 71, 72, 73, 74, 78, 82},
    'waste_management': {38, 39},
    'utilities': {35, 36},
    'hr_payroll_outsourcing': {69, 70, 78, 82},
    'accommodation': {55, 56},
    'vehicle_use': {45, 49, 77},
}


@_custom("nace_mismatch")
def _eval_nace_mismatch(db):
    """Flag contracts where supplier NACE sector doesn't match service category."""
    rows = db.execute("""
        SELECT z.id, z.dodavatel_ico, e.service_category, r.nace_code, r.nace_category
        FROM zmluvy z
        JOIN extractions e ON e.zmluva_id = z.id
        JOIN ruz_entities r ON r.cin = z.dodavatel_ico
        WHERE e.service_category IS NOT NULL AND e.service_category != 'other'
        AND r.nace_code IS NOT NULL AND r.nace_code != ''
        AND z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
    """).fetchall()

    matching_ids = set()
    details = {}
    for r in rows:
        cat = r["service_category"]
        if cat not in _NACE_COMPATIBLE:
            continue  # Skip categories we don't have a mapping for
        try:
            nace_sector = int(r["nace_code"][:2])
        except (ValueError, TypeError):
            continue
        if nace_sector not in _NACE_COMPATIBLE[cat]:
            matching_ids.add(r["id"])
            details[r["id"]] = f"NACE: {r['nace_category']} ({r['nace_code']}), zmluva: {cat}"
    return _insert_remove_flags(db, "nace_mismatch", matching_ids, details)


@_custom("signatory_overlap")
def _eval_signatory_overlap(db):
    """Flag contracts where a signatory signs for 10+ different supplier ICOs."""
    rows = db.execute("""
        SELECT e.zmluva_id, e.extraction_json, z.dodavatel_ico
        FROM extractions e
        JOIN zmluvy z ON z.id = e.zmluva_id
        WHERE e.extraction_json IS NOT NULL
        AND z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
    """).fetchall()

    # Build: signatory_name -> set of (dodavatel_ico, zmluva_id)
    sig_map = defaultdict(set)
    sig_contracts = defaultdict(set)
    for r in rows:
        try:
            ej = json.loads(r["extraction_json"])
        except Exception:
            continue
        for sig in (ej.get("signatories") or []):
            name = (sig.get("name") or "").strip().lower()
            if name and len(name) > 5:  # Skip very short names
                sig_map[name].add(r["dodavatel_ico"])
                sig_contracts[name].add(r["zmluva_id"])

    # Find signatories appearing with 10+ different supplier ICOs
    suspicious_sigs = {name: icos for name, icos in sig_map.items() if len(icos) >= 10}

    matching_ids = set()
    details = {}
    for name, icos in suspicious_sigs.items():
        for zmluva_id in sig_contracts[name]:
            matching_ids.add(zmluva_id)
            details[zmluva_id] = f"{name.title()} podpisuje za {len(icos)} roznych dodavatelov"
    return _insert_remove_flags(db, "signatory_overlap", matching_ids, details)


@_custom("hidden_entity_is_supplier")
def _eval_hidden_entity_is_supplier(db):
    """Flag contracts where a hidden entity ICO is also a dodavatel in other contracts."""
    all_dodavatel_icos = set(
        r[0] for r in db.execute(
            "SELECT DISTINCT dodavatel_ico FROM zmluvy WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''"
        ).fetchall()
    )

    matching_ids = set()
    details = {}
    for zmluva_id, name, ico in _get_hidden_entities(db):
        if ico and ico in all_dodavatel_icos:
            matching_ids.add(zmluva_id)
            details[zmluva_id] = f"{name or ico} (ICO: {ico}) je tiez dodavatel v inych zmluvach"
    return _insert_remove_flags(db, "hidden_entity_is_supplier", matching_ids, details)


@_custom("amount_outlier")
def _eval_amount_outlier(db):
    """Flag contracts where suma is >3 std deviations above mean for the service category."""
    # Compute stats per category
    stats = db.execute("""
        SELECT e.service_category, avg(z.suma) as mean, avg(z.suma * z.suma) as mean_sq, count(*) as cnt
        FROM zmluvy z JOIN extractions e ON e.zmluva_id = z.id
        WHERE z.suma IS NOT NULL AND z.suma > 0 AND e.service_category IS NOT NULL
        GROUP BY e.service_category HAVING count(*) >= 10
    """).fetchall()

    # stddev = sqrt(mean_sq - mean^2)
    import math
    thresholds = {}
    for r in stats:
        mean = r["mean"]
        variance = r["mean_sq"] - mean * mean
        stddev = math.sqrt(max(variance, 0))
        threshold = mean + 3 * stddev
        if threshold > 0:
            thresholds[r["service_category"]] = (threshold, mean, stddev)

    rows = db.execute("""
        SELECT z.id, z.suma, e.service_category
        FROM zmluvy z JOIN extractions e ON e.zmluva_id = z.id
        WHERE z.suma IS NOT NULL AND z.suma > 0 AND e.service_category IS NOT NULL
    """).fetchall()

    matching_ids = set()
    details = {}
    for r in rows:
        cat = r["service_category"]
        if cat in thresholds and r["suma"] > thresholds[cat][0]:
            matching_ids.add(r["id"])
            mean, stddev = thresholds[cat][1], thresholds[cat][2]
            n_sigma = (r["suma"] - mean) / stddev if stddev > 0 else 0
            details[r["id"]] = f"{r['suma']:,.0f} EUR ({n_sigma:.1f}x stddev pre {cat}, priemer: {mean:,.0f} EUR)"
    return _insert_remove_flags(db, "amount_outlier", matching_ids, details)


@_custom("dormant_then_active")
def _eval_dormant_then_active(db):
    """Flag contracts where supplier had no contracts for 2+ years then got a big one."""
    rows = db.execute("""
        SELECT id, dodavatel_ico, datum_podpisu, datum_zverejnenia, suma
        FROM zmluvy
        WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''
        AND suma IS NOT NULL AND suma > 50000
        ORDER BY dodavatel_ico, datum_zverejnenia
    """).fetchall()

    # Also get all contract dates per supplier
    all_contracts = db.execute("""
        SELECT dodavatel_ico, datum_podpisu, datum_zverejnenia
        FROM zmluvy
        WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''
        ORDER BY dodavatel_ico, datum_zverejnenia
    """).fetchall()

    # Build: ico -> sorted list of dates
    ico_dates = defaultdict(list)
    for r in all_contracts:
        dt = _parse_date(r["datum_podpisu"] or r["datum_zverejnenia"])
        if dt:
            ico_dates[r["dodavatel_ico"]].append(dt)
    for ico in ico_dates:
        ico_dates[ico].sort()

    matching_ids = set()
    details = {}
    for r in rows:
        ico = r["dodavatel_ico"]
        dt = _parse_date(r["datum_podpisu"] or r["datum_zverejnenia"])
        if not dt or ico not in ico_dates:
            continue
        dates = ico_dates[ico]
        # Find this contract's position and check gap to previous
        idx = None
        for i, d in enumerate(dates):
            if d == dt:
                idx = i
                break
        if idx is None or idx == 0:
            continue  # First contract or not found
        gap_days = (dt - dates[idx - 1]).days
        if gap_days >= 730:  # 2 years
            matching_ids.add(r["id"])
            years = gap_days / 365.25
            details[r["id"]] = f"{r['suma']:,.0f} EUR po {years:.1f} rokoch bez zmluv (ICO: {ico})"
    return _insert_remove_flags(db, "dormant_then_active", matching_ids, details)


@_custom("threshold_gaming")
def _eval_threshold_gaming(db):
    """Flag contracts with suma just below the EU procurement threshold (€215K).

    The EU public procurement directive requires open EU-wide tender for
    contracts above €215,000 (for supplies/services). Contracts clustering
    in the €210,000–€214,999 band may indicate deliberate threshold gaming
    to avoid the more transparent procedure.

    We flag a contract if:
      1. Its suma is in the 210–215K band, AND
      2. The same buyer has at least one OTHER contract also in the 210–215K
         band (repeat pattern strengthens the signal), OR the contract is
         for services/supplies (not grants/dotácie which are naturally set).
    Single occurrences are still flagged but with weaker detail.
    """
    BAND_LO = 210000
    BAND_HI = 215000

    rows = db.execute("""
        SELECT id, objednavatel_ico, objednavatel, dodavatel, dodavatel_ico,
               suma, nazov_zmluvy
        FROM zmluvy
        WHERE suma >= ? AND suma < ?
        AND objednavatel_ico IS NOT NULL AND objednavatel_ico != ''
    """, (BAND_LO, BAND_HI)).fetchall()

    # Group by buyer to detect repeat offenders
    buyer_contracts = defaultdict(list)
    for r in rows:
        buyer_contracts[r["objednavatel_ico"]].append(r)

    # Exclude grants/dotácie — their amounts are set by policy, not gaming
    grant_keywords = {'dotáci', 'dotaci', 'príspev', 'prispev', 'grant', 'úver', 'uver', 'záložn', 'zalozn', 'mechanizm', 'poskytnutí nfp', 'nenávratn'}

    matching_ids = set()
    details = {}
    for buyer_ico, contracts in buyer_contracts.items():
        for r in contracts:
            title_lower = (r["nazov_zmluvy"] or "").lower()
            is_grant = any(kw in title_lower for kw in grant_keywords)
            if is_grant:
                continue

            diff = BAND_HI - r["suma"]
            if len(contracts) >= 2:
                detail = (
                    f"{r['suma']:,.2f} EUR (iba {diff:,.0f} EUR pod EU limitom 215K); "
                    f"objednavatel {r['objednavatel_ico']} ma {len(contracts)} zmluv v tomto pasme"
                )
            else:
                detail = f"{r['suma']:,.2f} EUR (iba {diff:,.0f} EUR pod EU limitom 215K)"

            matching_ids.add(r["id"])
            details[r["id"]] = detail

    return _insert_remove_flags(db, "threshold_gaming", matching_ids, details)


@_custom("fs_vat_deregistered")
def _eval_fs_vat_deregistered(db):
    """Flag contracts where supplier was deregistered from VAT (ICO match)."""
    has_table = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fs_vat_deregistered'"
    ).fetchone()[0]
    if not has_table:
        return 0, 0

    rows = db.execute("""
        SELECT z.id, v.nazov, v.rok_porusenia, v.dat_vymazu
        FROM zmluvy z
        JOIN fs_vat_deregistered v ON v.ico = replace(z.dodavatel_ico, ' ', '')
        WHERE v.ico IS NOT NULL
    """).fetchall()

    matching_ids = set()
    details = {}
    for r in rows:
        matching_ids.add(r["id"])
        parts = [r["nazov"] or ""]
        if r["rok_porusenia"]:
            parts.append(f"rok porusenia: {r['rok_porusenia']}")
        if r["dat_vymazu"]:
            parts.append(f"vymazany: {r['dat_vymazu']}")
        details[r["id"]] = ", ".join(parts)
    return _insert_remove_flags(db, "fs_vat_deregistered", matching_ids, details)


@_custom("fs_vat_dereg_risk")
def _eval_fs_vat_dereg_risk(db):
    """Flag contracts where supplier has active VAT deregistration reasons."""
    has_table = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fs_vat_dereg_reasons'"
    ).fetchone()[0]
    if not has_table:
        return 0, 0

    rows = db.execute("""
        SELECT z.id, v.nazov, v.rok_porusenia, v.dat_zverejnenia
        FROM zmluvy z
        JOIN fs_vat_dereg_reasons v ON v.ico = replace(z.dodavatel_ico, ' ', '')
        WHERE v.ico IS NOT NULL
    """).fetchall()

    matching_ids = set()
    details = {}
    for r in rows:
        matching_ids.add(r["id"])
        parts = [r["nazov"] or ""]
        if r["rok_porusenia"]:
            parts.append(f"rok porusenia: {r['rok_porusenia']}")
        if r["dat_zverejnenia"]:
            parts.append(f"zverejnene: {r['dat_zverejnenia']}")
        details[r["id"]] = ", ".join(parts)
    return _insert_remove_flags(db, "fs_vat_dereg_risk", matching_ids, details)


@_custom("negative_equity")
def _eval_negative_equity(db):
    """Flag contracts where supplier has negative equity per RÚZ financial statements."""
    has_table = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='ruz_equity'"
    ).fetchone()[0]
    if not has_table:
        return 0, 0

    rows = db.execute("""
        SELECT z.id, e.nazov, e.vlastne_imanie, e.obdobie
        FROM zmluvy z
        JOIN ruz_equity e ON e.ico = replace(z.dodavatel_ico, ' ', '')
        WHERE e.vlastne_imanie < 0
    """).fetchall()

    matching_ids = set()
    details = {}
    for r in rows:
        matching_ids.add(r["id"])
        details[r["id"]] = (
            f"{r['nazov']}: vlastne imanie {r['vlastne_imanie']:,.0f} EUR "
            f"(obdobie {r['obdobie']})"
        )
    return _insert_remove_flags(db, "negative_equity", matching_ids, details)


@_custom("fs_tax_debtor")
def _eval_fs_tax_debtor(db):
    """Flag contracts where supplier is on the FS tax debtors list (name match)."""
    # Check if table exists
    has_table = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fs_tax_debtors'"
    ).fetchone()[0]
    if not has_table:
        return 0, 0

    debtor_rows = db.execute(
        "SELECT nazov_normalized, nazov, max(suma) as max_sum FROM fs_tax_debtors "
        "WHERE nazov_normalized IS NOT NULL AND nazov_normalized != '' "
        "GROUP BY nazov_normalized"
    ).fetchall()
    debtor_map = {r["nazov_normalized"]: (r["nazov"], r["max_sum"]) for r in debtor_rows}

    contracts = db.execute(
        "SELECT id, dodavatel FROM zmluvy WHERE dodavatel IS NOT NULL AND dodavatel != ''"
    ).fetchall()

    matching_ids = set()
    details = {}
    for c in contracts:
        norm = normalize_company_name(c["dodavatel"])
        if norm in debtor_map:
            matching_ids.add(c["id"])
            orig_name, amount = debtor_map[norm]
            details[c["id"]] = f"{orig_name} (dlh: {amount:,.2f} EUR)" if amount else orig_name
    return _insert_remove_flags(db, "fs_tax_debtor", matching_ids, details)


def run_rules(db, rule_id=None):
    """Evaluate all enabled rules (or a specific one)."""
    if rule_id:
        rules = db.execute(
            "SELECT * FROM flag_rules WHERE id = ? AND enabled = 1", (rule_id,)
        ).fetchall()
        if not rules:
            print(f"Rule '{rule_id}' not found or disabled.")
            return
    else:
        rules = db.execute(
            "SELECT * FROM flag_rules WHERE enabled = 1 ORDER BY id"
        ).fetchall()

    total_inserted = 0
    total_removed = 0

    for rule in rules:
        t0 = time.time()
        try:
            inserted, removed = evaluate_rule(db, rule)
            elapsed = time.time() - t0
            total_inserted += inserted
            total_removed += removed

            flag_count = db.execute(
                "SELECT count(*) FROM red_flags WHERE flag_type = ?", (rule["id"],)
            ).fetchone()[0]

            print(f"  {rule['id']:25s} +{inserted:>5} -{removed:>3}  total={flag_count:>6}  ({elapsed:.2f}s)")
        except Exception as exc:
            print(f"  {rule['id']:25s} ERROR: {exc}")

    db.commit()
    total_flags = db.execute("SELECT count(*) FROM red_flags").fetchone()[0]
    print(f"\nDone: +{total_inserted} new, -{total_removed} removed, {total_flags} total flags")


def list_rules(db):
    """Print all rules with their flag counts."""
    rules = db.execute("SELECT * FROM flag_rules ORDER BY id").fetchall()
    for r in rules:
        count = db.execute(
            "SELECT count(*) FROM red_flags WHERE flag_type = ?", (r["id"],)
        ).fetchone()[0]
        status = "ON " if r["enabled"] else "OFF"
        print(f"  [{status}] {r['id']:25s} {r['severity']:8s} {count:>6} flags  {r['label']}")
        print(f"         SQL: {r['sql_condition']}")


def add_rule_interactive(db):
    """Interactively add a new flag rule."""
    print("Pridať novú žltú stopu")
    print("=" * 40)
    rule_id = input("ID (slug, e.g. 'high_value_no_ico'): ").strip()
    if not rule_id:
        print("Cancelled."); return
    label = input("Label (short name): ").strip()
    description = input("Description: ").strip()
    severity = input("Severity (info/warning/danger) [warning]: ").strip() or "warning"
    sql_condition = input("SQL WHERE condition (use z.* for zmluvy, e.* for extractions): ").strip()
    if not sql_condition:
        print("Cancelled."); return
    needs_ext = "1" if "e." in sql_condition else "0"

    # Validate the SQL
    join = "LEFT JOIN extractions e ON e.zmluva_id = z.id" if needs_ext == "1" else ""
    try:
        count = db.execute(
            f"SELECT count(*) FROM zmluvy z {join} WHERE {sql_condition}"
        ).fetchone()[0]
        print(f"Condition matches {count} contracts.")
    except Exception as exc:
        print(f"SQL error: {exc}")
        return

    confirm = input("Save this rule? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled."); return

    db.execute(
        """INSERT OR REPLACE INTO flag_rules
           (id, label, description, severity, sql_condition, needs_extraction)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (rule_id, label, description, severity, sql_condition, int(needs_ext)),
    )
    db.commit()
    print(f"Rule '{rule_id}' saved. Run without --init to evaluate it.")


def main():
    parser = argparse.ArgumentParser(description="CRZ Žltá Stopa Evaluator")
    parser.add_argument("--init", action="store_true", help="Seed default rules only")
    parser.add_argument("--rule", type=str, help="Run a specific rule by ID")
    parser.add_argument("--list", action="store_true", help="List all rules and counts")
    parser.add_argument("--add", action="store_true", help="Add a new rule interactively")
    args = parser.parse_args()

    db = get_db()
    init_tables(db)
    seed_rules(db)

    if args.list:
        list_rules(db)
    elif args.add:
        add_rule_interactive(db)
    elif args.init:
        print("Tables and default rules initialized.")
        list_rules(db)
    else:
        print("Evaluating žltá stopa rules...")
        run_rules(db, rule_id=args.rule)

    db.close()


if __name__ == "__main__":
    main()
