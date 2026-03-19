"""Tests for flag rule accuracy — validates rules don't produce false positives.

Each test creates a minimal in-memory DuckDB with synthetic data and verifies
that the flag SQL condition triggers correctly (true positives) and doesn't
trigger for known false-positive patterns.

Run:
    uv run pytest delta_store/tests/test_flag_rules.py -v
"""

import duckdb
import pytest


@pytest.fixture
def db():
    """Create a fresh DuckDB connection with minimal schema for flag testing."""
    conn = duckdb.connect()
    conn.execute("""
        CREATE TABLE zmluvy (
            id INTEGER, nazov_zmluvy VARCHAR, dodavatel VARCHAR,
            dodavatel_ico VARCHAR, objednavatel VARCHAR, objednavatel_ico VARCHAR,
            suma DOUBLE, datum_zverejnenia VARCHAR, datum_podpisu VARCHAR,
            platnost_do VARCHAR, typ VARCHAR, stav VARCHAR, rezort VARCHAR,
            crz_url VARCHAR, suma_celkom DOUBLE
        )
    """)
    conn.execute("""
        CREATE TABLE extractions (
            zmluva_id INTEGER, actual_subject VARCHAR, service_category VARCHAR,
            hidden_entity_count INTEGER, penalty_asymmetry VARCHAR,
            penalty_count INTEGER, bezodplatne INTEGER,
            subcontractor_max_percentage VARCHAR, extraction_json VARCHAR,
            hidden_entities VARCHAR, funding_type VARCHAR
        )
    """)
    conn.execute("""
        CREATE TABLE prilohy (zmluva_id INTEGER, nazov VARCHAR)
    """)
    conn.execute("""
        CREATE TABLE ruz_entities (
            cin VARCHAR, name VARCHAR, established_on VARCHAR,
            terminated_on VARCHAR, nace_code VARCHAR, nace_category VARCHAR,
            organization_size_id INTEGER, legal_form_id INTEGER, region VARCHAR
        )
    """)
    conn.execute("""
        CREATE TABLE tax_reliability (ico VARCHAR, status VARCHAR)
    """)
    conn.execute("""
        CREATE TABLE vszp_debtors (cin VARCHAR, name VARCHAR, amount DOUBLE)
    """)
    conn.execute("""
        CREATE TABLE red_flags (
            id INTEGER, zmluva_id INTEGER, flag_type VARCHAR,
            detail VARCHAR, created_at VARCHAR
        )
    """)
    return conn


def run_sql_flag(db, sql_condition: str, extra_bindings=None) -> set[int]:
    """Run a flag rule SQL condition and return matching zmluva IDs."""
    query = f"""
        SELECT z.id
        FROM zmluvy z
        LEFT JOIN extractions e ON z.id = e.zmluva_id
        LEFT JOIN (
            SELECT zmluva_id, count(*) as prilohy_count
            FROM prilohy GROUP BY zmluva_id
        ) p ON z.id = p.zmluva_id
        WHERE ({sql_condition})
    """
    return {r[0] for r in db.execute(query).fetchall()}


# =========================================================================
# not_in_ruz — should exclude public entities (ICO starting with 00)
# =========================================================================

NOT_IN_RUZ_CONDITION = (
    "z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != '' "
    "AND length(z.dodavatel_ico) = 8 "
    "AND z.dodavatel_ico NOT LIKE '00%' "
    "AND z.dodavatel_ico NOT IN "
    "(SELECT cin FROM ruz_entities WHERE cin IS NOT NULL)"
)


class TestNotInRuz:
    def test_flags_private_company_not_in_ruz(self, db):
        """Private company with 8-digit ICO not in RUZ should be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'test','Firma s.r.o.','44556677','Obec X','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, NOT_IN_RUZ_CONDITION)
        assert 1 in result

    def test_skips_municipality(self, db):
        """Municipality (ICO 00xxxxxx) should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'test','Mesto Holíč','00309541','MV SR','00151866',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, NOT_IN_RUZ_CONDITION)
        assert 1 not in result

    def test_skips_state_org(self, db):
        """State organization with 00-prefix ICO should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'test','DIVES, príspevková organizácia','00162957','MV SR','00151866',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, NOT_IN_RUZ_CONDITION)
        assert 1 not in result

    def test_skips_company_in_ruz(self, db):
        """Company that IS in RUZ should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'test','Real s.r.o.','44556677','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO ruz_entities VALUES ('44556677','Real s.r.o.',NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, NOT_IN_RUZ_CONDITION)
        assert 1 not in result

    def test_skips_empty_ico(self, db):
        """Empty ICO should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'test','Ján Novák','','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, NOT_IN_RUZ_CONDITION)
        assert 1 not in result

    def test_skips_short_ico(self, db):
        """ICO shorter than 8 chars (foreign) should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'test','Foreign Ltd','12345','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, NOT_IN_RUZ_CONDITION)
        assert 1 not in result


# =========================================================================
# signatory_overlap — threshold raised from 3 to 10
# =========================================================================

def _build_extraction_json(signatories: list[str]) -> str:
    """Build minimal extraction_json with signatory names."""
    import json
    return json.dumps({"signatories": [{"name": n} for n in signatories]})


def _eval_signatory_overlap(db) -> tuple[set, dict]:
    """Reproduce the signatory_overlap logic with threshold=10."""
    import json
    from collections import defaultdict

    rows = db.execute("""
        SELECT e.zmluva_id, e.extraction_json, z.dodavatel_ico
        FROM extractions e JOIN zmluvy z ON z.id = e.zmluva_id
        WHERE e.extraction_json IS NOT NULL
          AND z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != ''
    """).fetchall()

    sig_map = defaultdict(set)
    sig_contracts = defaultdict(set)
    for zid, ej_str, dod_ico in rows:
        try:
            ej = json.loads(ej_str)
        except Exception:
            continue
        for sig in (ej.get("signatories") or []):
            name = (sig.get("name") or "").strip().lower()
            if name and len(name) > 5:
                sig_map[name].add(dod_ico)
                sig_contracts[name].add(zid)

    matching, details = set(), {}
    for name, icos in sig_map.items():
        if len(icos) >= 10:
            for zid in sig_contracts[name]:
                matching.add(zid)
                details[zid] = f"{name.title()} podpisuje za {len(icos)} roznych dodavatelov"
    return matching, details


class TestSignatoryOverlap:
    def test_flags_signatory_with_10_plus_suppliers(self, db):
        """Person signing for 10+ different suppliers should be flagged."""
        for i in range(1, 12):
            ico = f"4400{i:04d}"
            db.execute(f"INSERT INTO zmluvy VALUES ({i},'zmluva','Firma {i}','{ico}','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
            ej = _build_extraction_json(["Ing. Podozrivy Človek"])
            db.execute("INSERT INTO extractions VALUES (?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,?,NULL,NULL)", [i, ej])
        matching, _ = _eval_signatory_overlap(db)
        assert len(matching) == 11

    def test_skips_signatory_with_3_suppliers(self, db):
        """Person signing for only 3 suppliers should NOT be flagged (old threshold)."""
        for i in range(1, 4):
            ico = f"4400{i:04d}"
            db.execute(f"INSERT INTO zmluvy VALUES ({i},'zmluva','Firma {i}','{ico}','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
            ej = _build_extraction_json(["JUDr. Bežný Právnik"])
            db.execute("INSERT INTO extractions VALUES (?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,?,NULL,NULL)", [i, ej])
        matching, _ = _eval_signatory_overlap(db)
        assert len(matching) == 0

    def test_skips_signatory_with_9_suppliers(self, db):
        """Person signing for 9 suppliers should NOT be flagged (just under threshold)."""
        for i in range(1, 10):
            ico = f"4400{i:04d}"
            db.execute(f"INSERT INTO zmluvy VALUES ({i},'zmluva','Firma {i}','{ico}','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
            ej = _build_extraction_json(["Mgr. Normálny Notár"])
            db.execute("INSERT INTO extractions VALUES (?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,?,NULL,NULL)", [i, ej])
        matching, _ = _eval_signatory_overlap(db)
        assert len(matching) == 0

    def test_skips_short_names(self, db):
        """Names shorter than 6 chars should be ignored."""
        for i in range(1, 12):
            ico = f"4400{i:04d}"
            db.execute(f"INSERT INTO zmluvy VALUES ({i},'zmluva','Firma {i}','{ico}','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
            ej = _build_extraction_json(["J.Nov"])  # 5 chars
            db.execute("INSERT INTO extractions VALUES (?,NULL,NULL,NULL,NULL,NULL,NULL,NULL,?,NULL,NULL)", [i, ej])
        matching, _ = _eval_signatory_overlap(db)
        assert len(matching) == 0
