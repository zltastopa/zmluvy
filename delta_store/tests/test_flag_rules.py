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


# =========================================================================
# missing_expiry — exclude low-value and indefinite-by-nature categories
# =========================================================================

MISSING_EXPIRY_CONDITION = (
    "(z.platnost_do IS NULL OR z.platnost_do = '') "
    "AND z.suma > 10000 "
    "AND (e.service_category IS NULL OR e.service_category NOT IN "
    "('property_lease', 'cemetery', 'easement_encumbrance', 'asset_transfer', 'copyright_royalty'))"
)


class TestMissingExpiry:
    def test_flags_high_value_no_expiry(self, db):
        """High-value contract without expiry in non-exempt category should be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',50000,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO extractions VALUES (1,NULL,'professional_consulting',0,NULL,0,0,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, MISSING_EXPIRY_CONDITION)
        assert 1 in result

    def test_flags_no_extraction(self, db):
        """High-value contract without extraction (category=NULL) should still be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',50000,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, MISSING_EXPIRY_CONDITION)
        assert 1 in result

    def test_skips_property_lease(self, db):
        """Property lease without expiry should NOT be flagged (indefinite by nature)."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',50000,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO extractions VALUES (1,NULL,'property_lease',0,NULL,0,0,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, MISSING_EXPIRY_CONDITION)
        assert 1 not in result

    def test_skips_cemetery(self, db):
        """Cemetery contract without expiry should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',50000,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO extractions VALUES (1,NULL,'cemetery',0,NULL,0,0,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, MISSING_EXPIRY_CONDITION)
        assert 1 not in result

    def test_skips_easement(self, db):
        """Easement without expiry should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',50000,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO extractions VALUES (1,NULL,'easement_encumbrance',0,NULL,0,0,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, MISSING_EXPIRY_CONDITION)
        assert 1 not in result

    def test_skips_low_value(self, db):
        """Low-value contract (under 10k) without expiry should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',5000,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO extractions VALUES (1,NULL,'professional_consulting',0,NULL,0,0,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, MISSING_EXPIRY_CONDITION)
        assert 1 not in result

    def test_skips_contract_with_expiry(self, db):
        """Contract WITH expiry date should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',50000,NULL,NULL,'2027-12-31',NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, MISSING_EXPIRY_CONDITION)
        assert 1 not in result


# =========================================================================
# terminated_company — only flag if NO active RÚZ entry for the ICO
# =========================================================================

TERMINATED_COMPANY_CONDITION = (
    "z.dodavatel_ico IS NOT NULL AND z.dodavatel_ico != '' "
    "AND z.dodavatel_ico IN (SELECT cin FROM ruz_entities WHERE terminated_on IS NOT NULL AND cin IS NOT NULL) "
    "AND z.dodavatel_ico NOT IN (SELECT cin FROM ruz_entities WHERE terminated_on IS NULL AND cin IS NOT NULL)"
)


class TestTerminatedCompany:
    def test_flags_fully_terminated(self, db):
        """Company where ALL RÚZ entries are terminated should be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Dead s.r.o.','44556677','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO ruz_entities VALUES ('44556677','Dead s.r.o.',NULL,'2020-01-01',NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, TERMINATED_COMPANY_CONDITION)
        assert 1 in result

    def test_skips_ico_with_active_entry(self, db):
        """ICO that has both terminated AND active entries should NOT be flagged (restructured)."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Generali Poisťovňa','35709332','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        # Old entity terminated
        db.execute("INSERT INTO ruz_entities VALUES ('35709332','GSK Financial',NULL,'2022-11-24',NULL,NULL,NULL,NULL,NULL)")
        # New entity active (same ICO)
        db.execute("INSERT INTO ruz_entities VALUES ('35709332','Generali Poisťovňa',NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, TERMINATED_COMPANY_CONDITION)
        assert 1 not in result

    def test_skips_active_company(self, db):
        """Company with only active entries should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Active s.r.o.','44556677','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO ruz_entities VALUES ('44556677','Active s.r.o.',NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, TERMINATED_COMPANY_CONDITION)
        assert 1 not in result

    def test_skips_no_ruz_entry(self, db):
        """Company not in RÚZ at all should NOT be flagged."""
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Unknown s.r.o.','44556677','Obec','00111222',100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, TERMINATED_COMPANY_CONDITION)
        assert 1 not in result


# =========================================================================
# weekend_signing — exclude 1st/last of month, require high value
# =========================================================================

# DuckDB-compatible version (strftime takes date first)
WEEKEND_SIGNING_CONDITION = (
    "z.datum_podpisu IS NOT NULL AND z.datum_podpisu != '' "
    "AND cast(strftime(TRY_CAST(z.datum_podpisu AS DATE), '%w') as integer) IN (0, 6) "
    "AND z.suma > 50000 "
    "AND cast(strftime(TRY_CAST(z.datum_podpisu AS DATE), '%d') as integer) NOT IN (1, 28, 29, 30, 31)"
)


class TestWeekendSigning:
    def test_flags_high_value_weekend_mid_month(self, db):
        """High-value contract signed on Saturday mid-month should be flagged."""
        # 2026-03-07 is a Saturday
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',100000,NULL,'2026-03-07',NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, WEEKEND_SIGNING_CONDITION)
        assert 1 in result

    def test_skips_first_of_month_weekend(self, db):
        """Contract signed on 1st of month (Sunday) should NOT be flagged (admin date)."""
        # 2026-02-01 is a Sunday
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',100000,NULL,'2026-02-01',NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, WEEKEND_SIGNING_CONDITION)
        assert 1 not in result

    def test_skips_last_of_month_weekend(self, db):
        """Contract signed on 31st (Saturday) should NOT be flagged."""
        # 2026-01-31 is a Saturday
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',100000,NULL,'2026-01-31',NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, WEEKEND_SIGNING_CONDITION)
        assert 1 not in result

    def test_skips_low_value_weekend(self, db):
        """Low-value weekend contract should NOT be flagged."""
        # 2026-03-07 is Saturday
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',5000,NULL,'2026-03-07',NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, WEEKEND_SIGNING_CONDITION)
        assert 1 not in result

    def test_skips_weekday(self, db):
        """Weekday contract should NOT be flagged."""
        # 2026-03-09 is Monday
        db.execute("INSERT INTO zmluvy VALUES (1,'zmluva','Firma','44556677','Obec','00111222',100000,NULL,'2026-03-09',NULL,NULL,NULL,NULL,NULL,NULL)")
        result = run_sql_flag(db, WEEKEND_SIGNING_CONDITION)
        assert 1 not in result


# =========================================================================
# nace_mismatch — expanded compatible NACE sectors
# =========================================================================

# Import the same mapping used in production
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

from ingest import _NACE_COMPATIBLE


class TestNaceMismatch:
    def test_school_property_lease_not_flagged(self):
        """School (NACE 85) doing property_lease should NOT be a mismatch."""
        assert 85 in _NACE_COMPATIBLE['property_lease']

    def test_sports_club_property_lease_not_flagged(self):
        """Sports club (NACE 93) doing property_lease should NOT be a mismatch."""
        assert 93 in _NACE_COMPATIBLE['property_lease']

    def test_culture_property_lease_not_flagged(self):
        """Cultural org (NACE 90) doing property_lease should NOT be a mismatch."""
        assert 90 in _NACE_COMPATIBLE['property_lease']

    def test_public_admin_property_lease_not_flagged(self):
        """Public admin (NACE 84) doing property_lease should NOT be a mismatch."""
        assert 84 in _NACE_COMPATIBLE['property_lease']

    def test_telecom_utilities_not_flagged(self):
        """Telecom (NACE 61) providing utilities should NOT be a mismatch."""
        assert 61 in _NACE_COMPATIBLE['utilities']

    def test_forestry_property_lease_not_flagged(self):
        """Forestry (NACE 02) doing property_lease should NOT be a mismatch."""
        assert 2 in _NACE_COMPATIBLE['property_lease']

    def test_veterinary_consulting_not_flagged(self):
        """Veterinary (NACE 75) doing professional_consulting should NOT be a mismatch."""
        assert 75 in _NACE_COMPATIBLE['professional_consulting']

    def test_real_mismatch_still_caught(self):
        """Restaurant (NACE 56) doing software_it should still be a mismatch."""
        assert 56 not in _NACE_COMPATIBLE['software_it']

    def test_real_mismatch_construction_insurance(self):
        """Construction (NACE 41) doing insurance should still be a mismatch."""
        assert 41 not in _NACE_COMPATIBLE['insurance']
