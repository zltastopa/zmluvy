# Prehlad zmluv za februar 2026 — CRZ analyticky report

**Datum analyzy:** 2026-03-16
**Obdobie:** 1. februar 2026 -- 28. februar 2026
**Zdroj:** Centralny register zmluv (Datasette: zmluvy.zltastopa.sk)

---

## 1. Celkovy prehlad

| Ukazovatel | Hodnota |
|---|---|
| Celkovy pocet zmluv | **57 318** |
| Z toho nových zmluv | 52 477 |
| Z toho dodatkov | 4 841 |
| Celkova hodnota (suma_celkom) | **3,584 mld. EUR** |
| Celkovy pocet red flags | **149 816** |

---

## 2. Najvacsie zmluvy mesiaca

| # | Suma (EUR) | Dodavatel | Objednavatel | Nazov |
|---|---|---|---|---|
| 1 | 490 058 824 | Statny fond rozvoja byvania | Min. dopravy SR | Dodatok c.2 k Zmluve o financovani c. 850/CC00/2024 |
| 2 | **145 000 000** | **WAY INDUSTRIES, a.s.** | **Min. obrany SR** | **Ramcova zmluva** |
| 3 | 117 296 495 | STU Bratislava | Min. skolstva | Dotacia na rok 2026 |
| 4 | 93 992 763 | TU Kosice | Min. skolstva | Dotacia na rok 2026 |
| 5 | 65 960 618 | Min. skolstva | UPJS Kosice | Dotacia na rok 2026 |
| 6 | 60 408 004 | Min. spravodlivosti | Mestsky sud BA III | Dodatok c.3 - Plan obnovy |
| 7 | 60 408 004 | Min. spravodlivosti | Mestsky sud BA IV | Dodatok c.3 - Plan obnovy (duplicitny zaznam) |
| 8 | 60 000 000 | Min. cestovneho ruchu a sportu | Fond na podporu sportu | Prispevok na rok 2026 |
| 9 | **32 569 732** | **PERSET a.s.** | **Hlavne mesto SR Bratislava** | **Zmluva o ZP k Zmluve o spolupraci** |
| 10 | **32 569 732** | **Asset Real a.s.** | **Hlavne mesto SR Bratislava** | **Zmluva o ZP k Zmluve o spolupraci** |

---

## 3. Najzaujimavejsie nalezy

### 3.1 WAY INDUSTRIES — 145 mil. EUR ramcova zmluva s Min. obrany (fs_tax_debtor)

- **Zmluva:** [crz.gov.sk/zmluva/12012856](https://www.crz.gov.sk/zmluva/12012856/)
- **Suma:** 145 000 000 EUR
- **Dodavatel:** WAY INDUSTRIES, a.s. (ICO: 44965257)
- **Objednavatel:** Ministerstvo obrany SR
- **Podpis:** 2026-02-13, **zverejnenie:** 2026-02-19
- **Red flag:** `fs_tax_debtor` — dodavatel je dlznikom na daniach podla FinStat
- **Preco je to zaujimave:** Najvacsia neopakovana zmluva mesiaca. Ramcova zmluva za 145 mil. EUR s firmou, ktora figuruje ako danovy dlznik. WAY INDUSTRIES je zbrojarska firma (vyroba vojenskej techniky), ale danovy dlh pri zakazke takehoto rozsahu vyvolava otazky o financnej stabilite dodavatela. Toto je jedina zmluva tejto firmy v celej databaze CRZ.

### 3.2 PERSET a.s. + Asset Real a.s. — po 32.5 mil. EUR pre Bratislavu

- **Zmluvy:** [12047388](https://www.crz.gov.sk/zmluva/12047388/) a [12047390](https://www.crz.gov.sk/zmluva/12047390/)
- **Suma:** 2x 32 569 732 EUR = **65.1 mil. EUR spolu**
- **Objednavatel:** Hlavne mesto SR Bratislava
- **Zverejnene:** 2026-02-27, obe v rovnakom case (16:50)
- **Preco je to zaujimave:** Dve rovnako velke zmluvy zverejnene v rovnakom momente, obe naviazane na tu istu "Zmluvu o spolupraci c. OKVZoSFP0001". Nazov aj cislo zmluvy naznacuju suvislost medzi PERSET a Asset Real. Toto je jediny zaznam oboch firiem v databaze — nemaju ziadnu predchadzajucu historiu. Pri celkovej sume 65 mil. EUR pre Bratislavu si to zasluzuje hlbsie preskumanie.

### 3.3 Dodavatelia s financnymi rizikovymi flagmi — TOP 10

| Dodavatel | ICO | Flags | Pocet zmluv | Celkova suma (EUR) |
|---|---|---|---|---|
| WAY INDUSTRIES, a.s. | 44965257 | fs_tax_debtor | 1 | 145 000 000 |
| Sprava rezortnych zariadeni MK SR | 56767242 | fresh_company | 2 | 14 266 053 |
| SWAN, a.s. | 35680202 | tax_unreliable | 21 | 12 423 767 |
| VODOHOSPODARSKE STAVBY a.s. | 31322301 | tax_unreliable | 3 | 6 284 117 |
| EKO SVIP, s.r.o. | 36449717 | tax_unreliable | 6 | 5 524 293 |
| SIPSTAV s.r.o., r.s.p. | 50226851 | fs_tax_debtor | 1 | 3 099 894 |
| CSS LUC | 17066735 | negative_equity | 1 | 3 029 416 |
| XENEX, s.r.o. | 36416291 | fs_tax_debtor | 1 | 2 677 461 |
| LYNX s.r.o. | 00692069 | tax_unreliable | 2 | 2 113 255 |
| EURO-HOME s.r.o. | 46713212 | fs_tax_debtor | 2 | 1 952 282 |

### 3.4 BRIGHT STAR INVEST SK — danovy dlznik aj danovo nespolahliva firma

- **Zmluva:** [11992470](https://www.crz.gov.sk/zmluva/11992470/)
- **Suma:** 679 858.69 EUR
- **Dodavatel:** BRIGHT STAR INVEST SK s.r.o. (ICO: 51912597)
- **Objednavatel:** Obec Zakamenne
- **Flags:** `fs_tax_debtor` + `tax_unreliable` — kombinacia dvoch financnych flagov
- **Predmet:** Rekonstrukcia a zastresenie multifunkcneho ihriska
- **Preco je to zaujimave:** Firma ma sucasne dlh na daniach (FinStat) aj status danovo nespolahliveho platcu. Pri stavebnej zakazke za takmer 680 tis. EUR pre malu obec je toto vyrazne varovne znamenie.

### 3.5 EKO SVIP, s.r.o. — tax_unreliable s viacerymi zakazkami pre obce

- **ICO:** 36449717
- **Flag:** tax_unreliable
- **Pocet zmluv vo feb 2026:** 6 (celkovo 5.5 mil. EUR)
- **Objednavatelia:** Male obce (Chotca, Kurov, Havaj, Hankovce) + VVS a.s. + Urad prace Presov
- **Preco je to zaujimave:** Danovo nespolahliva firma ziskava opakovane stavebne zakazky od malych obci v Presovskom kraji. Vzorec opakovanych zakazok pre male obce moze naznacovat problematicke verejne obstaravanie.

### 3.6 SFINGA s.r.o. — zmluva zverejnena 489 dni po podpise

- **Zmluva:** [11946081](https://www.crz.gov.sk/zmluva/11946081/)
- **Suma:** 1 291 200 EUR
- **Dodavatel:** SFINGA s.r.o. (ICO: 51671824)
- **Objednavatel:** PE-ES, n.o.
- **Podpis:** 2024-10-04, **zverejnenie:** 2026-02-05
- **Oneskorenie:** **489 dni**
- **Preco je to zaujimave:** Zakon vyzaduje zverejnenie do 10 pracovnych dni. Tato zmluva o dielo za 1.29 mil. EUR bola zverejnena az po takmer 1.5 roku. Jedina zmluva tejto firmy v CRZ.

### 3.7 Extremne oneskorene zverejnenia (TOP 5)

| Oneskorenie (dni) | Suma (EUR) | Dodavatel | Objednavatel |
|---|---|---|---|
| 1 349 | 159 833 | Min. zivotneho prostredia | Zoo Bojnice |
| 617 | 80 000 | SAAIC (Erasmus+) | SPS Poprad |
| 489 | 1 291 200 | SFINGA s.r.o. | PE-ES, n.o. |
| 402 | 194 400 | TU Kosice | Mesto Presov |
| 370 | 539 476 | MIRRI SR | Obec Vidina |

### 3.8 Sprava rezortnych zariadeni MK SR — cerstve ICO, velka zmluva

- **Zmluva:** [11966830](https://www.crz.gov.sk/zmluva/11966830/)
- **Suma:** 14 266 053 EUR
- **Dodavatel:** Sprava rezortnych zariadeni MK SR (ICO: 56767242)
- **Objednavatel:** Ministerstvo kultury SR
- **Flag:** `fresh_company` — novo zalozeny subjekt
- **Podpis:** piatok 31.1.2026 (predvikendy), zverejnenie: nedela 9.2.2026
- **Preco je to zaujimave:** Kontrakt za 14.2 mil. EUR s novo zriadenym subjektom ministerstva. Podpis v posledny den mesiaca, vikendy na oboch stranach. Hoci ide o rezortnu organizaciu (nie sukromnu firmu), velkost kontraktu pre novo zriadeny subjekt si zasluzuje pozornost.

---

## 4. Strukturalne pozorovania

### 4.1 Rozdelenie red flagov (februar 2026)

| Typ flagu | Pocet |
|---|---|
| missing_expiry (chybajuci datum platnosti) | 40 159 |
| hidden_price (skryta cena) | 26 161 |
| signatory_overlap (prekryvanie signatárov) | 21 514 |
| not_in_ruz (nie je v RUZ) | 13 463 |
| missing_ico (chybajuce ICO) | 13 382 |
| hidden_entities (skryte entity) | 6 367 |
| missing_attachment (chybajuca priloha) | 4 789 |
| nace_mismatch (nesulad odvetvia) | 4 064 |
| rapid_succession (rychle za sebou) | 3 443 |
| bezodplatne (bezodplatna zmluva) | 3 025 |
| supplier_advantage (zvyhodnenie dodavatela) | 2 995 |
| weekend_signing (vikendovy podpis) | 1 335 |
| supplier_monopoly (monopol dodavatela) | 1 041 |
| tax_unreliable (danovo nespolahliva) | 824 |
| fs_tax_debtor (danovy dlznik) | 769 |
| negative_equity (negativne vlastne imanie) | 736 |
| fresh_company (cerstvy subjekt) | 547 |
| excessive_penalties (nadmerne pokuty) | 370 |
| contract_splitting (delenie zakaziek) | 334 |

### 4.2 Najvacsi objednavatelia

| Objednavatel | Pocet zmluv | Celkova suma (EUR) |
|---|---|---|
| Ministerstvo dopravy SR | 38 | 552 648 382 |
| Ministerstvo prace, soc. veci a rodiny SR | 780 | 321 387 190 |
| Ministerstvo skolstva SR | 224 | 257 308 321 |
| Ministerstvo obrany SR | 507 | 183 852 477 |
| Statny fond rozvoja byvania | 247 | 122 150 836 |
| Mestsky sud Bratislava IV | 5 | 121 325 960 |
| Hlavne mesto SR Bratislava | 222 | 91 386 602 |

### 4.3 INMEDIA — nespolahliva firma s desiatkami zmluv

- **ICO:** 36019208 | **Flag:** tax_unreliable
- **Pocet zmluv vo feb 2026:** 80 (pod roznymi variantmi nazvu firmy — INMEDIA, spol. s r.o. / spol. s.r.o. / s. r. o. atd.)
- **Celkova suma:** ~1.27 mil. EUR
- **Objednavatelia:** rozlicne statne institucie vr. Min. obrany SR
- **Preco je to zaujimave:** Danovo nespolahliva firma so znacnym poctom zmluv, pricom nazov firmy je zaznamenany v desiatke roznych pravopisnych variant, co stazuje automaticku kontrolu.

---

## 5. Zhrnutie a odporucania na hlbsiu analyzu

### Priorita 1 — Vysoke riziko
1. **WAY INDUSTRIES (145 mil. EUR)** — danovy dlznik so zbrojarsou zakazkou pre Min. obrany. Odporucam overit aktualny danovy dlh a financnu situaciu firmy.
2. **PERSET + Asset Real (65 mil. EUR)** — dve identicky ocenene zmluvy zverejnene sucasne pre Bratislavu, ziadna predchadzajuca historia. Overit vlastnicke struktury oboch firiem (RPVS, foaf.sk).
3. **SFINGA s.r.o. (1.29 mil. EUR)** — zmluva zverejnena 489 dni po podpise. Preco?

### Priorita 2 — Stredne riziko
4. **EKO SVIP, s.r.o.** — danovo nespolahliva stavebna firma s opakovanymi zakazkami od malych obci v Presovskom kraji.
5. **BRIGHT STAR INVEST SK** — dvojity financny flag (tax_unreliable + fs_tax_debtor), stavebna zakazka pre malu obec.
6. **Sprava rezortnych zariadeni MK SR** — fresh_company s kontraktom za 14.2 mil. EUR.

### Priorita 3 — Systemove problemy
7. **INMEDIA** — 80 zmluv pod desiatkou pravopisnych variant, tax_unreliable flag.
8. **Extremne oneskorenia zverejnenia** — viacero zmluv za stovky tisic EUR zverejnenych s oneskorenim 300+ dni.
9. **13 382 zmluv bez ICO dodavatela** — systematicky problem identifikacie dodavatelov.

---

*Report vygenerovany automatickou analyzou dat z CRZ. Vsetky nalezy vyzaduju dalsi manualny overovaci krok pred vyvodenim zaverov.*
