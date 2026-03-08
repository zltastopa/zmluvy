"""Import Financial Administration (Finančná správa) XML exports into crz.db.

Downloads are from: https://report.financnasprava.sk/
Source page: https://www.financnasprava.sk/sk/elektronicke-sluzby/verejne-sluzby/zoznamy/exporty-z-online-informacnych

Tables created:
  - fs_tax_debtors        (ds_dsdd) — daňoví dlžníci
  - fs_vat_deregistered   (ds_dphv) — vymazaní platitelia DPH
  - fs_vat_dereg_reasons  (ds_dphz) — dôvody na zrušenie DPH registrácie
  - fs_corporate_tax      (ds_dppos) — daň z príjmov PO

Usage:
    uv run python import_fs_exports.py
"""

import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

from settings import get_path, normalize_company_name

DB_PATH = get_path("CRZ_DB_PATH", "crz.db")
EXPORT_DIR = Path("data/fs_exports")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _text(item, tag):
    el = item.find(tag)
    return el.text.strip() if el is not None and el.text else None


def _float(item, tag):
    v = _text(item, tag)
    if v:
        try:
            return float(v.replace(",", "."))
        except ValueError:
            return None
    return None


def import_tax_debtors(db):
    """Import ds_dsdd — Zoznam daňových dlžníkov."""
    xml_path = EXPORT_DIR / "ds_dsdd" / "ds_dsdd.xml"
    if not xml_path.exists():
        print(f"  SKIP: {xml_path} not found")
        return

    db.execute("DROP TABLE IF EXISTS fs_tax_debtors")
    db.execute("""
        CREATE TABLE fs_tax_debtors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazov TEXT NOT NULL,
            nazov_normalized TEXT,
            suma REAL,
            ulica TEXT,
            psc TEXT,
            obec TEXT
        )
    """)
    db.execute("CREATE INDEX idx_fs_taxdebt_norm ON fs_tax_debtors(nazov_normalized)")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows = []
    for item in root.iter("ITEM"):
        nazov = _text(item, "NAZOV_SUBJEKTU")
        if not nazov:
            continue
        rows.append((
            nazov,
            normalize_company_name(nazov),
            _float(item, "CIASTKA"),
            _text(item, "ULICA_CISLO"),
            _text(item, "PSC"),
            _text(item, "OBEC"),
        ))

    db.executemany(
        "INSERT INTO fs_tax_debtors (nazov, nazov_normalized, suma, ulica, psc, obec) VALUES (?,?,?,?,?,?)",
        rows,
    )
    db.commit()
    print(f"  fs_tax_debtors: {len(rows)} rows imported")


def import_vat_deregistered(db):
    """Import ds_dphv — Zoznam vymazaných platiteľov DPH."""
    xml_path = EXPORT_DIR / "ds_dphv" / "ds_dphv.xml"
    if not xml_path.exists():
        print(f"  SKIP: {xml_path} not found")
        return

    db.execute("DROP TABLE IF EXISTS fs_vat_deregistered")
    db.execute("""
        CREATE TABLE fs_vat_deregistered (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ico TEXT,
            ic_dph TEXT,
            nazov TEXT,
            obec TEXT,
            psc TEXT,
            adresa TEXT,
            rok_porusenia INTEGER,
            dat_zverejnenia TEXT,
            dat_vymazu TEXT
        )
    """)
    db.execute("CREATE INDEX idx_fs_vatdereg_ico ON fs_vat_deregistered(ico)")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows = []
    for item in root.iter("ITEM"):
        rows.append((
            _text(item, "ICO"),
            _text(item, "IC_DPH"),
            _text(item, "NAZOV"),
            _text(item, "OBEC"),
            _text(item, "PSC"),
            _text(item, "ADRESA"),
            int(_text(item, "ROK_PORUSENIA") or 0) or None,
            _text(item, "DAT_ZVEREJNENIA"),
            _text(item, "DAT_VYMAZU"),
        ))

    db.executemany(
        "INSERT INTO fs_vat_deregistered (ico, ic_dph, nazov, obec, psc, adresa, rok_porusenia, dat_zverejnenia, dat_vymazu) VALUES (?,?,?,?,?,?,?,?,?)",
        rows,
    )
    db.commit()
    print(f"  fs_vat_deregistered: {len(rows)} rows imported")


def import_vat_dereg_reasons(db):
    """Import ds_dphz — dôvody na zrušenie DPH registrácie (aktívne prípady)."""
    xml_path = EXPORT_DIR / "ds_dphz" / "ds_dphz.xml"
    if not xml_path.exists():
        print(f"  SKIP: {xml_path} not found")
        return

    db.execute("DROP TABLE IF EXISTS fs_vat_dereg_reasons")
    db.execute("""
        CREATE TABLE fs_vat_dereg_reasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ico TEXT,
            ic_dph TEXT,
            nazov TEXT,
            obec TEXT,
            psc TEXT,
            adresa TEXT,
            rok_porusenia INTEGER,
            dat_zverejnenia TEXT
        )
    """)
    db.execute("CREATE INDEX idx_fs_vatdrgr_ico ON fs_vat_dereg_reasons(ico)")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows = []
    for item in root.iter("ITEM"):
        rows.append((
            _text(item, "ICO"),
            _text(item, "IC_DPH"),
            _text(item, "NAZOV"),
            _text(item, "OBEC"),
            _text(item, "PSC"),
            _text(item, "ADRESA"),
            int(_text(item, "ROK_PORUSENIA") or 0) or None,
            _text(item, "DAT_ZVEREJNENIA"),
        ))

    db.executemany(
        "INSERT INTO fs_vat_dereg_reasons (ico, ic_dph, nazov, obec, psc, adresa, rok_porusenia, dat_zverejnenia) VALUES (?,?,?,?,?,?,?,?)",
        rows,
    )
    db.commit()
    print(f"  fs_vat_dereg_reasons: {len(rows)} rows imported")


def import_corporate_tax(db):
    """Import ds_dppos — Zoznam subjektov s výškou dane z príjmov PO."""
    xml_path = EXPORT_DIR / "ds_dppos" / "ds_dppos.xml"
    if not xml_path.exists():
        print(f"  SKIP: {xml_path} not found")
        return

    db.execute("DROP TABLE IF EXISTS fs_corporate_tax")
    db.execute("""
        CREATE TABLE fs_corporate_tax (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ico TEXT,
            dic TEXT,
            nazov TEXT,
            obec TEXT,
            psc TEXT,
            ulica TEXT,
            stat TEXT,
            obdobie_od TEXT,
            obdobie_do TEXT,
            vyrubena_dan REAL,
            dodat_vyrubena_dan REAL,
            danova_strata REAL
        )
    """)
    db.execute("CREATE INDEX idx_fs_corptax_ico ON fs_corporate_tax(ico)")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows = []
    for item in root.iter("ITEM"):
        rows.append((
            _text(item, "ICO"),
            _text(item, "DIC"),
            _text(item, "NAZOV_DS"),
            _text(item, "OBEC"),
            _text(item, "PSC"),
            _text(item, "ULICA_CISLO"),
            _text(item, "STAT"),
            _text(item, "ZDAN_OBDOBIE_OD"),
            _text(item, "ZDAN_OBDOBIE_DO"),
            _float(item, "VYRUBENA_DAN"),
            _float(item, "DODAT_VYRUBENA_DAN"),
            _float(item, "DANOVA_STRATA"),
        ))

    db.executemany(
        "INSERT INTO fs_corporate_tax (ico, dic, nazov, obec, psc, ulica, stat, obdobie_od, obdobie_do, vyrubena_dan, dodat_vyrubena_dan, danova_strata) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    db.commit()
    print(f"  fs_corporate_tax: {len(rows)} rows imported")


def main():
    print("Importing FS XML exports into crz.db...")
    db = get_db()
    import_tax_debtors(db)
    import_vat_deregistered(db)
    import_vat_dereg_reasons(db)
    import_corporate_tax(db)

    # Summary: check overlap with CRZ suppliers
    print("\n--- Overlap with CRZ contract suppliers ---")

    # Tax debtors (name match)
    count = db.execute("""
        SELECT count(DISTINCT z.id) FROM zmluvy z
        JOIN fs_tax_debtors t ON t.nazov_normalized = (
            SELECT nazov_normalized FROM fs_tax_debtors
            WHERE nazov_normalized IS NOT NULL
            LIMIT 0
        )
    """).fetchone()
    # Simpler: just count unique normalized names that match
    tax_match = db.execute("""
        SELECT count(DISTINCT z.id)
        FROM zmluvy z, fs_tax_debtors t
        WHERE t.nazov_normalized IS NOT NULL
        AND t.nazov_normalized != ''
        AND z.dodavatel IS NOT NULL
        AND t.nazov_normalized = ?
        LIMIT 0
    """, ("__impossible__",)).fetchone()

    # VAT deregistered (ICO match)
    vat_dereg = db.execute("""
        SELECT count(DISTINCT z.id) FROM zmluvy z
        JOIN fs_vat_deregistered v ON v.ico = replace(z.dodavatel_ico, ' ', '')
        WHERE v.ico IS NOT NULL
    """).fetchone()[0]
    print(f"  VAT deregistered suppliers with CRZ contracts: {vat_dereg}")

    # VAT dereg reasons (ICO match)
    vat_risk = db.execute("""
        SELECT count(DISTINCT z.id) FROM zmluvy z
        JOIN fs_vat_dereg_reasons v ON v.ico = replace(z.dodavatel_ico, ' ', '')
        WHERE v.ico IS NOT NULL
    """).fetchone()[0]
    print(f"  VAT dereg-risk suppliers with CRZ contracts: {vat_risk}")

    # Corporate tax with loss (ICO match)
    tax_loss = db.execute("""
        SELECT count(DISTINCT z.id) FROM zmluvy z
        JOIN fs_corporate_tax t ON t.ico = replace(z.dodavatel_ico, ' ', '')
        WHERE t.danova_strata > 0
    """).fetchone()[0]
    print(f"  Suppliers declaring tax loss with CRZ contracts: {tax_loss}")

    db.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
