"""Import external register data (VSZP, Socpoist, RUZ) from PostgreSQL dumps into crz.db.

Usage:
    uv run python import_debtors.py                         # import all available
    uv run python import_debtors.py --vszp vszp.sql         # VSZP only
    uv run python import_debtors.py --socpoist socpoist.sql  # Socpoist only
    uv run python import_debtors.py --ruz ruz.sql            # RUZ only
"""
import confpath  # noqa: F401

import argparse
import sqlite3
from pathlib import Path

from settings import get_path, normalize_company_name

DB_PATH = get_path("CRZ_DB_PATH", "crz.db")
ROOT = Path(__file__).resolve().parent.parent


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_tables(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS vszp_debtors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            postal_code TEXT,
            amount REAL NOT NULL,
            payer_type TEXT,
            published_on TEXT NOT NULL,
            cin TEXT,
            health_care_claim TEXT
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_vszp_cin ON vszp_debtors(cin)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_vszp_name ON vszp_debtors(name)")

    db.execute("""
        CREATE TABLE IF NOT EXISTS socpoist_debtors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            amount REAL NOT NULL,
            published_on TEXT NOT NULL,
            name_normalized TEXT
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_socpoist_name ON socpoist_debtors(name_normalized)")
    db.commit()


def parse_pg_copy(filepath, num_fields):
    """Parse PostgreSQL COPY stdin data from a dump file."""
    in_copy = False
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('COPY '):
                in_copy = True
                continue
            if in_copy:
                if line.strip() == '\\.':
                    in_copy = False
                    continue
                parts = line.rstrip('\n').split('\t')
                # Replace \N with None
                parts = [None if p == '\\N' else p for p in parts]
                if len(parts) >= num_fields:
                    rows.append(parts[:num_fields])
    return rows


def import_vszp(db, filepath):
    """Import VSZP debtors."""
    print(f"Parsing {filepath}...")
    # Fields: id, name, address, city, postal_code, amount, payer_type, published_on, created_at, updated_at, cin, health_care_claim
    rows = parse_pg_copy(filepath, 12)
    print(f"  Parsed {len(rows)} rows")

    db.execute("DELETE FROM vszp_debtors")
    batch = []
    for r in rows:
        batch.append((
            int(r[0]),       # id
            r[1],            # name
            r[2],            # address
            r[3],            # city
            r[4],            # postal_code
            float(r[5]),     # amount
            r[6],            # payer_type
            r[7],            # published_on
            r[10],           # cin
            r[11],           # health_care_claim
        ))

    db.executemany("""
        INSERT INTO vszp_debtors (id, name, address, city, postal_code, amount, payer_type, published_on, cin, health_care_claim)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch)
    db.commit()

    with_cin = db.execute("SELECT count(*) FROM vszp_debtors WHERE cin IS NOT NULL").fetchone()[0]
    print(f"  Imported {len(batch)} VSZP debtors ({with_cin} with CIN/ICO)")


def import_socpoist(db, filepath):
    """Import Socpoist debtors."""
    print(f"Parsing {filepath}...")
    # Fields: id, name, address, city, amount, published_on, created_at, updated_at
    rows = parse_pg_copy(filepath, 8)
    print(f"  Parsed {len(rows)} rows")

    db.execute("DELETE FROM socpoist_debtors")
    batch = []
    for r in rows:
        name = r[1] or ''
        # Only normalize companies
        is_company = any(x in name.lower() for x in ['s.r.o', 'a.s.', 'spol.', 'o.z.', 'n.o.', 'z.s.', 'k.s.', 'v.o.s', 's.e.'])
        normalized = normalize_company_name(name) if is_company else None
        batch.append((
            int(r[0]),       # id
            name,            # name
            r[2],            # address
            r[3],            # city
            float(r[4]),     # amount
            r[5],            # published_on
            normalized,      # name_normalized
        ))

    db.executemany("""
        INSERT INTO socpoist_debtors (id, name, address, city, amount, published_on, name_normalized)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, batch)
    db.commit()

    companies = db.execute("SELECT count(*) FROM socpoist_debtors WHERE name_normalized IS NOT NULL").fetchone()[0]
    print(f"  Imported {len(batch)} Socpoist debtors ({companies} companies with normalized names)")


def init_ruz_tables(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS ruz_entities (
            id INTEGER PRIMARY KEY,
            cin TEXT,
            tin TEXT,
            name TEXT,
            city TEXT,
            street TEXT,
            postal_code TEXT,
            region TEXT,
            district TEXT,
            established_on TEXT,
            terminated_on TEXT,
            legal_form TEXT,
            legal_form_id INTEGER,
            nace_category TEXT,
            nace_code TEXT,
            organization_size TEXT,
            organization_size_id INTEGER,
            ownership_type TEXT,
            consolidated INTEGER,
            deleted INTEGER,
            data_source TEXT
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_ruz_cin ON ruz_entities(cin)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_ruz_name ON ruz_entities(name)")
    db.commit()


def parse_pg_copy_multi(filepath, table_fields):
    """Parse multiple COPY blocks from a PostgreSQL dump in a single pass.

    table_fields: dict of short_table_name -> num_fields
    Returns: dict of short_table_name -> list of rows
    """
    results = {name: [] for name in table_fields}
    current_table = None
    current_fields = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('COPY '):
                # Extract table name from "COPY schema.table (cols) FROM stdin;"
                full_name = line.split()[1]
                short_name = full_name.split('.')[-1]
                if short_name in table_fields:
                    current_table = short_name
                    current_fields = table_fields[short_name]
                else:
                    current_table = None
                continue
            if current_table:
                if line.strip() == '\\.':
                    current_table = None
                    continue
                parts = line.rstrip('\n').split('\t')
                parts = [None if p == '\\N' else p for p in parts]
                if len(parts) >= current_fields:
                    results[current_table].append(parts[:current_fields])

    return results


def import_ruz(db, filepath):
    """Import RUZ (Register of Financial Statements) entities with denormalized lookups."""
    print(f"Parsing {filepath} (single pass, multiple tables)...")

    tables = parse_pg_copy_multi(filepath, {
        'accounting_entities': 23,
        'legal_forms': 6,
        'organization_sizes': 6,
        'regions': 6,
        'districts': 7,
        'sk_nace_categories': 6,
        'ownership_types': 6,
    })

    for name, rows in tables.items():
        print(f"  {name}: {len(rows)} rows")

    # Build lookup dicts: id -> name_sk
    # Most tables: id(0), name_sk(1); districts: id(0), region_id(1), name_sk(2)
    def build_lookup(rows, name_idx=1):
        return {int(r[0]): r[name_idx] for r in rows}

    legal_forms = build_lookup(tables['legal_forms'])
    org_sizes = build_lookup(tables['organization_sizes'])
    regions = build_lookup(tables['regions'])
    districts = build_lookup(tables['districts'], name_idx=2)
    nace_cats = {int(r[0]): (r[1], r[5]) for r in tables['sk_nace_categories']}  # id -> (name, code)
    ownership = build_lookup(tables['ownership_types'])

    # Import accounting_entities with denormalized values
    # Fields: id(0), cin(1), tin(2), corporate_body_name(3), city(4), street(5),
    #         postal_code(6), region_id(7), district_id(8), municipality_id(9),
    #         last_updated_on(10), established_on(11), legal_form_id(12),
    #         sk_nace_category_id(13), organization_size_id(14), ownership_type_id(15),
    #         consolidated(16), data_source(17), created_at(18), updated_at(19),
    #         deleted(20), terminated_on(21), sid(22)

    init_ruz_tables(db)
    db.execute("DELETE FROM ruz_entities")

    batch = []
    for r in tables['accounting_entities']:
        lf_id = int(r[12]) if r[12] else None
        nace_id = int(r[13]) if r[13] else None
        os_id = int(r[14]) if r[14] else None
        ow_id = int(r[15]) if r[15] else None
        region_id = int(r[7]) if r[7] else None
        district_id = int(r[8]) if r[8] else None

        nace_name, nace_code = nace_cats.get(nace_id, (None, None)) if nace_id else (None, None)

        batch.append((
            int(r[0]),                              # id
            str(int(r[1])) if r[1] else None,       # cin (bigint -> text, strip leading zeros)
            str(int(r[2])) if r[2] else None,       # tin
            r[3],                                    # name
            r[4],                                    # city
            r[5],                                    # street
            r[6],                                    # postal_code
            regions.get(region_id),                  # region
            districts.get(district_id),              # district
            r[11],                                   # established_on
            r[21],                                   # terminated_on
            legal_forms.get(lf_id),                  # legal_form
            lf_id,                                   # legal_form_id
            nace_name,                               # nace_category
            nace_code,                               # nace_code
            org_sizes.get(os_id),                    # organization_size
            os_id,                                   # organization_size_id
            ownership.get(ow_id),                    # ownership_type
            1 if r[16] == 't' else 0,               # consolidated
            1 if r[20] == 't' else 0,               # deleted
            r[17],                                   # data_source
        ))

    db.executemany("""
        INSERT INTO ruz_entities (id, cin, tin, name, city, street, postal_code,
            region, district, established_on, terminated_on,
            legal_form, legal_form_id, nace_category, nace_code,
            organization_size, organization_size_id, ownership_type,
            consolidated, deleted, data_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch)
    db.commit()

    total = len(batch)
    with_cin = db.execute("SELECT count(*) FROM ruz_entities WHERE cin IS NOT NULL").fetchone()[0]
    terminated = db.execute("SELECT count(*) FROM ruz_entities WHERE terminated_on IS NOT NULL").fetchone()[0]
    micro = db.execute("SELECT count(*) FROM ruz_entities WHERE organization_size_id IN (0, 1, 2)").fetchone()[0]
    print(f"  Imported {total} RUZ entities ({with_cin} with CIN, {terminated} terminated, {micro} micro/unknown size)")

    # Show CRZ overlap
    overlap = db.execute("""
        SELECT count(DISTINCT z.dodavatel_ico) FROM zmluvy z
        JOIN ruz_entities r ON r.cin = z.dodavatel_ico
        WHERE z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
    """).fetchone()[0]
    not_found = db.execute("""
        SELECT count(DISTINCT z.dodavatel_ico) FROM zmluvy z
        WHERE z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
            AND length(z.dodavatel_ico) = 8
            AND z.dodavatel_ico NOT IN (SELECT cin FROM ruz_entities WHERE cin IS NOT NULL)
    """).fetchone()[0]
    print(f"  CRZ ICOs found in RUZ: {overlap}, not found: {not_found}")


def show_crz_matches(db):
    """Show how many CRZ contracts match debtor records."""
    # VSZP by CIN
    vszp_matches = db.execute("""
        SELECT count(DISTINCT z.id) FROM zmluvy z
        JOIN vszp_debtors v ON v.cin = z.dodavatel_ico
        WHERE z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
    """).fetchone()[0]
    print(f"\n  CRZ contracts with dodavatel matching VSZP by ICO: {vszp_matches}")

    # Socpoist by normalized name
    socpoist_matches = db.execute("""
        SELECT count(DISTINCT z.id) FROM zmluvy z
        JOIN socpoist_debtors s ON s.name_normalized = lower(replace(replace(replace(replace(replace(
            z.dodavatel, ', s.r.o.', ''), ', a.s.', ''), ' s.r.o.', ''), ' a.s.', ''), ',', ''))
        WHERE s.name_normalized IS NOT NULL
    """).fetchone()[0]
    print(f"  CRZ contracts with dodavatel matching Socpoist by name: {socpoist_matches}")


def main():
    parser = argparse.ArgumentParser(description="Import external registers into crz.db")
    parser.add_argument("--vszp", default=str(ROOT / "vszp.sql"), help="Path to vszp.sql")
    parser.add_argument("--socpoist", default=str(ROOT / "socpoist.sql"), help="Path to socpoist.sql")
    parser.add_argument("--ruz", default=str(ROOT / "ruz.sql"), help="Path to ruz.sql")
    args = parser.parse_args()

    db = get_db()
    init_tables(db)

    if Path(args.vszp).exists():
        import_vszp(db, args.vszp)
    else:
        print(f"Skipping VSZP — {args.vszp} not found")

    if Path(args.socpoist).exists():
        import_socpoist(db, args.socpoist)
    else:
        print(f"Skipping Socpoist — {args.socpoist} not found")

    if Path(args.ruz).exists():
        import_ruz(db, args.ruz)
    else:
        print(f"Skipping RUZ — {args.ruz} not found")

    show_crz_matches(db)
    db.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
