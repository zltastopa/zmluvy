"""Tests for the CRZ-connected RUZ materialization optimization.

Verifies that:
- ruz_entities table contains only CRZ-connected entities (slim columns)
- ruz_entities_full view provides access to all columns
- Flag queries produce correct results against the slim table
- Browse query columns are available in the slim table
- Detail page query works via ruz_entities_full view

Requires Delta tables in delta_store/tables/.

Run:
    uv run pytest delta_store/tests/test_ruz_optimization.py -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TABLES_DIR = Path(__file__).resolve().parent.parent / "tables"

# Skip all tests if Delta tables aren't available
pytestmark = pytest.mark.skipif(
    not (TABLES_DIR / "ruz_entities" / "_delta_log").exists(),
    reason="Delta tables not available",
)


@pytest.fixture(scope="module")
def db():
    """Create a DuckDB connection with the RUZ optimization applied."""
    import serve

    serve.TABLES_DIR = TABLES_DIR
    serve._conn = None  # force re-init
    conn = serve.get_db()
    yield conn
    serve._conn = None


# ---------------------------------------------------------------------------
# Table structure
# ---------------------------------------------------------------------------

class TestSlimTable:
    """ruz_entities should be a materialized table with slim columns."""

    def test_is_table_not_view(self, db):
        tables = {r[0] for r in db.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_type = 'BASE TABLE' AND table_name = 'ruz_entities'"
        ).fetchall()}
        assert "ruz_entities" in tables

    def test_has_required_columns(self, db):
        cols = {r[0] for r in db.execute("DESCRIBE ruz_entities").fetchall()}
        expected = {
            "cin", "name", "terminated_on", "established_on",
            "organization_size_id", "organization_size",
            "legal_form_id", "legal_form",
            "region", "nace_code", "nace_category",
        }
        assert expected == cols

    def test_excludes_non_crz_entities(self, db):
        """Slim table should have far fewer rows than full view."""
        slim = db.execute("SELECT count(*) FROM ruz_entities").fetchone()[0]
        full = db.execute("SELECT count(*) FROM ruz_entities_full").fetchone()[0]
        assert slim < full * 0.1, f"Slim ({slim}) should be <10% of full ({full})"

    def test_all_cins_appear_in_crz(self, db):
        """Every cin in slim table should exist in zmluvy as supplier or buyer."""
        orphans = db.execute("""
            SELECT count(*) FROM ruz_entities r
            WHERE r.cin NOT IN (
                SELECT dodavatel_ico FROM zmluvy WHERE dodavatel_ico IS NOT NULL
                UNION
                SELECT objednavatel_ico FROM zmluvy WHERE objednavatel_ico IS NOT NULL
            )
        """).fetchone()[0]
        assert orphans == 0, f"{orphans} ruz_entities CINs not found in zmluvy"


# ---------------------------------------------------------------------------
# Full view
# ---------------------------------------------------------------------------

class TestFullView:
    """ruz_entities_full should be a view with all columns."""

    def test_is_view_not_table(self, db):
        views = {r[0] for r in db.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_type = 'VIEW' AND table_name = 'ruz_entities_full'"
        ).fetchall()}
        assert "ruz_entities_full" in views

    def test_has_detail_columns(self, db):
        """Full view must have columns needed by the detail page."""
        cols = {r[0] for r in db.execute("DESCRIBE ruz_entities_full").fetchall()}
        detail_cols = {"city", "street", "district", "ownership_type"}
        assert detail_cols.issubset(cols), f"Missing: {detail_cols - cols}"

    def test_full_view_has_more_rows(self, db):
        full = db.execute("SELECT count(*) FROM ruz_entities_full").fetchone()[0]
        assert full > 1_000_000, f"Full view should have >1M rows, got {full}"


# ---------------------------------------------------------------------------
# Flag query correctness
# ---------------------------------------------------------------------------

class TestFlagCorrectness:
    """Flag rules that use ruz_entities should produce correct results."""

    def test_terminated_company_count(self, db):
        """terminated_company flags should match between slim table and full scan."""
        slim_count = db.execute("""
            SELECT count(DISTINCT z.id) FROM zmluvy z
            JOIN ruz_entities r ON r.cin = z.dodavatel_ico
            WHERE r.terminated_on IS NOT NULL
              AND z.dodavatel_ico NOT IN (
                  SELECT cin FROM ruz_entities WHERE terminated_on IS NULL AND cin IS NOT NULL
              )
        """).fetchone()[0]
        # Same query against full view
        full_count = db.execute("""
            SELECT count(DISTINCT z.id) FROM zmluvy z
            JOIN ruz_entities_full r ON r.cin = z.dodavatel_ico
            WHERE r.terminated_on IS NOT NULL
              AND z.dodavatel_ico NOT IN (
                  SELECT cin FROM ruz_entities_full WHERE terminated_on IS NULL AND cin IS NOT NULL
              )
        """).fetchone()[0]
        assert slim_count == full_count, (
            f"terminated_company: slim={slim_count}, full={full_count}"
        )

    def test_not_in_ruz_count(self, db):
        """not_in_ruz flags should be identical between slim and full."""
        slim_count = db.execute("""
            SELECT count(*) FROM zmluvy z
            WHERE z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
              AND z.dodavatel_ico NOT LIKE '00%'
              AND z.dodavatel_ico NOT IN (SELECT cin FROM ruz_entities WHERE cin IS NOT NULL)
        """).fetchone()[0]
        full_count = db.execute("""
            SELECT count(*) FROM zmluvy z
            WHERE z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
              AND z.dodavatel_ico NOT LIKE '00%'
              AND z.dodavatel_ico NOT IN (SELECT cin FROM ruz_entities_full WHERE cin IS NOT NULL)
        """).fetchone()[0]
        assert slim_count == full_count, (
            f"not_in_ruz: slim={slim_count}, full={full_count}"
        )

    def test_fresh_company_count(self, db):
        """fresh_company detection should match between slim and full."""
        slim_count = db.execute("""
            SELECT count(*) FROM ruz_entities
            WHERE cin IS NOT NULL AND established_on IS NOT NULL AND terminated_on IS NULL
        """).fetchone()[0]
        full_count = db.execute("""
            SELECT count(*) FROM ruz_entities_full
            WHERE cin IS NOT NULL AND established_on IS NOT NULL AND terminated_on IS NULL
              AND cin IN (
                  SELECT dodavatel_ico FROM zmluvy WHERE dodavatel_ico IS NOT NULL
                  UNION
                  SELECT objednavatel_ico FROM zmluvy WHERE objednavatel_ico IS NOT NULL
              )
        """).fetchone()[0]
        assert slim_count == full_count, (
            f"fresh_company pool: slim={slim_count}, full={full_count}"
        )

    def test_nace_mismatch_count(self, db):
        """nace_mismatch join should produce same results with slim vs full."""
        slim_count = db.execute("""
            SELECT count(*) FROM zmluvy z
            JOIN extractions e ON e.zmluva_id = z.id
            JOIN ruz_entities r ON r.cin = z.dodavatel_ico
            WHERE e.service_category IS NOT NULL AND e.service_category != 'other'
              AND r.nace_code IS NOT NULL AND r.nace_code != ''
        """).fetchone()[0]
        full_count = db.execute("""
            SELECT count(*) FROM zmluvy z
            JOIN extractions e ON e.zmluva_id = z.id
            JOIN ruz_entities_full r ON r.cin = z.dodavatel_ico
            WHERE e.service_category IS NOT NULL AND e.service_category != 'other'
              AND r.nace_code IS NOT NULL AND r.nace_code != ''
        """).fetchone()[0]
        assert slim_count == full_count, (
            f"nace_mismatch pool: slim={slim_count}, full={full_count}"
        )


# ---------------------------------------------------------------------------
# Browse query compatibility
# ---------------------------------------------------------------------------

class TestBrowseQuery:
    """Browse API columns must be available in the slim table."""

    def test_browse_columns_available(self, db):
        """All columns used by the browse endpoint should exist in ruz_entities."""
        browse_cols = [
            "established_on", "terminated_on", "legal_form",
            "organization_size", "organization_size_id", "nace_category",
        ]
        row = db.execute(f"""
            SELECT {', '.join(f'ruz.{c}' for c in browse_cols)}
            FROM zmluvy z
            LEFT JOIN ruz_entities ruz ON ruz.cin = z.dodavatel_ico
            LIMIT 1
        """).fetchone()
        assert row is not None

    def test_browse_filter_terminated(self, db):
        """Filter by ruz.terminated_on should work."""
        count = db.execute("""
            SELECT count(*) FROM zmluvy z
            LEFT JOIN ruz_entities ruz ON ruz.cin = z.dodavatel_ico
            WHERE ruz.terminated_on IS NOT NULL
        """).fetchone()[0]
        assert count >= 0  # just verify it runs without error

    def test_browse_filter_micro(self, db):
        """Filter by organization_size_id should work."""
        count = db.execute("""
            SELECT count(*) FROM zmluvy z
            LEFT JOIN ruz_entities ruz ON ruz.cin = z.dodavatel_ico
            WHERE ruz.organization_size_id IN (1, 2)
        """).fetchone()[0]
        assert count >= 0


# ---------------------------------------------------------------------------
# Detail page query
# ---------------------------------------------------------------------------

class TestDetailPage:
    """Detail page uses ruz_entities_full for rich company info."""

    def test_detail_query_works(self, db):
        """The detail page query should return results from ruz_entities_full."""
        # Pick a real ICO from zmluvy
        ico = db.execute("""
            SELECT dodavatel_ico FROM zmluvy
            WHERE dodavatel_ico IS NOT NULL AND dodavatel_ico != ''
            LIMIT 1
        """).fetchone()
        if ico is None:
            pytest.skip("No contracts with ICO")
        row = db.execute("""
            SELECT name, city, street, region, district, established_on, terminated_on,
                legal_form, nace_category, nace_code, organization_size, ownership_type
            FROM ruz_entities_full WHERE cin = $1 LIMIT 1
        """, [ico[0]]).fetchone()
        # May be None if this ICO isn't in RUZ — that's OK, query should just work
        assert True
