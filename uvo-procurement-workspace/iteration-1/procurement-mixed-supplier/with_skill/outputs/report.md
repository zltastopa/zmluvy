# UVO procurement lookup: Swietelsky-Slovakia spol. s r.o. (ICO 00896225)

## Sumar
- Celkovy pocet kontraktov v CRZ: 10 (celkovo 9 648 195.02 EUR)
- Kontrakty s UVO odkazom: 3 z 10
- Kontrakty BEZ obstaravania (>50 000 EUR, bez dodatkov): 6
- Zlte stopy: 4 WARNING, 1 DANGER (z procurement hladiska)

**Poznamka:** Tato analyza pokryva kroky 1-2 zo SKILL.md (DB-first strategia). Kroky 3-6 (browser lookup na UVO) neboli vykonane.

---

## Prehlad vsetkych kontraktov

| # | ID | Nazov | Objednavatel | Suma (EUR) | UVO odkaz | Typ |
|---|---|---|---|---|---|---|
| 1 | 12065312 | DODATOK c. 3 - Cyklotrasa Vranov nad Toplou | Mesto Vranov nad Toplou | 2 950 881.94 | NENAJDENY | zmluva (dodatok v nazve) |
| 2 | 12063119 | DODATOK c. 2 - Cyklotrasa Vranov nad Toplou | Mesto Vranov nad Toplou | 2 936 428.72 | NENAJDENY | zmluva (dodatok v nazve) |
| 3 | 12029209 | Zmluva o dielo | Obec Jezersko | 1 760 000.00 | NENAJDENY | zmluva |
| 4 | 11707199 | Dodatok c. 1 - Modernizacia ul. Holleho, Martin | Mesto Martin | 916 431.07 | NENAJDENY | zmluva (dodatok v nazve) |
| 5 | 11979775 | Parkovacia plocha ul. Osuského, Petrzalka | MC Bratislava-Petrzalka | 336 458.57 | ANO | zmluva |
| 6 | 11919045 | Zmluva o dielo | Mesto Bardejov | 297 308.61 | ANO | zmluva |
| 7 | 11626757 | Modernizacia miestnych komunikacii | Obec Vysna Hutka | 258 077.06 | NENAJDENY | zmluva |
| 8 | 12010690 | Mlatovy chodnik velky Drazdiak - sever | MC Bratislava-Petrzalka | 106 788.70 | ANO | zmluva |
| 9 | 11993021 | Dodatok c.1 k Zmluva o dielo Z26-013-0049 | Obec Rohoznik | 85 820.35 | NENAJDENY | zmluva (dodatok v nazve) |
| 10 | 11986337 | Dodatok c. 2 k Zmluve o dielo c. 387/2025 | Mesto Skalica | 0.00 | NENAJDENY | zmluva (dodatok v nazve) |

---

## Kontrakty S UVO odkazom (Step 1)

### Kontrakt 5: Parkovacia plocha ul. Osuského, Bratislava-Petrzalka (336 458.57 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 11979775 |
| Dodavatel | Swietelsky-Slovakia spol. s r.o. (ICO 00896225) |
| Objednavatel | Mestska cast Bratislava-Petrzalka |
| Suma | 336 458.57 EUR |
| Datum zverejnenia | 2026-02-11 |
| UVO URL | https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-profilov/zakazky/6556?cHash=93df1f1e32ac522425a9b081b6683602 |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Danovo nespolahlivy subjekt v zmluve | DANGER | VKS ELTO s.r.o. (ICO: 44020465) |
| Skryte entity | WARNING | 1 skryta entita |
| Skryta entita je dodavatel | WARNING | VKS ELTO s.r.o. (ICO: 44020465) je tiez dodavatel v inych zmluvach |

#### Hodnotenie
UVO odkaz vedie na profil obstaravatela MC Petrzalka. Obstaravanie prebehlo, ale kontrakt obsahuje skrytu entitu (VKS ELTO s.r.o.), ktora je danovo nespolahlivy subjekt. Nutne overit rolu tejto entity v zakazke.

---

### Kontrakt 6: Zmluva o dielo - Mesto Bardejov (297 308.61 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 11919045 |
| Dodavatel | Swietelsky-Slovakia spol. s.r.o. (ICO 00896225) |
| Objednavatel | Mesto Bardejov |
| Suma | 297 308.61 EUR |
| Datum zverejnenia | 2026-01-30 |
| UVO URL | https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek/detail/537023?cHash=58c4b64597ecc5130491ddc3ce6ff205 |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Neuvedena platnost | INFO | - |
| Dodavatel nie je v RUZ | INFO | - |

#### Hodnotenie
Kontrakt ma UVO odkaz na detail zakazky. Ziadne zavazne zlte stopy z CRZ dat. Pre uplne hodnotenie by bolo potrebne otvorit UVO stranku a overit pocet ponuk, typ postupu a vitaznu cenu.

---

### Kontrakt 8: Mlatovy chodnik velky Drazdiak - sever (106 788.70 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 12010690 |
| Dodavatel | Swietelsky-Slovakia spol. s r.o. (ICO 00896225) |
| Objednavatel | Mestska cast Bratislava-Petrzalka |
| Suma | 106 788.70 EUR |
| Datum zverejnenia | 2026-02-19 |
| UVO URL | https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek/detail/548008 |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Pokuty zvyhodnuju dodavatela | DANGER | Zmluvne pokuty su nastavene v prospech dodavatela |
| Zdielany podpisujuci | WARNING | Ing. Jan Hrcka podpisuje za 14 roznych dodavatelov |

#### Hodnotenie
Kontrakt ma UVO odkaz, co je pozitivne. Ale obsahuje DANGER flag na pokuty zvyhodnujuce dodavatela a zdielaneho podpisujuceho (14 roznych dodavatelov). Pre uplne hodnotenie nutne overit UVO detail - pocet ponuk a ci bola sutaz.

---

## Kontrakty BEZ UVO odkazu (Step 2)

### Kontrakt 1: DODATOK c. 3 - Cyklotrasa Vranov nad Toplou (2 950 881.94 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 12065312 |
| Dodavatel | Swietelsky-Slovakia spol. s r.o. (ICO 00896225) |
| Objednavatel | Mesto Vranov nad Toplou |
| Suma | 2 950 881.94 EUR |
| Datum zverejnenia | 2026-03-05 |
| UVO URL | NENAJDENY |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Skryte entity | WARNING | 2 skryte entity |
| Skryta entita je dodavatel | WARNING | SPORTFINAL s.r.o. (ICO: 44149671) je tiez dodavatel v inych zmluvach |
| Zdielany podpisujuci | WARNING | Ing. Jan Ragan podpisuje za 12 roznych dodavatelov |

#### Hodnotenie
Najvacsi kontrakt v portfoliu (takmer 3M EUR). Napriek nazvu "DODATOK c. 3" je v CRZ evidovany ako typ "zmluva", nie "Dodatok". Chybajuci UVO odkaz pri stavebnej zakazke nad 50 000 EUR je procurement zlta stopa. Zaroven obsahuje skrytu entitu SPORTFINAL s.r.o., ktora je tiez dodavatel v inych zmluvach - mozna subdodavka alebo konzorcium. Existuje aj DODATOK c. 2 (ID 12063119, 2 936 428.72 EUR) s rovnakymi flagmi, co naznacuje, ze ide o ten isty projekt s navyseniami.

---

### Kontrakt 2: DODATOK c. 2 - Cyklotrasa Vranov nad Toplou (2 936 428.72 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 12063119 |
| Dodavatel | Swietelsky-Slovakia spol. s r.o. (ICO 00896225) |
| Objednavatel | Mesto Vranov nad Toplou |
| Suma | 2 936 428.72 EUR |
| Datum zverejnenia | 2026-03-04 |
| UVO URL | NENAJDENY |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Skryte entity | WARNING | 2 skryte entity |
| Skryta entita je dodavatel | WARNING | SPORTFINAL s.r.o. (ICO: 44149671) je tiez dodavatel v inych zmluvach |
| Zdielany podpisujuci | WARNING | Ing. Jan Ragan podpisuje za 12 roznych dodavatelov |

#### Hodnotenie
Druhy dodatok k rovnakemu projektu cyklotrasy. Suma je takmer rovnaka ako DODATOK c. 3 - pravdepodobne ide o kumulativnu sumu celeho diela. Bez UVO odkazu pri stavebnom kontakte tejto velkosti je to vyrazna zlta stopa. Povodna zmluva o dielo nie je v nasej DB alebo bola zverejnena pod inym dodavatelom/ICO.

---

### Kontrakt 3: Zmluva o dielo - Obec Jezersko (1 760 000.00 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 12029209 |
| Dodavatel | Swietelsky-Slovakia spol. s r. o. (ICO 00896225) |
| Objednavatel | Obec Jezersko |
| Suma | 1 760 000.00 EUR |
| Datum zverejnenia | 2026-02-24 |
| UVO URL | NENAJDENY |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Neuvedena platnost | INFO | - |
| Dodavatel nie je v RUZ | INFO | - |

#### Hodnotenie
Velky stavebny kontrakt (1.76M EUR) pre malu obec bez UVO odkazu. Toto je vyrazna procurement zlta stopa. Stavebne zakazky nad 50 000 EUR musia prejst verejnym obstaravanim podla zakona o verejnom obstaravani. Chybajuci LLM extrakcny zaznam (service_category je prazdne) naznacuje, ze zmluva nebola este plne spracovana.

---

### Kontrakt 4: Dodatok c. 1 - Modernizacia ul. Holleho, Martin (916 431.07 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 11707199 |
| Dodavatel | Swietelsky-Slovakia spol. s.r.o. (ICO 00896225) |
| Objednavatel | Mesto Martin |
| Suma | 916 431.07 EUR |
| Datum zverejnenia | 2025-12-08 |
| UVO URL | NENAJDENY |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Neuvedena platnost | INFO | - |
| Dodavatel nie je v RUZ | INFO | - |

#### Hodnotenie
Dodatok c. 1 k zmluve o dielo pre modernizaciu komunikacie v Martine. Suma 916K EUR bez UVO odkazu. Je mozne, ze povodna zmluva o dielo mala UVO odkaz, ale tento dodatok ho nema. Povodna zmluva by mala byt overena v UVO systeme.

---

### Kontrakt 7: Modernizacia miestnych komunikacii - Obec Vysna Hutka (258 077.06 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 11626757 |
| Dodavatel | Swietelsky-Slovakia spol. s r.o. (ICO 00896225) |
| Objednavatel | Obec Vysna Hutka |
| Suma | 258 077.06 EUR |
| Datum zverejnenia | 2025-11-20 |
| UVO URL | NENAJDENY |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Neuvedena platnost | INFO | - |
| Dodavatel nie je v RUZ | INFO | - |

#### Hodnotenie
Stavebna zakazka na modernizaciu komunikacii za 258K EUR bez UVO odkazu. Nad limitom 50 000 EUR pre stavebne prace. Obstaravanie by malo byt overitelne v UVO systeme.

---

### Kontrakt 9: Dodatok c.1 k Zmluva o dielo - Obec Rohoznik (85 820.35 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 11993021 |
| Dodavatel | Swietelsky-Slovakia spol. s.r.o. (ICO 00896225) |
| Objednavatel | Obec Rohoznik |
| Suma | 85 820.35 EUR |
| Datum zverejnenia | 2026-02-14 |
| UVO URL | NENAJDENY |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Zdielany podpisujuci | WARNING | Mgr. Peter Svara podpisuje za 5 roznych dodavatelov |

#### Hodnotenie
Dodatok k zmluve o dielo za 85K EUR. Nad limitom pre stavebne prace. Zdielany podpisujuci je mierna zlta stopa.

---

### Kontrakt 10: Dodatok c. 2 k Zmluve o dielo - Mesto Skalica (0.00 EUR)

#### CRZ data
| Pole | Hodnota |
|---|---|
| ID | 11986337 |
| Dodavatel | SWIETELSKY Slovakia, s.r.o. (ICO 00896225) |
| Objednavatel | Mesto Skalica |
| Suma | 0.00 EUR |
| Datum zverejnenia | 2026-02-12 |
| UVO URL | NENAJDENY |

#### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| Skryta cena | WARNING | Suma nie je uvedena |
| Zdielany podpisujuci | WARNING | Mgr. Olga Luptakova podpisuje za 8 roznych dodavatelov |

#### Hodnotenie
Dodatok s nulovou sumou a skrytou cenou. Pravdepodobne zmena podmienok bez financneho dopadu alebo nebol uvedena suma. Nizka priorita z procurement hladiska.

---

## Celkove hodnotenie

### Procurement profil Swietelsky-Slovakia spol. s r.o.

Swietelsky je velka stavebna firma (dcerska spolocnost rakuskeho Swietelsky AG) s 10 kontraktmi v CRZ za celkovo **9 648 195 EUR**. Z procurement hladiska:

**Pozitivne zistenia:**
- 3 z 10 kontraktov maju UVO odkaz, co preukazuje, ze firma sa zucastnuje formalnych obstaravani
- Dva kontrakty s UVO odkazom su od MC Bratislava-Petrzalka, co naznacuje systematickejsi pristup vacsich objednavatelov

**Zlte stopy - procurement:**

| Zlta stopa | Severity | Pocet | Detail |
|---|---|---|---|
| Velke kontrakty bez UVO odkazu | WARNING | 6 | Kontrakty >50K EUR bez evidencie obstaravania |
| Cyklotrasa Vranov - dva "dodatky" za ~3M EUR | WARNING | 2 | Povodna zmluva o dielo chyba v DB, oba dodatky su bez UVO |
| Obec Jezersko - 1.76M EUR bez UVO | WARNING | 1 | Velky kontrakt pre malu obec |
| Danovo nespolahlivy subjekt | DANGER | 1 | VKS ELTO s.r.o. v kontakte Petrzalka |
| Pokuty zvyhodnuju dodavatela | DANGER | 1 | Chodnik Drazdiak |

**Klucove otazky na dalsie preverenie:**
1. Cyklotrasa Vranov nad Toplou - kde je povodna zmluva o dielo? Prebehlo obstaravanie?
2. Obec Jezersko - ako mala obec obstarala stavebnu zakazku za 1.76M EUR?
3. VKS ELTO s.r.o. - aka je rola tejto danovo nespolahlivej entity v kontakte Petrzalka?
4. Pre kontrakty s UVO odkazmi - kolko ponuk bolo podanych? Bola realna sutaz?

**Obmedzenia:** Tato analyza je zalozena len na CRZ databaze (kroky 1-2). Pre uplny obraz by bolo potrebne otvorit UVO stranky (krok 3-6) a overit detaily obstaravaní - typ postupu, pocet ponuk, vitazne ceny a konkurenciu.

---

**Lookup ukonceny.** Swietelsky-Slovakia ma 3 z 10 kontraktov s UVO odkazom. 6 kontraktov nad 50 000 EUR nema evidenciu obstaravania, pricom najvacsi (Cyklotrasa Vranov ~3M EUR a Obec Jezersko 1.76M EUR) predstavuju vyrazne procurement zlte stopy. Toto su stopy, nie verdikty - chybajuci UVO odkaz v CRZ databaze neznamena automaticky, ze obstaravanie neprebehlo, ale vyzaduje dalsie preverenie.
