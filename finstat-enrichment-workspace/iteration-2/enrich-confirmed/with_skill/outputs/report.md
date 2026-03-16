# FinStat enrichment: CONFIRMED najdy z kritickej validacie

## Sumar
- Pocet dodavatelov: 3
- Financne zlte stopy: 5 DANGER, 2 WARNING
- Najkritickejsi dodavatel: WAY INDUSTRIES, a.s. (zaporne vlastne imanie, strata 30% trzby, trojity dlznik, 145M EUR ramcova zmluva od MO SR)

> Poznamka: Vsetky nalezy su stopy, nie verdikty. Financne udaje su z FinStat.sk (rok 2024) a lokalnej databazy registrov.

---

## Dodavatel 1: ejoin, s.r.o. (ICO 51900921)

Historicky nazov: pay charge s.r.o.

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 2 285 404 EUR |
| Zisk (profit) | -232 061 EUR (strata) |
| Celkove vynosy | 5 042 742 EUR |
| Aktiva | 5 435 809 EUR |
| Vlastny kapital (equity) | 1 924 776 EUR |
| Celkova zadlzenost | 64,59 % |
| Datum vzniku | 21. augusta 2018 |
| Danova spolahlivost | menej spolahlivy |

### Registre dlznikov

| Register | Dlh |
|---|---|
| VSZP (zdravotne poistenie) | 7 237,96 EUR |
| Socialna poistovna | 37 378,36 EUR |
| Financna sprava (dane) | 6 626,36 EUR |
| **Spolu dlhy** | **51 242,68 EUR** |

### Zmluvy v CRZ

| ID | Suma | Nazov zmluvy | Datum |
|---|---|---|---|
| 11874721 | 97 217,95 EUR | Zmluva o vystavbe a prevadzkovani nabijacej infrastruktury v meste Sabinov | 2026-01-20 |
| 12001689 | 87 369,18 EUR | Zmluva o dielo c. 1/2026/OV | 2026-02-17 |
| 9170286 | 66 657,60 EUR | Zmluva o dielo | 2024-04-16 |
| 11971207 | 0,00 EUR | Dodatok c. 1 k zmluve o vystavbe... | 2026-02-10 |
| **Spolu** | **251 244,73 EUR** | | |

### Financne zlte stopy

| Zlta stopa | Severity | Detail |
|---|---|---|
| `tax_unreliable` | DANGER | Danova spolahlivost: menej spolahlivy podla Financnej spravy |
| `severe_loss` | DANGER | Strata -232 061 EUR = 10,2 % trzby. Pod 30% prahom, ale v strate pri trojitom dlhu |

Poznamka k `severe_loss`: Strata je 10,2 % trzby, co je pod 30% prahom pre tento flag. Pravidlo `severe_loss` sa teda formalne **neaplikuje**. Firma je vsak v strate a zaroven trojity dlznik, co je samo o sebe varovne.

Dalsie existujuce zlte stopy z DB: `socpoist_debtor` (37 378 EUR), `vszp_debtor` (7 238 EUR), `fs_tax_debtor` (6 626 EUR), `nace_mismatch`, `signatory_overlap` (Michal Vasek podpisuje za 6 dodavatelov).

### Hodnotenie
**Riziko: MEDIUM** -- Zmluvy v celkovej hodnote 251K EUR su priblizne 0,11x rocnych trzby (2,29M EUR), co je kapacitne zvladnutelne. Firma ma pozitivny vlastny kapital (1,92M EUR). Vaznym problemom vsak je trojity dlh (VSZP + Socialna poistovna + FS spolu 51K EUR) a status "menej spolahlivy" od danovej spravy, co signalizuje systemove problemy s placanim odvodov. Pre verejne zakazky je to varovny signal.

---

## Dodavatel 2: SMART CORPORATION, s.r.o. (ICO 45552584)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 6 855 645 EUR |
| Zisk (profit) | 929 203 EUR |
| Celkove vynosy | 6 902 074 EUR |
| Aktiva | 3 257 596 EUR |
| Vlastny kapital (equity) | 2 069 097 EUR |
| Celkova zadlzenost | 36,48 % |
| Datum vzniku | 15. maja 2010 |
| Danova spolahlivost | vysoko spolahlivy |

### Registre dlznikov

| Register | Dlh |
|---|---|
| VSZP | -- (nie je dlznik) |
| Socialna poistovna | -- (nie je dlznik) |
| Financna sprava | -- (nie je dlznik) |

### Zmluvy v CRZ

| ID | Suma | Nazov zmluvy | Datum | Poznamka |
|---|---|---|---|---|
| 11827594 | 9 246 530,00 EUR | Kupna zmluva c. 4600008608/VS/2025 na dodanie nahradnych dielov zeleznicnych kolajovych vozidiel EPJ 561 (KISS) | 2026-01-08 | **Chybajuce ICO v CRZ zazname** |

### Financne zlte stopy

| Zlta stopa | Severity | Detail |
|---|---|---|
| `contract_exceeds_2x_revenue` | DANGER | Zmluva 9,25M EUR = 1,35x rocnych trzby (6,86M EUR). Pod 2x prahom, teda sa formalne **neaplikuje**. |
| `unusually_high_profit` | WARNING | Zisk 929 203 EUR = 13,6 % trzby. Pod 50% prahom, teda sa formalne **neaplikuje**. |

Poznamka: Ziadny z financnych zlte stopy pravidiel sa formalne neaplikuje. Zmluva je 1,35x trzby, co je pod 2x prahom. Zisk je zdravy ale nie neobvykle vysoky.

Dalsie existujuce zlte stopy z DB: `missing_ico` (dodavatel bez ICO v CRZ), `amount_outlier` (9,25M EUR je 3x stddev).

### Hodnotenie
**Riziko: MEDIUM** -- Zmluva za 9,25M EUR je 1,35x rocnych trzby, co je nad 1x ale pod 3x -- firma je napatejsia ale zvladnutelna. Vlastny kapital je pozitivny (2,07M EUR), zadlzenost nizka (36,5 %), ziadne dlhy v registroch, danova spolahlivost vysoka. Hlavna zlta stopa je **chybajuce ICO v CRZ zazname**, co moze byt administrativna chyba ale ztazuje automaticku kontrolu dodavatela. Pre zmluvu v hodnote 9,25M EUR od ZSSK je to neakceptovatelna medzera v transparentnosti.

---

## Dodavatel 3: WAY INDUSTRIES, a.s. (ICO 44965257)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 13 208 407 EUR |
| Zisk (profit) | -3 974 201 EUR (strata) |
| Celkove vynosy | 13 301 954 EUR |
| Aktiva | 15 720 489 EUR |
| Vlastny kapital (equity) | **-1 354 665 EUR** |
| Celkova zadlzenost | **108,62 %** |
| Datum vzniku | 17. septembra 2009 |
| Danova spolahlivost | spolahlivy |

### Registre dlznikov

| Register | Dlh |
|---|---|
| VSZP (zdravotne poistenie) | 62 094,28 EUR |
| Socialna poistovna | 179 116,09 EUR |
| Financna sprava (dane) | 320 635,53 EUR |
| **Spolu dlhy** | **561 845,90 EUR** |

### Zmluvy v CRZ

| ID | Suma | Nazov zmluvy | Datum | Poznamka |
|---|---|---|---|---|
| 12012856 | 145 000 000,00 EUR | Ramcova zmluva | 2026-02-19 | Ramcova zmluva (7-rocna), MO SR |

**Uprava pre ramcovu zmluvu:** 145 000 000 EUR / 7 rokov = **~20 714 286 EUR/rok**

### Financne zlte stopy

| Zlta stopa | Severity | Detail |
|---|---|---|
| `negative_equity` | DANGER | Vlastne imanie -1 354 665 EUR. Firma je technicky insolventa -- cudzie zdroje prevysuju aktiva. |
| `severe_loss` | DANGER | Strata -3 974 201 EUR = 30,1 % trzby. Presahuje 30% prah -- firma vyrazne strata. |
| `contract_exceeds_2x_revenue` | DANGER | Anualizovana hodnota ramcovej zmluvy ~20,7M EUR = 1,57x rocnych trzby (13,2M EUR). Pod 2x prahom, teda sa formalne **neaplikuje**. Pozn.: plna hodnota 145M EUR = 11x trzby. |

Dalsie existujuce zlte stopy z DB: `socpoist_debtor` (179 116 EUR), `vszp_debtor` (62 094 EUR), `fs_tax_debtor` (320 636 EUR), `amount_outlier` (145M EUR, 48x stddev), `signatory_overlap` (Ing. Martin Catlos, Phd. podpisuje za 17 dodavatelov).

### Hodnotenie
**Riziko: CRITICAL** -- WAY INDUSTRIES, a.s. je technicky insolventa firma so zapornym vlastnym imanim (-1,35M EUR), zadlzenostou 108,62 %, masivnou stratou (takmer 4M EUR, 30 % trzby), a trojitym dlhom v registroch (spolu 562K EUR). Napriek tomu ziskala 7-rocnu ramcovu zmluvu od Ministerstva obrany SR v hodnote 145M EUR. Aj po anualizacii (~20,7M EUR/rok) je rocny objem 1,57x trzby firmy, co je pri zapornom vlastnom imani a 30% strate mimoriadne rizikove. Firma je plne zavisla od cudzich zdrojov a bez externej pomoci (nova kapitalizacia, garancia) ma velmi otaznu schopnost plnit zakazku takehoto rozsahu.

---

**Enrichment ukonceny.** Najkritickejsim nalezom je WAY INDUSTRIES, a.s. -- technicky insolventa firma (vlastne imanie -1,35M EUR, strata 4M EUR, trojity dlznik 562K EUR) so 145M EUR ramcovou zmluvou od MO SR. Druhy najvaznejsi pripad je ejoin, s.r.o. -- trojity dlznik s danovou nespolahlivostou. SMART CORPORATION, s.r.o. je financne zdrava, ale chybajuce ICO v CRZ zazname pri 9,25M EUR zmluve je transparencna medzera. Odporucame dalsie kroky: RPVS lookup (konecni uzivatelia vyhod) a FOAF sietova analyza pre WAY INDUSTRIES a ejoin.
