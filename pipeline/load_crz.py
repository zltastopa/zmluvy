"""Parse CRZ daily XML export into SQLite for Datasette."""
import confpath  # noqa: F401

import xml.etree.ElementTree as ET
import sqlite_utils
import sys
import os

from settings import get_path

REZORT_MAP = {
    "0": "",
    "118974": "agrokomplex NÁRODNÉ VÝSTAVISKO, štátny podnik",
    "127698": "Akadémia umení v Banskej Bystrici",
    "119593": "Audiovizuálny fond",
    "121236": "Ekonomická univerzita v Bratislave",
    "1552144": "Elektronický kontraktačný systém",
    "3065787": "Fond na podporu kultúry národnostných menšín",
    "2249797": "Fond na podporu umenia",
    "779485": "Fond na podporu vzdelávania",
    "408599": "Fond národného majetku SR",
    "748131": "Fond výtvarných umení",
    "356772": "Generálna prokuratúra Slovenskej republiky",
    "131444": "Hudobný fond",
    "7524853": "Jadrová energetická spoločnosť Slovenska",
    "5870791": "Kancelária Najvyššieho správneho súdu Slovenskej republiky",
    "2782449": "Kancelária Najvyššieho súdu Slovenskej republiky",
    "356965": "Kancelária Národnej rady Slovenskej republiky",
    "381892": "Kancelária prezidenta Slovenskej republiky",
    "659697": "Kancelária Rady pre rozpočtovú zodpovednosť",
    "2263690": "Kancelária Súdnej rady SR",
    "390844": "Kancelária Ústavného súdu Slovenskej republiky",
    "473568": "Kancelária verejného ochrancu práv",
    "119840": "Katolícka univerzita v Ružomberku",
    "1476896": "Literárny fond",
    "773800": "Matica slovenská",
    "406837": "MH Teplárenský holding, a.s.",
    "8898224": "Ministerstvo cestovného ruchu a športu SR",
    "114573": "Ministerstvo dopravy a výstavby SR",
    "114725": "Ministerstvo financií SR",
    "114499": "Ministerstvo hospodárstva SR",
    "2473554": "Ministerstvo investícií, regionálneho rozvoja a informatizácie",
    "114692": "Ministerstvo kultúry SR",
    "114495": "Ministerstvo obrany SR",
    "114727": "Ministerstvo pôdohospodárstva a rozvoja vidieka SR",
    "114533": "Ministerstvo práce, sociálnych vecí a rodiny SR",
    "114497": "Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky",
    "114565": "Ministerstvo spravodlivosti SR",
    "114723": "Ministerstvo vnútra SR",
    "114654": "Ministerstvo zahraničných vecí SR",
    "114571": "Ministerstvo zdravotníctva SR",
    "114535": "Ministerstvo životného prostredia SR",
    "356929": "Najvyšší kontrolný úrad Slovenskej republiky",
    "358680": "Najvyšší súd SR",
    "114652": "Národný bezpečnostný úrad",
    "518667": "Národný inšpektorát práce",
    "1455994": "Ostatné",
    "316407": "Pôžičkový fond pre začínajúcich pedagógov",
    "119589": "Prešovská univerzita v Prešove",
    "114490": "Protimonopolný úrad SR",
    "779519": "Rada pre vysielanie a retransmisiu",
    "402088": "Recyklačný fond v likvidácii",
    "114752": "Rozhlas a televizia Slovenska",
    "363849": "Slovenská akadémia vied",
    "358672": "Slovenská elektrizačná prenosová sústava, a.s.",
    "4055741": "Slovenská informačná služba",
    "2572185": "Slovenská obchodná a priemyselná komora",
    "115447": "Slovenská poľnohospodárska univerzita v Nitre",
    "119006": "Slovenská technická univerzita v Bratislave",
    "526459": "Slovenské národné stredisko pre ľudské práva",
    "358675": "Slovenský pozemkový fond",
    "114493": "Sociálna poisťovňa",
    "114690": "Správa štátnych hmotných rezerv SR",
    "114733": "Štatistický úrad SR",
    "307882": "Študentský pôžičkový fond",
    "6215909": "Subjekty verejnej správy",
    "117199": "Technická univerzita v Košiciach",
    "117205": "Technická univerzita vo Zvolene",
    "117113": "Tlačová agentúra Slovenskej republiky",
    "118692": "Trenčianska univerzita Alexandra Dubčeka v Trenčíne",
    "117729": "Trnavská univerzita so sídlom v Trnave",
    "116991": "Univerzita J. Selyeho v Komárne",
    "116293": "Univerzita Komenského v Bratislave",
    "115013": "Univerzita Konštantína Filozofa v Nitre",
    "119217": "Univerzita Mateja Bela v Banskej Bystrici",
    "116277": "Univerzita Pavla Jozefa Šafárika v Košiciach",
    "115434": "Univerzita sv. Cyrila a Metoda v Trnave",
    "117166": "Univerzita veterinárskeho lekárstva a farmácie v Košiciach",
    "114731": "Úrad geodézie, kartografie a katastra SR",
    "114501": "Úrad jadrového dozoru SR",
    "2862619": "Úrad komisára pre deti",
    "3956955": "Úrad komisára pre osoby so zdravotným postihnutím",
    "561884": "Úrad na ochranu osobných údajov Slovenskej republiky",
    "5742083": "Úrad na ochranu oznamovateľov protispoločenskej činnosti",
    "10269138": "Úrad podpredsedu vlády SR vlády pre Plán obnovy a znalostnú ekonomiku",
    "6706801": "Úrad podpredsedu vlády, ktorý neriadi ministerstvo",
    "115005": "Úrad pre dohľad nad výkonom auditu",
    "360085": "Úrad pre dohľad nad zdravotnou starostlivosťou",
    "114735": "Úrad pre normalizáciu, metrológiu a skúšobníctvo SR",
    "356704": "Úrad pre reguláciu sieťových odvetví",
    "114729": "Úrad pre verejné obstarávanie",
    "114489": "Úrad priemyselného vlastníctva SR",
    "114688": "Úrad vlády SR",
    "3805640": "Ústav pamäti národa",
    "3953379": "Ústredie ekumenickej pastoračnej služby v OS SR a OZ SR",
    "114503": "Všeobecná zdravotná poisťovňa a.s.",
    "131437": "Vysoká škola múzických umení",
    "117084": "Vysoká škola výtvarných umení v Bratislave",
    "115836": "Žilinská univerzita v Žiline",
}

DRUH_MAP = {"1": "zmluva", "2": "objednávka"}
ZDROJ_MAP = {"0": "neznámy", "1": "CRZ", "2": "rezort", "3": "organizácia"}


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
    attachments = []

    for z in root:
        cid = get_text(z, "ID")
        contract_id = int(cid) if cid.isdigit() else None

        # Collect all attachments
        prilohy = z.find("prilohy")
        if prilohy is not None:
            for p in prilohy:
                fname = get_text(p, "dokument1") or get_text(p, "dokument")
                if fname:
                    att_id = get_text(p, "ID")
                    attachments.append({
                        "id": int(att_id) if att_id.isdigit() else None,
                        "zmluva_id": contract_id,
                        "nazov": get_text(p, "nazov"),
                        "subor": fname,
                        "url": f"https://www.crz.gov.sk/data/att/{fname}",
                    })

        rezort_id = get_text(z, "rezort")
        druh_raw = get_text(z, "druh")
        zdroj_raw = get_text(z, "zdroj")
        uvo = get_text(z, "uvo")

        contracts.append({
            "id": contract_id,
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
            "druh": DRUH_MAP.get(druh_raw, druh_raw),
            "rezort_id": rezort_id,
            "rezort": REZORT_MAP.get(rezort_id, ""),
            "zdroj": ZDROJ_MAP.get(zdroj_raw, zdroj_raw),
            "uvo_url": uvo,
            "crz_url": f"https://www.crz.gov.sk/zmluva/{cid}/" if cid else "",
        })

    return contracts, attachments


def main():
    if len(sys.argv) < 2:
        print("Usage: python load_crz.py <xml_file> [xml_file2 ...]")
        sys.exit(1)

    db_path = get_path("CRZ_DB_PATH", "crz.db")
    fresh = not os.path.exists(db_path)
    db = sqlite_utils.Database(db_path)

    all_contracts = []
    all_attachments = []
    for path in sys.argv[1:]:
        print(f"Parsing {path}...")
        contracts, attachments = parse_xml(path)
        all_contracts.extend(contracts)
        all_attachments.extend(attachments)

    print(f"Loaded {len(all_contracts)} contracts, {len(all_attachments)} attachments")

    # Deduplicate by id (keep latest)
    seen = {}
    for c in all_contracts:
        if c["id"] is not None:
            seen[c["id"]] = c
        else:
            seen[id(c)] = c
    contracts = list(seen.values())
    print(f"After dedup: {len(contracts)} unique contracts")

    # Deduplicate attachments by id
    att_seen = {}
    for a in all_attachments:
        if a["id"] is not None:
            att_seen[a["id"]] = a
        else:
            att_seen[id(a)] = a
    attachments = list(att_seen.values())
    print(f"After dedup: {len(attachments)} unique attachments")

    # Upsert contracts
    table = db["zmluvy"]
    table.insert_all(contracts, pk="id", replace=True)

    # Upsert attachments
    att_table = db["prilohy"]
    att_table.insert_all(attachments, pk="id", foreign_keys=[("zmluva_id", "zmluvy")], replace=True)

    # Rezort lookup table
    rezort_rows = [{"id": k, "nazov": v} for k, v in REZORT_MAP.items() if k != "0" and v]
    db["rezorty"].insert_all(rezort_rows, pk="id", replace=True)

    # Set up FTS and indexes only on fresh DB or if FTS table doesn't exist
    if fresh or "zmluvy_fts" not in db.table_names():
        table.enable_fts(
            ["nazov_zmluvy", "dodavatel", "objednavatel", "poznamka", "popis", "dodavatel_adresa"],
            create_triggers=True,
            tokenize="unicode61",
            replace=True,
        )
    else:
        table.populate_fts(["nazov_zmluvy", "dodavatel", "objednavatel", "poznamka", "popis", "dodavatel_adresa"])

    table.create_index(["dodavatel_ico"], if_not_exists=True)
    table.create_index(["objednavatel_ico"], if_not_exists=True)
    table.create_index(["suma"], if_not_exists=True)
    table.create_index(["rezort_id"], if_not_exists=True)
    table.create_index(["druh"], if_not_exists=True)
    table.create_index(["datum_zverejnenia"], if_not_exists=True)
    att_table.create_index(["zmluva_id"], if_not_exists=True)

    print(f"Done! {len(contracts)} contracts, {len(attachments)} attachments in {db_path}")
    print(f"Run: uv run datasette {db_path}")


if __name__ == "__main__":
    main()
