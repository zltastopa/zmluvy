"""Parse CRZ daily XML export into SQLite for Datasette."""
import xml.etree.ElementTree as ET
import sqlite_utils
import sys

def get_text(el, tag, default=""):
    node = el.find(tag)
    return node.text.strip() if node is not None and node.text else default

def get_amount(el, tag):
    val = get_text(el, tag, "0")
    try:
        a = float(val)
        return a if a > 0 else None
    except ValueError:
        return None

def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    contracts = []
    for z in root:
        # Get attachment info
        att_name, att_url = "", ""
        prilohy = z.find("prilohy")
        if prilohy is not None:
            for p in prilohy:
                for field in ["dokument1", "dokument"]:
                    fname = get_text(p, field)
                    if fname:
                        att_name = fname
                        att_url = f"https://www.crz.gov.sk/data/att/{fname}"
                        break
                if att_name:
                    break

        cid = get_text(z, "ID")
        contracts.append({
            "id": int(cid) if cid.isdigit() else None,
            "nazov_zmluvy": get_text(z, "predmet"),
            "cislo_zmluvy": get_text(z, "nazov"),
            "dodavatel": get_text(z, "zs2"),
            "dodavatel_ico": get_text(z, "ico"),
            "dodavatel_adresa": get_text(z, "sidlo"),
            "objednavatel": get_text(z, "zs1"),
            "objednavatel_ico": get_text(z, "ico1"),
            "objednavatel_adresa": get_text(z, "sidlo1"),
            "suma": get_amount(z, "suma_zmluva"),
            "suma_celkom": get_amount(z, "suma_spolu"),
            "datum_zverejnenia": get_text(z, "datum_zverejnene"),
            "datum_podpisu": get_text(z, "datum"),
            "datum_ucinnosti": get_text(z, "datum_ucinnost"),
            "platnost_do": get_text(z, "datum_platnost_do") if get_text(z, "datum_platnost_do") != "0000-00-00" else "",
            "poznamka": get_text(z, "poznamka"),
            "popis": get_text(z, "popis"),
            "typ": "zmluva" if get_text(z, "typ") == "1" else "dodatok" if get_text(z, "typ") == "2" else get_text(z, "typ"),
            "stav": "aktívna" if get_text(z, "stav") == "2" else "zrušená" if get_text(z, "stav") == "3" else get_text(z, "stav"),
            "priloha": att_name,
            "priloha_url": att_url,
            "crz_url": f"https://www.crz.gov.sk/zmluva/{cid}/" if cid else "",
        })
    return contracts


def main():
    if len(sys.argv) < 2:
        print("Usage: python load_crz.py <xml_file> [xml_file2 ...]")
        sys.exit(1)

    db = sqlite_utils.Database("crz.db", recreate=True)

    all_contracts = []
    for path in sys.argv[1:]:
        print(f"Parsing {path}...")
        all_contracts.extend(parse_xml(path))

    print(f"Loaded {len(all_contracts)} contracts total")

    # Deduplicate by id (keep latest)
    seen = {}
    for c in all_contracts:
        if c["id"] is not None:
            seen[c["id"]] = c
        else:
            seen[id(c)] = c
    contracts = list(seen.values())
    print(f"After dedup: {len(contracts)} unique contracts")

    # Insert into SQLite
    table = db["zmluvy"]
    table.insert_all(contracts, pk="id", replace=True)

    # Enable full-text search across all the useful fields
    table.enable_fts(
        ["nazov_zmluvy", "dodavatel", "objednavatel", "poznamka", "popis", "dodavatel_adresa"],
        create_triggers=True,
        tokenize="unicode61",
    )

    # Add useful indexes
    table.create_index(["dodavatel_ico"], if_not_exists=True)
    table.create_index(["objednavatel_ico"], if_not_exists=True)
    table.create_index(["suma"], if_not_exists=True)

    print(f"Done! {len(contracts)} contracts in crz.db")
    print(f"Run: uv run datasette crz.db")


if __name__ == "__main__":
    main()
