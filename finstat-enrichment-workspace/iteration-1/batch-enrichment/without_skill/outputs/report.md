# Financne obohatenie dodavatelov Q1 2026 (januar -- marec)

Datum spracovania: 2026-03-16
Obdobie: 2026-01-01 az 2026-03-31
Metoda: Enrichment pipeline (`pipeline/enrich_suppliers.py`) + manualna kontrola registrov

> **Upozornenie:** Toto su stopy, nie verdikty. Kazdy nalez vyzaduje dalsie overenie.

---

## 1. Zhrnutie

Pipeline obohatil **30 najvacsich dodavatelov** podla celkovej hodnoty zmluv v Q1 2026.
Z nich bolo identifikovanych **5 dodavatelov s financnymi zlymi stopami** (typ: `contract_exceeds_2x_revenue` -- hodnota zmluvy presahuje 2-nasobok rocnych trzieb).

Vacsina z top 30 dodavatelov su statne institucie (ministerstva, univerzity, statne fondy), ktore nemaju profily na FinStat.sk -- to je ocakavane a nepredstavuje riziko.

---

## 2. Najrizikovejsi dodavatelia

### 2.1 PERSET a.s. (ICO: 48239089) -- NAJVYSSIE RIZIKO

| Ukazovatel | Hodnota |
|---|---|
| Trzby | 294 963 EUR |
| Strata | -34 915 EUR |
| Aktiva | 7 974 052 EUR |
| Zadlzenost | 12,31 % |
| Pocet zamestnancov | 3--4 |
| NACE | 68200 (Prenajom vlastnych nehnutelnosti) |
| Datum vzniku | 25.07.2015 |
| Danova spolahlivost | spolahlivy |
| VSZP dlznik | NIE |

**Zmluva v Q1 2026:**

| ID zmluvy | Nazov | Suma | Datum | Zlte stopy |
|---|---|---|---|---|
| 12047388 | Zmluva o ZP k Zmluve o spolupraci | 32 569 732,00 EUR | 2026-02-27 | Neobvykle vysoka suma; Bezodplatna zmluva; Skryte entity; Neuvedena platnost; Zdielany podpisujuci |

**Rizikove faktory:**
- Hodnota zmluvy je **110,4x vyssia** nez rocne trzby firmy (32,6 mil. EUR vs. 295 tis. EUR)
- Mikro firma (3-4 zamestnanci) s obrovskou zmluvou
- Firma ma stratu (-34 915 EUR)
- Zmluva obsahuje skryte entity a je oznacena ako bezodplatna
- 5 zltych stop na jednej zmluve

---

### 2.2 WAY INDUSTRIES, a.s. (ICO: 44965257) -- VYSOKE RIZIKO

| Ukazovatel | Hodnota |
|---|---|
| Trzby | 13 208 407 EUR |
| Strata | -3 974 201 EUR |
| Aktiva | 15 720 489 EUR |
| Zadlzenost | 108,62 % (prekrocena -- dlhy prevysuju aktiva) |
| Pocet zamestnancov | 150--199 |
| NACE | 28920 (Stroje pre tazobny priemysel a stavebnictvo) |
| Datum vzniku | 17.09.2009 |
| Danova spolahlivost | spolahlivy |
| VSZP dlznik | **ANO** |

**Zmluva v Q1 2026:**

| ID zmluvy | Nazov | Suma | Datum | Zlte stopy |
|---|---|---|---|---|
| 12012856 | Ramcova zmluva | 145 000 000,00 EUR | 2026-02-19 | Neobvykle vysoka suma; Danovy dlznik FS; Neuvedena platnost; Zdielany podpisujuci; Dlznik Socialnej poistovne; Dlznik VSZP |

**Rizikove faktory:**
- Hodnota zmluvy je **11x vyssia** nez rocne trzby (145 mil. EUR vs. 13,2 mil. EUR)
- Firma je v **strate** (-3,97 mil. EUR)
- **Predlzena** -- celkova zadlzenost 108,62 % (dlhy prevysuju majetok)
- **Dlznik** VSZP (zdravotna poistovna)
- **Danovy dlznik** Financnej spravy
- **Dlznik** Socialnej poistovne
- 6 zltych stop na jednej zmluve -- najvyssie pocet v datasete

---

### 2.3 INVEST 9 - Westend Gate a. s. (ICO: 36288411) -- VYSOKE RIZIKO

| Ukazovatel | Hodnota |
|---|---|
| Trzby | 3 596 779 EUR |
| Strata | -1 600 886 EUR |
| Aktiva | 50 272 343 EUR |
| Zadlzenost | 80,55 % |
| Pocet zamestnancov | 0 |
| NACE | 68200 (Prenajom vlastnych nehnutelnosti) |
| Datum vzniku | 25.03.2006 |
| Danova spolahlivost | spolahlivy |
| Historicky nazov | Botus, a.s. |

**Zmluva v Q1 2026:**

| ID zmluvy | Nazov | Suma | Datum | Zlte stopy |
|---|---|---|---|---|
| 11847539 | Zmluva o najme nebytovych priestorov a parkovacich miest | 42 277 656,00 EUR | 2026-01-13 | Neobvykle vysoka suma; Mikro dodavatel, velka zmluva; Neuvedena platnost; Zdielany podpisujuci |

**Rizikove faktory:**
- Hodnota zmluvy je **11,8x vyssia** nez rocne trzby (42,3 mil. EUR vs. 3,6 mil. EUR)
- Firma ma **0 zamestnancov** a je oznacena ako mikro dodavatel
- Firma je v **strate** (-1,6 mil. EUR)
- Vysoka zadlzenost (80,55 %)
- 4 zlte stopy

*Poznamka:* Firma vlastni nehnutelnost (Westend Gate), preto vysoka suma najmu moze byt odovodnitelna -- ale pomer zmluvy k trzby je stale neobvykly.

---

### 2.4 zares, spol. s r.o. (ICO: 35778806) -- STREDNE RIZIKO

| Ukazovatel | Hodnota |
|---|---|
| Trzby | 5 153 511 EUR |
| Zisk | 89 178 EUR |
| Aktiva | 3 994 653 EUR |
| Zadlzenost | 12,49 % |
| Pocet zamestnancov | 25--49 |
| NACE | 01610 (Pomocne cinnosti pre rastlinnu vyrobu) |
| Datum vzniku | 20.12.1999 |
| Danova spolahlivost | vysoko spolahlivy |

**Zmluva v Q1 2026:**

| ID zmluvy | Nazov | Suma | Datum | Zlte stopy |
|---|---|---|---|---|
| 12069757 | Ramcova zmluva | 34 999 999,99 EUR | 2026-03-05 | (ziadne automaticke stopy) |

**Rizikove faktory:**
- Hodnota zmluvy je **6,8x vyssia** nez rocne trzby (35 mil. EUR vs. 5,2 mil. EUR)
- Firma posobi v polnohospodarstve, ale zmluva je ramcova -- moze byt viaccrocna
- Danovo vysoko spolahlivy, ziskovost stabilna -- znizuje celkove riziko

---

### 2.5 ARRIVA Nove Zamky, a.s. (ICO: 36545317) -- NIZSIE RIZIKO

| Ukazovatel | Hodnota |
|---|---|
| Trzby | 7 319 872 EUR |
| Zisk | 885 206 EUR |
| Aktiva | 50 429 426 EUR |
| Zadlzenost | 70,20 % |
| Vlastne imanie | 11 034 390 EUR |
| Pocet zamestnancov | 250--499 |
| NACE | 49310 (Mestska a primestska osobna doprava) |
| Datum vzniku | 01.01.2002 |
| Danova spolahlivost | vysoko spolahlivy |

**Hlavna zmluva v Q1 2026:**

| ID zmluvy | Nazov | Suma | Datum | Zlte stopy |
|---|---|---|---|---|
| 11899030 | Dodatok c. 27 k Zmluve o sluzbach vo verejnom zaujme | 32 921 350,00 EUR | 2026-01-26 | Neuvedena platnost |

**Rizikove faktory:**
- Hodnota zmluvy je **4,5x vyssia** nez rocne trzby
- Avsak: firma ma znacny majetok (50,4 mil. EUR aktiva), ziskova, vysoko spolahlivy danovo
- Jedna sa o dlhodobeho poskytovatela verejnej dopravy -- zmluvy vo verejnom zaujme su typicky viaccrocne
- 18 zltych stop celkovo v Q1, ale vacsina su nizkeho vyznamu (neuvedena platnost, zdielany podpisujuci)

---

## 3. Dalsich 5 velkych sukromnych dodavatelov (bez financnych zltych stop)

| ICO | Nazov | Celk. suma Q1 | Trzby | Zadlz. | Tax status |
|---|---|---|---|---|---|
| 35919001 | Narodna dialnicna spolocnost, a.s. | 262 938 641 EUR | 440 421 000 EUR | 67,6 % | spolahlivy |
| 31333320 | Doprastav, a.s. | 66 433 411 EUR | 217 400 000 EUR | 66,8 % | spolahlivy |
| 31320155 | Vseobecna uverova banka, a.s. | 100 624 248 EUR | 1 232 235 000 EUR | 91,1 % | vysoko spolahlivy |
| 00151653 | Slovenska sporitelna, a.s. | 42 470 788 EUR | 1 221 853 000 EUR | 90,6 % | vysoko spolahlivy |
| 17314569 | Valbek SK, spol. s r.o. | 49 330 123 EUR | 15 972 644 EUR | 40,3 % | vysoko spolahlivy |

*Poznamka k Valbek SK:* Celkova suma Q1 zmluv (49,3 mil. EUR) je 3x vyssia nez trzby (16 mil. EUR), ale nezapadla do pipeline stopy, pretoze stopa sa pocita per zmluva, nie per supplier. Jednotlive zmluvy su 27,3 mil. a 21,1 mil. EUR -- obe by mali byt skontrolovane.

---

## 4. Sumar zltych stop z enrichment pipeline

| Typ stopy | Zavaznost | Pocet |
|---|---|---|
| contract_exceeds_2x_revenue | danger | 5 |

Pipeline identifikoval 5 zmluvno-financnych neskladov typu "zmluva prevysuje 2x trzby". Dalsie typy stop (negative_equity, tax_unreliable, young_company) neboli v tomto obdobi detekovane.

---

## 5. Odporucania na dalsie preverenie

1. **WAY INDUSTRIES, a.s. (ICO: 44965257)** -- Preverit RPVS (beneficiarnych vlastnikov), detaily ramcovej zmluvy za 145 mil. EUR, dovod dlhu v VSZP a Socialnej poistovni
2. **PERSET a.s. (ICO: 48239089)** -- Preverit skryte entity v zmluve, dovod bezodplatnosti, preco mikro firma so 4 zamestnancami dostala zmluvu za 32,6 mil. EUR
3. **INVEST 9 - Westend Gate a. s. (ICO: 36288411)** -- Preverit ci 42,3 mil. EUR zodpoveda trhovemu najmu, skontrolovat vlastnicku strukturu (historicky nazov Botus, a.s.)
4. **Valbek SK (ICO: 17314569)** -- Zmluvy v rychlom slede, skryte entity -- preverit rozsah subdodavok
5. **zares, spol. s r.o. (ICO: 35778806)** -- Overit ci ramcova zmluva za 35 mil. EUR je viaccrocna a akeho typu

---

## 6. Metodologia

- **Zdroj dat:** Lokalna databaza `crz.db` (CRZ register zmluv) + cache z FinStat.sk
- **Pipeline:** `pipeline/enrich_suppliers.py --from 2026-01 --to 2026-03 --limit 30`
- **Doplnkove registre:** tax_reliability, ruz_entities, ruz_equity, vszp_debtors, fs_vat_deregistered
- **FinStat scraping:** Data boli uz v cache z predchadzajuceho behu; overene cez curl na finstat.sk
- **Pravidla financnych stop:**
  - `contract_exceeds_2x_revenue`: suma zmluvy > 2x rocne trzby dodavatela (danger)
  - `negative_equity`: zaporne vlastne imanie (danger)
  - `severe_loss`: strata > 30% trzieb (danger)
  - `unusually_high_profit`: zisk > 50% trzieb (warning)
  - `missing_rpvs`: zmluva > 100K EUR a dodavatel nie je v RPVS (warning)
  - `tax_unreliable`: index danovej spolahlivosti = menej spolahlivy (danger)
  - `young_company`: firma mladsie nez 1 rok v case podpisu zmluvy (warning)
