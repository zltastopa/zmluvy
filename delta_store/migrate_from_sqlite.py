"""Migrate all tables from SQLite (crz.db) to Delta Lake tables.

Usage:
    uv run python delta_store/migrate_from_sqlite.py
    uv run python delta_store/migrate_from_sqlite.py --sqlite path/to/crz.db
    uv run python delta_store/migrate_from_sqlite.py --out delta_store/tables
"""

import argparse
import sqlite3
import sys
from pathlib import Path

import pyarrow as pa
from deltalake import write_deltalake

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from settings import get_path

# Arrow schemas per table — explicit types avoid inference issues on NULL-heavy columns
SCHEMAS = {
    "zmluvy": pa.schema([
        ("id", pa.int64()),
        ("nazov_zmluvy", pa.utf8()),
        ("cislo_zmluvy", pa.utf8()),
        ("dodavatel", pa.utf8()),
        ("dodavatel_ico", pa.utf8()),
        ("dodavatel_adresa", pa.utf8()),
        ("objednavatel", pa.utf8()),
        ("objednavatel_ico", pa.utf8()),
        ("objednavatel_adresa", pa.utf8()),
        ("suma", pa.float64()),
        ("suma_celkom", pa.float64()),
        ("datum_zverejnenia", pa.utf8()),
        ("datum_podpisu", pa.utf8()),
        ("datum_ucinnosti", pa.utf8()),
        ("platnost_do", pa.utf8()),
        ("poznamka", pa.utf8()),
        ("popis", pa.utf8()),
        ("typ", pa.utf8()),
        ("stav", pa.utf8()),
        ("druh", pa.utf8()),
        ("rezort_id", pa.utf8()),
        ("rezort", pa.utf8()),
        ("zdroj", pa.utf8()),
        ("uvo_url", pa.utf8()),
        ("crz_url", pa.utf8()),
    ]),
    "extractions": pa.schema([
        ("zmluva_id", pa.int64()),
        ("service_category", pa.utf8()),
        ("actual_subject", pa.utf8()),
        ("penalty_asymmetry", pa.utf8()),
        ("auto_renewal", pa.int64()),
        ("bezodplatne", pa.int64()),
        ("funding_type", pa.utf8()),
        ("grant_amount", pa.utf8()),
        ("hidden_entity_count", pa.int64()),
        ("penalty_count", pa.int64()),
        ("iban_count", pa.int64()),
        ("extraction_json", pa.utf8()),
        ("model", pa.utf8()),
        ("subcontracting_mentioned", pa.int64()),
        ("subcontractor_count", pa.int64()),
        ("subcontractor_max_percentage", pa.utf8()),
    ]),
    "red_flags": pa.schema([
        ("id", pa.int64()),
        ("zmluva_id", pa.int64()),
        ("flag_type", pa.utf8()),
        ("detail", pa.utf8()),
        ("created_at", pa.utf8()),
    ]),
    "flag_rules": pa.schema([
        ("id", pa.utf8()),
        ("label", pa.utf8()),
        ("description", pa.utf8()),
        ("severity", pa.utf8()),
        ("sql_condition", pa.utf8()),
        ("needs_extraction", pa.int64()),
        ("enabled", pa.int64()),
        ("created_at", pa.utf8()),
    ]),
    "prilohy": pa.schema([
        ("id", pa.int64()),
        ("zmluva_id", pa.int64()),
        ("nazov", pa.utf8()),
        ("subor", pa.utf8()),
        ("url", pa.utf8()),
    ]),
    "tax_reliability": pa.schema([
        ("ico", pa.utf8()),
        ("dic", pa.utf8()),
        ("nazov", pa.utf8()),
        ("status", pa.utf8()),
        ("obec", pa.utf8()),
        ("psc", pa.utf8()),
        ("ulica", pa.utf8()),
        ("stat", pa.utf8()),
    ]),
    "ruz_entities": pa.schema([
        ("id", pa.int64()),
        ("cin", pa.utf8()),
        ("tin", pa.utf8()),
        ("name", pa.utf8()),
        ("city", pa.utf8()),
        ("street", pa.utf8()),
        ("postal_code", pa.utf8()),
        ("region", pa.utf8()),
        ("district", pa.utf8()),
        ("established_on", pa.utf8()),
        ("terminated_on", pa.utf8()),
        ("legal_form", pa.utf8()),
        ("legal_form_id", pa.int64()),
        ("nace_category", pa.utf8()),
        ("nace_code", pa.utf8()),
        ("organization_size", pa.utf8()),
        ("organization_size_id", pa.int64()),
        ("ownership_type", pa.utf8()),
        ("consolidated", pa.int64()),
        ("deleted", pa.int64()),
        ("data_source", pa.utf8()),
    ]),
    "ruz_equity": pa.schema([
        ("ico", pa.utf8()),
        ("ruz_id", pa.utf8()),
        ("nazov", pa.utf8()),
        ("obdobie", pa.utf8()),
        ("vlastne_imanie", pa.float64()),
        ("zakladne_imanie", pa.float64()),
        ("vysledok_hospodarenia", pa.float64()),
        ("celkove_pasiva", pa.float64()),
        ("uz_id", pa.utf8()),
        ("vykaz_id", pa.utf8()),
        ("fetched_at", pa.utf8()),
    ]),
    "vszp_debtors": pa.schema([
        ("id", pa.int64()),
        ("name", pa.utf8()),
        ("address", pa.utf8()),
        ("city", pa.utf8()),
        ("postal_code", pa.utf8()),
        ("amount", pa.float64()),
        ("payer_type", pa.utf8()),
        ("published_on", pa.utf8()),
        ("cin", pa.utf8()),
        ("health_care_claim", pa.utf8()),
    ]),
    "socpoist_debtors": pa.schema([
        ("id", pa.int64()),
        ("name", pa.utf8()),
        ("address", pa.utf8()),
        ("city", pa.utf8()),
        ("amount", pa.float64()),
        ("published_on", pa.utf8()),
        ("name_normalized", pa.utf8()),
    ]),
    "fs_tax_debtors": pa.schema([
        ("id", pa.int64()),
        ("nazov", pa.utf8()),
        ("nazov_normalized", pa.utf8()),
        ("suma", pa.float64()),
        ("ulica", pa.utf8()),
        ("psc", pa.utf8()),
        ("obec", pa.utf8()),
    ]),
    "fs_vat_deregistered": pa.schema([
        ("id", pa.int64()),
        ("ico", pa.utf8()),
        ("ic_dph", pa.utf8()),
        ("nazov", pa.utf8()),
        ("obec", pa.utf8()),
        ("psc", pa.utf8()),
        ("adresa", pa.utf8()),
        ("rok_porusenia", pa.utf8()),
        ("dat_zverejnenia", pa.utf8()),
        ("dat_vymazu", pa.utf8()),
    ]),
    "fs_vat_dereg_reasons": pa.schema([
        ("id", pa.int64()),
        ("ico", pa.utf8()),
        ("ic_dph", pa.utf8()),
        ("nazov", pa.utf8()),
        ("obec", pa.utf8()),
        ("psc", pa.utf8()),
        ("adresa", pa.utf8()),
        ("rok_porusenia", pa.utf8()),
        ("dat_zverejnenia", pa.utf8()),
    ]),
    "fs_corporate_tax": pa.schema([
        ("id", pa.int64()),
        ("ico", pa.utf8()),
        ("dic", pa.utf8()),
        ("nazov", pa.utf8()),
        ("obec", pa.utf8()),
        ("psc", pa.utf8()),
        ("ulica", pa.utf8()),
        ("stat", pa.utf8()),
        ("obdobie_od", pa.utf8()),
        ("obdobie_do", pa.utf8()),
        ("vyrubena_dan", pa.float64()),
        ("dodat_vyrubena_dan", pa.float64()),
        ("danova_strata", pa.float64()),
    ]),
    "rezorty": pa.schema([
        ("id", pa.utf8()),
        ("nazov", pa.utf8()),
    ]),
}

# Primary key columns per table (used for merge/upsert)
PRIMARY_KEYS = {
    "zmluvy": "id",
    "extractions": "zmluva_id",
    "red_flags": "id",
    "flag_rules": "id",
    "prilohy": "id",
    "tax_reliability": "ico",
    "ruz_entities": "id",
    "ruz_equity": "ico",
    "vszp_debtors": "id",
    "socpoist_debtors": "id",
    "fs_tax_debtors": "id",
    "fs_vat_deregistered": "id",
    "fs_vat_dereg_reasons": "id",
    "fs_corporate_tax": "id",
    "rezorty": "id",
}

BATCH_SIZE = 50_000


def read_sqlite_batched(conn, table_name, schema):
    """Read a SQLite table in batches, yielding PyArrow RecordBatches."""
    col_names = [f.name for f in schema]
    cursor = conn.execute(f"SELECT {','.join(col_names)} FROM [{table_name}]")
    while True:
        rows = cursor.fetchmany(BATCH_SIZE)
        if not rows:
            break
        columns = {col: [] for col in col_names}
        for row in rows:
            for i, col in enumerate(col_names):
                columns[col].append(row[i])
        arrays = []
        for field in schema:
            # SQLite may store ints in text columns — coerce to string
            if field.type == pa.utf8():
                columns[field.name] = [str(v) if v is not None and not isinstance(v, str) else v
                                       for v in columns[field.name]]
            arr = pa.array(columns[field.name], type=field.type)
            arrays.append(arr)
        yield pa.RecordBatch.from_arrays(arrays, schema=schema)


def migrate_table(conn, table_name, schema, out_dir):
    """Migrate one SQLite table to a Delta Lake table."""
    table_path = str(out_dir / table_name)
    count = conn.execute(f"SELECT count(*) FROM [{table_name}]").fetchone()[0]
    if count == 0:
        print(f"  {table_name}: empty, creating empty Delta table")
        empty = pa.table({f.name: pa.array([], type=f.type) for f in schema}, schema=schema)
        write_deltalake(table_path, empty, mode="overwrite")
        return 0

    first = True
    written = 0
    for batch in read_sqlite_batched(conn, table_name, schema):
        table = pa.Table.from_batches([batch], schema=schema)
        if first:
            write_deltalake(table_path, table, mode="overwrite")
            first = False
        else:
            write_deltalake(table_path, table, mode="append")
        written += len(batch)
        print(f"  {table_name}: {written:,}/{count:,}", end="\r")

    print(f"  {table_name}: {written:,} rows migrated")
    return written


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite to Delta Lake")
    parser.add_argument("--sqlite", default=None, help="Path to crz.db")
    parser.add_argument("--out", default=None, help="Output directory for Delta tables")
    args = parser.parse_args()

    sqlite_path = args.sqlite or get_path("CRZ_DB_PATH", "crz.db")
    out_dir = Path(args.out) if args.out else Path(__file__).parent / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Source: {sqlite_path}")
    print(f"Target: {out_dir}")

    conn = sqlite3.connect(sqlite_path)

    # Discover which tables actually exist in the SQLite DB
    existing = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%'"
    ).fetchall()}

    total = 0
    for table_name, schema in SCHEMAS.items():
        if table_name not in existing:
            print(f"  {table_name}: not found in SQLite, skipping")
            continue
        total += migrate_table(conn, table_name, schema, out_dir)

    conn.close()
    print(f"\nDone! {total:,} total rows migrated to {out_dir}")


if __name__ == "__main__":
    main()
