"""Load Financial Administration tax reliability data (ds_iz_ran.xml) into SQLite.

Source: Finančná správa SR (Slovak Financial Administration)
Download: https://report.financnasprava.sk/ds_iz_ran.zip
Info: https://www.financnasprava.sk/sk/elektronicke-sluzby/verejne-sluzby/zoznamy/detail/_5cd6a827-0ee0-4028-8982-4d8bb1de3008
File: ds_iz_ran.zip → ds_iz_ran.xml (CC0 license, ~680K subjects, updated daily)

The file contains the "Index daňovej spoľahlivosti" (Tax Reliability Index)
for all registered tax subjects in Slovakia:
  - "vysoko spoľahlivý" — highly reliable taxpayer
  - "spoľahlivý"        — reliable taxpayer
  - "menej spoľahlivý"  — less reliable taxpayer (tax debts, late filings, etc.)

Creates table `tax_reliability` (keyed on ICO) which can be joined against
`zmluvy.dodavatel_ico` or `zmluvy.objednavatel_ico` to flag contracts with
unreliable parties.

Usage:
    python load_tax_reliability.py                    # default: ds_iz_ran.xml
    python load_tax_reliability.py path/to/file.xml   # custom path
"""
import confpath  # noqa: F401

import xml.etree.ElementTree as ET
import sqlite_utils
import sys

from settings import get_path


def main():
    xml_path = sys.argv[1] if len(sys.argv) > 1 else "ds_iz_ran.xml"
    db = sqlite_utils.Database(get_path("CRZ_DB_PATH", "crz.db"))

    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    datum = root.findtext("DatumAktualizacieZoznamu", "")
    print(f"Data as of: {datum}")

    ds = root.find("DS_IZ_RAN")
    rows = []
    for item in ds.findall("ITEM"):
        ico = (item.findtext("ICO") or "").strip()
        if not ico:
            continue
        rows.append({
            "ico": ico,
            "dic": (item.findtext("DIC") or "").strip(),
            "nazov": (item.findtext("NAZOV_SUBJEKTU") or "").strip(),
            "status": (item.findtext("IDS") or "").strip(),
            "obec": (item.findtext("OBEC") or "").strip(),
            "psc": (item.findtext("PSC") or "").strip(),
            "ulica": (item.findtext("ULICA_CISLO") or "").strip(),
            "stat": (item.findtext("STAT") or "").strip(),
        })

    print(f"Loaded {len(rows)} subjects")

    table = db["tax_reliability"]
    table.insert_all(rows, pk="ico", replace=True)
    table.create_index(["status"], if_not_exists=True)

    # Summary
    from collections import Counter
    statuses = Counter(r["status"] for r in rows)
    for s, c in statuses.most_common():
        print(f"  {s}: {c}")

    # Cross-reference: flag contracts with unreliable suppliers
    n = db.execute("""
        select count(*) from zmluvy z
        join tax_reliability t on z.dodavatel_ico = t.ico
        where t.status = 'menej spoľahlivý'
    """).fetchone()[0]
    print(f"\nContracts with 'menej spoľahlivý' supplier: {n}")

    print(f"Done! Table 'tax_reliability' in {get_path('CRZ_DB_PATH', 'crz.db')}")


if __name__ == "__main__":
    main()
