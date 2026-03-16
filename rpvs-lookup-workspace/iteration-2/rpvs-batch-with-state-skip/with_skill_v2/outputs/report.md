# RPVS lookup: sql-analytics najdy — Alanata, Ministerstvo investicii, ejoin

## Sumar
- Firmy skontrolovane: 3
- Statne entity (preskocene): 1 (Ministerstvo investicii, ICO 50349287)
- Registrovane v RPVS: 2 z 2 (sukromne firmy)
- Neregistrovane (>100K EUR): 0
- Prekryv UBO: ziadny
- Zlte stopy: 1

---

## Pre-check: Statne entity

| Firma | ICO | Dovod preskocenia |
|---|---|---|
| Ministerstvo investicii, regionalneho rozvoja a informatizacie SR | 50349287 | Statna institucia (ministerstvo) — nema sukromnych konecnych uzivatelov vyhod |

Ministerstvo investicii je statny organ s 362 kontraktmi v CRZ (336M EUR). RPVS registracia sa na statne entity nevztahuje.

---

## Firma 1: Alanata a. s. (ICO 54629331)

### RPVS status
| Pole | Hodnota |
|---|---|
| Stav | **Platny** |
| Cislo vlozky | 37284 |
| Datum zapisu | 16.07.2022 |
| Pravna forma | Akciova spolocnost |
| Adresa sidla | Krasovskeho 0/14, 85101 Bratislava - Petrzalka |
| Opravnena osoba | Malata, Pruzinsky, Hegedus & Partners s. r. o. (ICO 47239921) |
| Posledne overenie | 02.01.2026 (oznamenie 07.01.2026, typ: k 31. decembru) |

### Konecni uzivatelia vyhod
| Meno | Datum narodenia | Statna prislusnost | Verejny funkcionar |
|---|---|---|---|
| Ing. Stefan Petergac | 02.10.1962 | Slovenska republika | Nie |
| Ing. Jozef Mokry | 23.04.1968 | Slovenska republika | Nie |
| Ing. Peter Kotuliak | 28.09.1967 | Slovenska republika | Nie |

### CRZ kontrakty (>100K EUR)
| ID | Nazov | Objednavatel | Suma (EUR) |
|---|---|---|---|
| 11926714 | Zmluva o poskytvani sluzieb | Ministerstvo dopravy SR | 14,833,000.50 |
| 11712493 | Kupna zmluva | Narodna agentura pre sietove a elektronicke sluzby | 8,010,344.25 |
| 11980294 | Ramcova zmluva c. 3/2026/111 (AGIS) | Podohospodarska platobna agentura | 4,232,651.40 |
| 11966109 | Kupna | Narodna agentura pre sietove a elektronicke sluzby | 3,231,534.72 |
| 11854319 | Zmluva na dodavku licencii a sluzieb | Socialna poistovna, ustredie | 2,458,030.77 |
| 11922893 | Kupna zmluva | Generalna prokuratura SR | 723,960.78 |
| 11922668 | Kupna zmluva | Generalna prokuratura SR | 675,977.25 |
| 12014312 | Zmluva na dodania sluzieb podpory HW | Narodna agentura pre sietove a elektronicke sluzby | 416,593.30 |
| 11887707 | Zmluva na dodanie softverovych licencii | Narodne centrum zdravotnickych informacii | 255,840.00 |
| 12054560 | Zmluva o poskytvani sluzieb a o najme | Narodne centrum zdravotnickych informacii | 244,647.00 |

**Celkom: 35.3M EUR v 14 kontraktoch** napriec 7 rozsahlymi statnym instituciam (ministerstvo, agentura, poistovna, prokuratura, nemocnicne systemy).

### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Mlada firma, velke kontrakty | WARNING | RPVS zapis 16.07.2022, firma ziskala 35M EUR v statnych kontraktoch za menej nez 4 roky |

---

## Firma 2: ejoin, s.r.o. (ICO 51900921)

### RPVS status
| Pole | Hodnota |
|---|---|
| Stav | **Platny** |
| Cislo vlozky | 33271 |
| Datum zapisu | 12.03.2021 |
| Pravna forma | Spolocnost s rucenim obmedzenym |
| Adresa sidla | Sturova 0/1, 01841 Dubnica nad Vahom |
| Opravnena osoba | AK PG s.r.o. (ICO 36866911) |
| Posledne overenie | 02.01.2026 (oznamenie 12.01.2026, typ: k 31. decembru) |

### Konecni uzivatelia vyhod
| Meno | Datum narodenia | Statna prislusnost | Verejny funkcionar |
|---|---|---|---|
| Michal Vasek | 31.01.1985 | Slovenska republika | Nie |
| Mgr. Klaudia Vasekova | 30.03.1987 | Slovenska republika | Nie |

Poznamka: Vasek / Vasekova — pravdepodobne manzelsky par (rovnake priezvisko, oba z okolia Dubnice nad Vahom/Borcice).

### CRZ kontrakty
| ID | Nazov | Objednavatel | Suma (EUR) |
|---|---|---|---|
| 11874721 | Zmluva o vystavbe a prevadzkovani nabijacej infrastruktury | Mesto Sabinov | 97,217.95 |
| 12001689 | Zmluva o dielo c. 1/2026/OV | Mesto Nove Mesto nad Vahom | 87,369.18 |
| 9170286 | Zmluva o dielo | Presovsky samospravny kraj | 66,657.60 |
| 11971207 | Dodatok c. 1 k zmluve (Sabinov) | Mesto Sabinov | 0.00 |

**Celkom: 251,244.73 EUR v 4 kontraktoch.** Kontext: trojity dlznik (flag z sql-analytics).

### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| (ziadne RPVS-specificke nalezy) | — | Firma je riadne registrovana, overenie aktualne, ziadne pokuty ani podnety |

---

## Prekryv UBO

### Porovnanie konecnych uzivatelov vyhod

| UBO | Alanata a. s. | ejoin, s.r.o. |
|---|---|---|
| Ing. Stefan Petergac | ANO | nie |
| Ing. Jozef Mokry | ANO | nie |
| Ing. Peter Kotuliak | ANO | nie |
| Michal Vasek | nie | ANO |
| Mgr. Klaudia Vasekova | nie | ANO |

**Prekryv: ZIADNY.** Ziadny konecny uzivatel vyhod nie je spolocny medzi Alanata a ejoin. Firmy nemaju spolocnych vlastnikov.

### Spolocni objednavatelia

Ziadny spolocny objednavatel medzi Alanata a ejoin v CRZ databaze. Firmy posobili v uplne roznych segmentoch:
- **Alanata** — IT sluzby a licencie pre velke statne institucie (ministerstva, NASES, Socialna poistovna)
- **ejoin** — nabijacia infrastruktura pre male samospravne celky (mesta, kraje)

---

## Celkove zhrnutie

| Firma | RPVS | UBO pocet | Verejny funkcionar | Pokuty | Prekryv |
|---|---|---|---|---|---|
| Alanata a. s. | Platny (od 07/2022) | 3 | Nie | Ziadne | — |
| Ministerstvo investicii | *Preskocene (statna entita)* | — | — | — | — |
| ejoin, s.r.o. | Platny (od 03/2021) | 2 | Nie | Ziadne | — |

**Hlavne zistenia:**
1. Obe sukromne firmy su riadne registrovane v RPVS s aktualnymi overeniami (januar 2026).
2. Ziadny prekryv konecnych uzivatelov vyhod — ziadna koordinovana siet.
3. Ziadny konecny uzivatel vyhod nie je verejny funkcionar.
4. Ziadne pokuty ani kvalifikovane podnety.
5. Poznamka k Alanata: Relativne mlada firma (RPVS zapis 07/2022) s velmi vysokym objemom statnych kontraktov (35M EUR). Opravnena osoba je renomovana advokatska kancelaria (Malata, Pruzinsky, Hegedus & Partners).
6. Poznamka k ejoin: Dva UBO s rovnakym priezviskom (Vasek/Vasekova) — pravdepodobne rodinny par vlastniaci firmu.

---

**Lookup ukonceny.** RPVS registracia oboch sukromnych firiem je v poriadku. Ziadny prekryv UBO, ziadne verejne funkcionari, ziadne pokuty. Flag "trojity dlznik" pre ejoin nesuvisi s RPVS registraciou — je to flag z ineho zdroja (sql-analytics). Pre Alanata stoji za pozornost rapidny rast kontraktov pre mladu firmu, ale z hladiska RPVS je vsetko v sulade.
