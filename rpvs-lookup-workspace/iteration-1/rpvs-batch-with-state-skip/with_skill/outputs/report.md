# RPVS lookup: sql-analytics najdovia -- Alanata, Ministerstvo investicii, ejoin

## Sumar
- Firmy skontrolovane: 3
- Preskocene (statny sektor): 1 (Ministerstvo investicii, ICO 50349287)
- RPVS lookup vykonany: 2
- Registrovane v RPVS: 1 z 2
- Neregistrovane (>100K EUR): 1 (Alanata, a.s.)
- Prekryv UBO: ziadny
- Zlte stopy: 2

---

## Firma 1: Alanata, a.s. (ICO 54629331)

### RPVS status
| Pole | Hodnota |
|---|---|
| Stav | **NEREGISTROVANY** |
| Cislo vlozky | -- |
| Datum zapisu | -- |
| Opravnena osoba | -- |
| Posledne overenie | -- |

Vyhladavanie na rpvs.gov.sk s ICO 54629331 vratilo **0 zaznamov** ("Zaznamy 0 az 0 z celkom 0, vyfiltrovane spomedzi 51 429 zaznamov").

### Konecni uzivatelia vyhod
Nie je mozne zistit -- firma nie je registrovana v RPVS.

### CRZ kontrakty (>100K EUR)
| ID | Nazov | Objednavatel | Suma (EUR) |
|---|---|---|---|
| 11926714 | Zmluva o poskytnuti sluzieb | Ministerstvo dopravy SR | 14 833 000.50 |
| 11712493 | Kupna zmluva | Narodna agentura pre sietove a elektronicke sluzby | 8 010 344.25 |
| 11980294 | Ramcova zmluva c. 3/2026/111 na zabezpecenie sluzieb podpory, prevadzky a rozvoja IS AGIS | Podohospodarska platobna agentura | 4 232 651.40 |
| 11966109 | Kupna | Narodna agentura pre sietove a elektronicke sluzby | 3 231 534.72 |
| 11854319 | Zmluva na dodavku licencii a o poskytnuti sluzieb technickej podpory a rozvoja | Socialna poistovna, ustredie | 2 458 030.77 |

**Celkovy objem:** 35 322 081.88 EUR v 14 kontraktoch.

### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| **Chybajuca registracia v RPVS** | DANGER | Firma s 35.3M EUR v CRZ kontraktoch nie je registrovana v RPVS. Kazdy partner verejneho sektora prijimajuci >100K EUR verejnych prostriedkov musi byt registrovany. |
| Neznami konecni uzivatelia vyhod | DANGER | Nie je mozne zistit, kto skutocne profituje z 35M EUR verejnych kontraktov. |

---

## Firma 2: Ministerstvo investicii, regionalneho rozvoja a informatizacie SR (ICO 50349287)

### RPVS status
| Pole | Hodnota |
|---|---|
| Stav | **PRESKOCENE -- STATNY SEKTOR** |

Ministerstvo investicii je statna institucia (ministerstvo). Statne entity nemaju sukromnych konecnych uzivatelov vyhod a nepodliehaju registracii v RPVS.

**CRZ objem:** 337 661 786.02 EUR v 362 kontraktoch (ako dodavatel).

### Zlte stopy
Ziadne -- statny sektor, RPVS sa neuplatnuje.

---

## Firma 3: ejoin s.r.o. (ICO 51900921)

### RPVS status
| Pole | Hodnota |
|---|---|
| Stav | **Platny** |
| Cislo vlozky | 33271 |
| Datum zapisu | 12.03.2021 |
| Opravnena osoba | AK PG s.r.o. (ICO 36866911, Vapenna 16927/7, Bratislava - Ruzinov) |
| Posledne overenie | 02.01.2026 (oznamenie 12.01.2026, typ: k 31. decembru kalendarneho roku) |
| Datum aktualizacie | 14.03.2026 |

Detail: https://rpvs.gov.sk/rpvs/Partner/Partner/Detail/33271

### Konecni uzivatelia vyhod
| Meno | Datum narodenia | Statna prislusnost | Adresa | Verejny funkcionar |
|---|---|---|---|---|
| Michal Vasek | 31.01.1985 | Slovenska republika | Partizanska 1280/10, 018 41 Dubnica nad Vahom | Nie |
| Mgr. Klaudia Vasekova | 30.03.1987 | Slovenska republika | Borcice 174, 01853 Borcice | Nie |

Verejni funkcionari v riadiacej strukture: ziadni.
Udelene pokuty: ziadne.
Kvalifikovany podnet: ziadny.

### CRZ kontrakty
| ID | Nazov | Objednavatel | Suma (EUR) |
|---|---|---|---|
| 11874721 | Zmluva o vystavbe a prevadzkovani nabijacej infrastruktury v meste Sabinov | Mesto Sabinov | 97 217.95 |
| 12001689 | Zmluva o dielo c. 1/2026/OV | Mesto Nove Mesto nad Vahom | 87 369.18 |
| 9170286 | Zmluva o dielo | Presovsky samospravny kraj | 66 657.60 |

**Celkovy objem:** 251 244.73 EUR v 4 kontraktoch.

### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Trojity dlznik | DANGER | Firma je sucastne: danovy dlznik FS, dlznik Socialnej poistovne, dlznik VSZP, a danovo nespolahlivy dodavatel (flagy z CRZ red_flags). |
| Registracia v RPVS OK | INFO | Firma je platne registrovana v RPVS od 12.03.2021, overenie aktualne (01/2026). |

---

## Prekryv UBO

**Ziadny prekryv najdeny.**

- Alanata, a.s. -- UBO neznami (nie je v RPVS)
- ejoin s.r.o. -- UBO: Michal Vasek, Mgr. Klaudia Vasekova
- Ministerstvo investicii -- statny sektor (n/a)

Krizova kontrola objednavatelov ukazala, ze Alanata a ejoin nemaju spolocneho objednavatela -- ich kontrakty su od uplne odlisnych institucii (Alanata: NASES, Ministerstvo dopravy, Socialna poistovna; ejoin: Mesto Sabinov, Presovsky samospravny kraj).

---

## Hlavne zistenia

1. **Alanata, a.s. (ICO 54629331) -- NEREGISTROVANA v RPVS napriek 35.3M EUR v CRZ kontraktoch.** Toto je najzavaznejsia zlta stopa. Zakon vyzaduje registraciu pre kazdeho partnera verejneho sektora s kontraktmi nad 100K EUR. Nie je mozne overit, kto su konecni uzivatelia vyhod tejto firmy prostrednictvom RPVS.

2. **ejoin s.r.o. (ICO 51900921) -- registrovana v RPVS, ale trojity dlznik.** Konecni uzivatelia vyhod su Michal Vasek (nar. 1985) a Klaudia Vasekova (nar. 1987), obaja zo Slovenskej republiky, nie su verejni funkcionari. Firma vsak ma viacnasobne dlznicke flagy.

3. **Ministerstvo investicii (ICO 50349287)** -- statna institucia, RPVS sa neuplatnuje. Preskocene.

4. **Prekryv UBO medzi firmami neexistuje** -- kedze Alanata nie je v RPVS, nie je mozne plne porovnat. Odporuca sa dalsie skumanie vlastnickej struktury Alanata cez foaf.sk alebo obchodny register.

---

**Lookup ukonceny.** Skontrolovane 3 firmy, 1 preskocena (statny sektor), 1 registrovana v RPVS (ejoin), 1 neregistrovana napriek 35M EUR v kontraktoch (Alanata). Odporucame: (a) preverit preco Alanata nie je v RPVS, (b) skontrolovat Alanata cez foaf.sk a obchodny register, (c) overit vztah Michal Vasek / Klaudia Vasekova k dalsim dodavatelom verejneho sektora.

*Tieto zistenia su stopy, nie verdikty.*
