"""Import VSZP and Socpoist debtor lists from PostgreSQL dumps into crz.db.

Usage:
    uv run python import_debtors.py
    uv run python import_debtors.py --vszp vszp.sql --socpoist socpoist.sql
"""
import argparse
import sqlite3
from pathlib import Path

from settings import get_path, normalize_company_name

DB_PATH = get_path("CRZ_DB_PATH", "crz.db")
ROOT = Path(__file__).parent


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
    parser = argparse.ArgumentParser(description="Import debtor lists into crz.db")
    parser.add_argument("--vszp", default=str(ROOT / "vszp.sql"), help="Path to vszp.sql")
    parser.add_argument("--socpoist", default=str(ROOT / "socpoist.sql"), help="Path to socpoist.sql")
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

    show_crz_matches(db)
    db.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
