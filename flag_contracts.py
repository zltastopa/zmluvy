"""Evaluate red flag rules against contracts and materialize results.

Usage:
    uv run python flag_contracts.py                # run all enabled rules
    uv run python flag_contracts.py --rule hidden_entities  # run one rule
    uv run python flag_contracts.py --init          # seed default rules only
    uv run python flag_contracts.py --list          # show all rules
    uv run python flag_contracts.py --add           # add a new rule interactively
"""

import argparse
import json
import sqlite3
import time

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
        "description": "Zmluva nema uvedeny datum platnosti (platnost_do)",
        "severity": "info",
        "sql_condition": "z.platnost_do IS NULL OR z.platnost_do = ''",
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
    """Insert default rules (skip existing)."""
    for rule in DEFAULT_RULES:
        db.execute(
            """INSERT OR IGNORE INTO flag_rules
               (id, label, description, severity, sql_condition, needs_extraction)
               VALUES (?, ?, ?, ?, ?, ?)""",
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


def evaluate_custom_rule(db, rule):
    """Evaluate custom rules that require Python logic (e.g. JSON parsing)."""
    rule_id = rule["id"]

    if rule_id == "tax_unreliable_entity":
        return _eval_tax_unreliable_entity(db)
    if rule_id == "socpoist_debtor":
        return _eval_socpoist_debtor(db)
    if rule_id == "vszp_debtor_entity":
        return _eval_vszp_debtor_entity(db)

    raise ValueError(f"Unknown custom rule: {rule_id}")


def _eval_tax_unreliable_entity(db):
    """Flag contracts where a hidden entity ICO is 'menej spoľahlivý'."""
    # Load all unreliable ICOs into a set for fast lookup
    unreliable = set(
        r[0] for r in db.execute(
            "SELECT ico FROM tax_reliability WHERE status = 'menej spoľahlivý'"
        ).fetchall()
    )

    # Get all extractions with hidden entities
    rows = db.execute("""
        SELECT e.zmluva_id, e.extraction_json
        FROM extractions e
        WHERE e.hidden_entity_count > 0 AND e.extraction_json IS NOT NULL
    """).fetchall()

    matching_ids = set()
    details = {}
    for row in rows:
        try:
            ej = json.loads(row["extraction_json"])
        except Exception:
            continue
        for he in (ej.get("hidden_entities") or []):
            ico = (he.get("ico") or "").strip()
            if ico and ico in unreliable:
                matching_ids.add(row["zmluva_id"])
                name = he.get("name") or ico
                details[row["zmluva_id"]] = f"{name} (ICO: {ico})"

    # Insert flags
    inserted = 0
    for zmluva_id in matching_ids:
        cursor = db.execute(
            "INSERT OR IGNORE INTO red_flags (zmluva_id, flag_type, detail) VALUES (?, ?, ?)",
            (zmluva_id, "tax_unreliable_entity", details.get(zmluva_id)),
        )
        inserted += cursor.rowcount

    # Remove flags for contracts that no longer match
    cursor2 = db.execute(
        "DELETE FROM red_flags WHERE flag_type = 'tax_unreliable_entity' AND zmluva_id NOT IN ({})".format(
            ",".join(str(i) for i in matching_ids) if matching_ids else "0"
        )
    )
    removed = cursor2.rowcount

    return inserted, removed


def _eval_socpoist_debtor(db):
    """Flag contracts where dodavatel name matches a Socpoist debtor company."""
    # Build lookup of normalized socpoist company names -> (name, amount)
    socpoist_rows = db.execute(
        "SELECT name_normalized, name, amount FROM socpoist_debtors WHERE name_normalized IS NOT NULL"
    ).fetchall()
    socpoist_map = {}
    for r in socpoist_rows:
        key = r["name_normalized"]
        # Keep the one with highest debt
        if key not in socpoist_map or r["amount"] > socpoist_map[key][1]:
            socpoist_map[key] = (r["name"], r["amount"])

    # Get all distinct dodavatel names
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

    # Insert flags
    inserted = 0
    for zmluva_id in matching_ids:
        cursor = db.execute(
            "INSERT OR IGNORE INTO red_flags (zmluva_id, flag_type, detail) VALUES (?, ?, ?)",
            (zmluva_id, "socpoist_debtor", details.get(zmluva_id)),
        )
        inserted += cursor.rowcount

    # Remove stale flags
    cursor2 = db.execute(
        "DELETE FROM red_flags WHERE flag_type = 'socpoist_debtor' AND zmluva_id NOT IN ({})".format(
            ",".join(str(i) for i in matching_ids) if matching_ids else "0"
        )
    )
    removed = cursor2.rowcount
    return inserted, removed


def _eval_vszp_debtor_entity(db):
    """Flag contracts where a hidden entity ICO is a VSZP debtor."""
    # Load all VSZP debtor CINs into a set
    vszp_cins = {}
    for r in db.execute("SELECT cin, name, amount FROM vszp_debtors WHERE cin IS NOT NULL").fetchall():
        cin = r["cin"].strip()
        if cin:
            if cin not in vszp_cins or r["amount"] > vszp_cins[cin][1]:
                vszp_cins[cin] = (r["name"], r["amount"])

    # Get all extractions with hidden entities
    rows = db.execute("""
        SELECT e.zmluva_id, e.extraction_json
        FROM extractions e
        WHERE e.hidden_entity_count > 0 AND e.extraction_json IS NOT NULL
    """).fetchall()

    matching_ids = set()
    details = {}
    for row in rows:
        try:
            ej = json.loads(row["extraction_json"])
        except Exception:
            continue
        for he in (ej.get("hidden_entities") or []):
            ico = (he.get("ico") or "").strip()
            if ico and ico in vszp_cins:
                matching_ids.add(row["zmluva_id"])
                name, amount = vszp_cins[ico]
                entity_name = he.get("name") or name
                details[row["zmluva_id"]] = f"{entity_name} (ICO: {ico}, dlh VSZP: {amount:,.2f} EUR)"

    # Insert flags
    inserted = 0
    for zmluva_id in matching_ids:
        cursor = db.execute(
            "INSERT OR IGNORE INTO red_flags (zmluva_id, flag_type, detail) VALUES (?, ?, ?)",
            (zmluva_id, "vszp_debtor_entity", details.get(zmluva_id)),
        )
        inserted += cursor.rowcount

    # Remove stale flags
    cursor2 = db.execute(
        "DELETE FROM red_flags WHERE flag_type = 'vszp_debtor_entity' AND zmluva_id NOT IN ({})".format(
            ",".join(str(i) for i in matching_ids) if matching_ids else "0"
        )
    )
    removed = cursor2.rowcount
    return inserted, removed


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
    print("Add new red flag rule")
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
    parser = argparse.ArgumentParser(description="CRZ Red Flag Evaluator")
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
        print("Evaluating red flag rules...")
        run_rules(db, rule_id=args.rule)

    db.close()


if __name__ == "__main__":
    main()
