# Kriticka validacia: Q4 2025 nalezy -- Skutocne podozrive, alebo nevinna vysvetlenie?

Datum: 2026-03-16
Zdroj dat: CRZ databaza (crz.db, overene oproti zmluvy.zltastopa.sk)

> Upozornenie: Nasledujuce zistenia su **stopy, nie verdikty**. Sluzia ako podklad pre dalsie preverenie.

---

## Suhrn

| # | Nalez | Povodne tvrdenie | Skutocnost v CRZ | Verdikt |
|---|-------|-------------------|-------------------|---------|
| 1 | TATRA DEFENCE SYSTEMS | 1.03 mld EUR od MO SR | Potvrdzene -- ramcova zmluva ID 11760561, suma 1 032 689 734 EUR | **CONFIRMED** |
| 2 | Environmentalny fond -> VV s.p. | 30M EUR okruhla suma | Potvrdzene -- dotacia z EU Modernizacneho fondu pre statny podnik | **DISMISSED** |
| 3 | Fond na podporu vzdelavania -> Hengerics | 457 zmluv, 4.2M EUR | Hengerics ma 1 zmluvu za 11 571 EUR (studentska pozicka). Chybna atribucia. | **DISMISSED** |
| 4 | Hruzova Zuzana, Bc. | 506 zmluv, 13.6M EUR bez ICO | 10 zmluv za 150 EUR (prenajom kinosaly po 15 EUR). Cisla su nespravne. | **DISMISSED** |
| 5 | Eduardo Carmona | 49 zmluv pre APVV po 700 EUR | 1 zmluva za 700 EUR (autorsky posudok). Standardna prax APVV. | **DISMISSED** |

---

## 1. TATRA DEFENCE SYSTEMS s.r.o. -- 1 032 689 734 EUR od Ministerstva obrany SR

**Verdikt: CONFIRMED**

### Fakty z databazy
- **Zmluva ID:** 11760561, zverejnena 2025-12-17
- **Nazov:** RAMCOVA ZMLUVA c. SEMOD-179/2025-7
- **Dodavatel:** TATRA DEFENCE SYSTEMS s.r.o. (ICO 08993289)
- **Objednavatel:** Ministerstvo obrany SR
- **Suma:** 1 032 689 734 EUR
- **Typ:** zmluva (ramcova)
- **UVO URL:** neuvedena
- **CRZ URL:** https://www.crz.gov.sk/zmluva/11760561/
- **Dalsie zmluvy tohto dodavatela:** ziadne -- jedina zmluva v CRZ
- **Extractions:** ziadne (zmluva nebola LLM-extrahovana)

### Zlte stopy v databaze
| Stopa | Zavaznost | Detail |
|-------|-----------|--------|
| `not_in_ruz` | info | Firma nie je v Registri uctovnych zavierok |

### Overenie nevinnych vysvetleni

**Co hovori za legitimnost:**
- **Ramcova zmluva =/= realna utrata.** Suma 1.03 mld EUR je maximalny strop pre buduce objednavky na ~7 rokov. Skutocne cerpanie bude postupne a moze byt vyrazne nizsie.
- **Obrana je legitimne drahy sektor.** Vojenske vozidla, obrnena technika a zbrojne systemy bezne dosahuju stamilionove az miliardove sumy v cele EU.
- **TATRA DEFENCE SYSTEMS** (ICO 08993289) je sucastou skupiny TATRA / CSG (Czechoslovak Group) -- znamej stredoeuropskej zbrojovky vyrábajucej vojenske nakladne vozidla a obrnenu techniku.
- **Vojenske zakazky** maju legitimnu vynimku z verejneho obstaravania podla cl. 346 ZFEU a zakona c. 343/2015 Z. z., co vysvetluje absenciu UVO URL.

**Co zostava podozrive a zasluhuje dalsi dozor:**
- Firma **nie je v ziadnom registri** v databaze (RUZ, tax_reliability, vszp_debtors) -- neobvykle pre firmu s miliardovym kontraktom.
- **Jedina zmluva** v celom CRZ -- ziadna predchadzajuca historia statnych zakaziek.
- **Chyba UVO link** -- aj ked vojenske vynimky existuju, pri takejto sume by bolo vhodne overit, ci bola vyuzita legitimne.

### Odporucanie
Overit cez FinStat (ICO 08993289) financny profil firmy, cez RPVS konecnych uzivatelov vyhod a cez foaf.sk korporatnu siet. Overit na UVO, ci existuje zaznam o tomto obstaravani.

---

## 2. Environmentalny fond -- 30 000 000 EUR pre Vodohospodarsku vystavbu, s.p.

**Verdikt: DISMISSED**

### Fakty z databazy
- **Zmluva ID:** 11849535, zverejnena 2026-01-14
- **Nazov:** Zmluva o poskytnuti podpory z Environmentalneho fondu formou dotacie z prostriedkov Modernizacneho fondu
- **Dodavatel:** VODOHOSPODARSKA VYSTAVBA, STATNY PODNIK (ICO 00156752)
- **Objednavatel:** Environmentalny fond
- **Suma:** 30 000 000 EUR
- **Projekt:** Innovacia a modernizacia Vodnej elektrarne Gabcikovo (z LLM extrakcie)
- **Financovanie:** Modernizacny fond EU (schema reference: "Modernizacny fond")
- **Subcontractor:** Basler & Hofmann Slovakia s.r.o. (vypracovanie dokumentacie stavebneho zameru)
- Druha zmluva pre toho isteho objednavatela: ID 11849557 za 12 149 252.55 EUR

### Zlte stopy v databaze
| Stopa | Zavaznost | Detail |
|-------|-----------|--------|
| `amount_outlier` | warning | 30M EUR = 3.6x stddev pre grant_subsidy (priemer 538 142 EUR) |
| `hidden_entities` | warning | Subcontractor Basler & Hofmann Slovakia s.r.o. |
| `signatory_overlap` | warning | Ing. Marek Giba, MBA podpisuje za 9 roznych dodavatelov |
| `missing_expiry` | info | Neuvedena platnost |
| `not_in_ruz` | info | Dodavatel nie je v RUZ |

### Overenie nevinnych vysvetleni

**Vsetky zlte stopy maju nevine vysvetlenie:**

1. **Okruhla suma 30M EUR** -- typicka pre grantove/dotacne zmluvy, kde sa stanovuje strop financovania podla rozpoctoveho ramca EU fondu. V rovnakom obdobi Env. fond poskytol aj 27.2M a 12.1M EUR dalsim prijemcom z toho isteho Modernizacneho fondu.

2. **Vodohospodarska vystavba je statny podnik** (s.p.) -- 100% vlastneny statom. Dotacia stat -> statny podnik na modernizaciu statnej infrastruktury (VE Gabcikovo) je bezna prax.

3. **Modernizacny fond** je EU mechanizmus na financovanie energetickych a environmentalnych projektov. Cislo zmluvy "MoF..." to potvrdzuje.

4. **Signatory overlap** (Ing. Marek Giba, MBA za 9 dodavatelov) -- Giba je generalny riaditel Environmentalneho fondu a podpisuje ako **kupujuci/objednavatel**, nie dodavatel. Logicky podpisuje vsetky zmluvy fondu -- falozny pozitiv automatickeho systemu.

5. **Hidden entity** (Basler & Hofmann) -- subdodavatel na projektovu dokumentaciu je standardna prax pri velkych stavebnych projektoch.

### Zaver
Standardna dotacia z EU Modernizacneho fondu pre statny podnik na modernizaciu vodnej elektrarne. Ziadne realne podozrenie.

---

## 3. Fond na podporu vzdelavania -> Tomas Hengerics -- udajne 457 zmluv za 4.2M EUR

**Verdikt: DISMISSED (chybna atribucia)**

### Fakty z databazy

**Tomas Hengerics v CRZ:**
- Presne **1 zmluva** (ID 11641718): *Zmluva o pozicke*
- Dodavatel: Fond na podporu vzdelavania
- Objednavatel (prijemca): Tomas Hengerics
- Suma: **11 571.13 EUR**
- Ide o **studentsku pozicku** -- Fond poskytuje financne prostriedky studentovi.

**Fond na podporu vzdelavania (ICO 47245531) celkovo:**
- V CRZ evidovany ako **dodavatel** v **596 zmluvach** s celkovou sumou **10 530 231 EUR**
- Vsetky zmluvy su **studentske pozicky** -- Fond poskytuje pozicky stovkam individualnych studentov
- Kazdy student ma typicky 1 zmluvu (max 2)
- Top prijemca (Katarina Sulcova) ma 2 zmluvy za 20 000 EUR

### Overenie
- Cislo **"457 zmluv za 4.2M EUR"** neodpoveda Hengericsovi (1 zmluva, 11 571 EUR).
- Toto cislo by mohlo zodpovedat **celemu Fondu** v nejakom casovom useku (napr. Q4 2025), ale bolo chybne pripisane jednej osobe.
- Fond na podporu vzdelavania je legitimna vladna institucia zriadena zakonom c. 396/2012 Z. z.

### Zaver
**Chybna atribucia.** Velky pocet zmluv patri Fondu ako celku (studentske pozicky pre stovky studentov), nie jednej osobe. Hengerics je bezny prijemca studentskej pozicky.

---

## 4. Hruzova Zuzana, Bc. -- udajne 506 zmluv za 13.6M EUR bez ICO

**Verdikt: DISMISSED (hrube chybne data)**

### Fakty z databazy
- Hruzova Zuzana, Bc. ma v CRZ presne **10 zmluv**, vsetky pre **Obec Varin**
- Kazda zmluva je za **15.00 EUR** -- celkova suma **150.00 EUR**
- Nazvy zmluv: "najom sala Z. Hruzova", "prenajom kinosala p. Hruzova", "cvicenie" atd.
- Ide o opakovany **prenajom obecnej kinosaly** na jednorazove podujatia (cvicenia a pod.)
- Casovy rozsah: 2024-09 az 2026-01 (cca raz za mesiac)
- Jedina zlta stopa na vsetkych 10 zmluvach: `missing_ico` (info) -- fyzicka osoba bez ICO

### Overenie
| Tvrdenie | Skutocnost | Odchylka |
|----------|------------|----------|
| 506 zmluv | 10 zmluv | 50.6x |
| 13.6M EUR | 150 EUR | 90 666x |
| Podozrive bez ICO | Fyzicka osoba = bezne bez ICO | -- |

- Pani Hruzova si jednoducho opakovane prenajima obecnu kinosalu vo Varine za 15 EUR na akciu.
- Obec Varin zverejnuje aj tieto miniaturne zmluvy, co je prejavom transparentnosti.
- Chybajuce ICO je standardne pre fyzicke osoby -- nie su povinne mat ICO.

### Zaver
**Uplne chybny najd.** Povodne tvrdenie (506 zmluv, 13.6M EUR) sa odchyluje od reality (10 zmluv, 150 EUR) o niekolko radov. Pravdepodobne doslo k chybe v agregacii dat alebo k zamene s inou entitou.

---

## 5. Eduardo Carmona -- udajne 49 zmluv pre APVV po 700 EUR

**Verdikt: DISMISSED (hrube chybne data)**

### Fakty z databazy
- Eduardo Carmona ma v CRZ presne **1 zmluvu** (ID 11490797):
  - Nazov: *Autorska zmluva o dielo*
  - Objednavatel: Agentura na podporu vyskumu a vyvoja (APVV)
  - Suma: **700 EUR**
  - Datum: 2025-10-27
  - Zlte stopy: `missing_expiry` (info), `missing_ico` (info)

**APVV a autorske zmluvy:**
- APVV ma v databaze celkovo **61 autorskych zmluv o dielo** s celkovou sumou 27 760 EUR
- Priemerna suma autorskej zmluvy APVV: ~455 EUR (rozsah 440 -- 4 800 EUR)
- Su to odmeny pre vedcov za recenzie, posudky a expertne hodnotenia
- Zmluvy okolo 700 EUR (600-800 EUR) maju v DB iba 2 dodavatelia: Carmona (700 EUR) a Zachar Podolinska (780 EUR)

### Overenie
| Tvrdenie | Skutocnost | Odchylka |
|----------|------------|----------|
| 49 zmluv | 1 zmluva | 49x |
| Opakovany vzor | Jednorazova zmluva | -- |

- Eduardo Carmona je s najvacsou pravdepodobnostou zahranicny vedec/recenzent prizvaný APVV na odborny posudok.
- Suma 700 EUR za autorsku zmluvu o dielo je v plnom sulade s beznou praxou APVV.
- Tvrdenie o 49 zmluvach sa neda overit -- APVV nema ziadneho dodavatela s viac ako 9 zmluvami.

### Zaver
**Uplne chybny najd.** Jedna zmluva za 700 EUR na autorsky posudok je standardna prax vedeckej agentury. Cislo 49 nema oporu v datach.

---

## Celkove zistenia a metodologicka poznamka

### Skore validacie: 1 CONFIRMED, 4 DISMISSED

Z 5 skumanych nalezov:
- **1 CONFIRMED** (TATRA DEFENCE) -- data v CRZ potvrdzuju existenciu zmluvy za 1.03 mld EUR, ale s kontextom ramcovej zmluvy a obranneho sektora. Zasluhuje dalsi dozor.
- **4 DISMISSED** -- z toho:
  - 1x nevinna vysvetlenie (Environmentalny fond -- legitímna EU dotacia)
  - 3x **hrube chyby v povodnych cislach** (Hengerics, Hruzova, Carmona)

### Systmicka chyba v povodnej analyze

Tri z piatich nalezov (c. 3, 4, 5) obsahovali **radove nespravne cisla**:

| Nalez | Tvrdeny pocet zmluv | Skutocny pocet | Tvrdena suma | Skutocna suma |
|-------|---------------------|----------------|--------------|---------------|
| Hengerics | 457 | 1 | 4.2M EUR | 11 571 EUR |
| Hruzova | 506 | 10 | 13.6M EUR | 150 EUR |
| Carmona | 49 | 1 | ~34 300 EUR | 700 EUR |

To naznacuje bud:
1. **Chybu v agregacnej logike** -- napr. pripisanie dat celej organizacie jednej osobe (dokazatelne v pripade Hengerics/Fond na podporu vzdelavania)
2. **Hallucination AI modelu** -- vygenerovanie presvedcivych ale nepravdivych cisel
3. **Pouzitie dat z ineho zdroja/obdobia** -- cisla mohli pochádzat z inej databazy

**Pred publikovanim akychkolvek nalezov je nevyhnutne overit ich priamo oproti zdrojovym datam v CRZ.**
