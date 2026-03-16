# FinStat enrichment: SFINGA s.r.o. (ICO 51671824)

Kontext: Zmluva o dielo za 1 291 200 EUR s neziskovou organizaciou PE-ES, n.o., zverejnena 489 dni po podpise. Overenie financnej sposobnosti dodavatela.

## Sumar
- Pocet dodavatelov: 1
- Financne zlte stopy: 1 DANGER, 1 WARNING
- Najkritickejsi dodavatel: SFINGA s.r.o. (zmluva presahuje 2,84-nasobok rocnych trzib)

---

## Dodavatel 1: SFINGA s.r.o. (ICO 51671824)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 454 385 EUR |
| Celkove vynosy | 454 464 EUR |
| Zisk (profit) | 5 079 EUR |
| Aktiva | 266 274 EUR |
| Vlastny kapital (equity) | 59 691 EUR |
| Celkova zadlzenost | 77,58 % |
| Hruba marza | 7,08 % |
| Datum vzniku | 25. maja 2018 (7 rokov) |
| Danova spolahlivost | spolahlivy |
| NACE kod | 41209 — Vystavba obytnych a neobytnych budov i.n. |
| Sidlo | Na Skotnu 32, Teplicka nad Vahom, 013 01 |
| Druh vlastnictva | Sukromne tuzemske |

### Registre dlznikov

| Register | Vysledok |
|---|---|
| Financna sprava (danovi dlznici) | Nenajdeny |
| VSZP (zdravotne poistenie) | Nenajdeny |
| Socialna poistovna | Nenajdeny |
| DPH deregistracia | Nie |
| Danova spolahlivost | Spolahlivy |

### Zmluvy v CRZ

| ID | Suma | Nazov zmluvy | Objednavatel | Podpis | Zverejnenie | Typ |
|---|---|---|---|---|---|---|
| 11946081 | 1 291 200 EUR | Zmluva o dielo c. 1/2024 | PE-ES, n.o. | 2024-10-04 | 2026-02-05 | zmluva |

Existujuce zlte stopy v CRZ databaze pre tento kontrakt:
- `missing_expiry` — zmluva nema datum platnosti
- `signatory_overlap` — Phdr. Lubica Geczyova podpisuje za 3 roznych dodavatelov

### Financne zlte stopy

| Zlta stopa | Severity | Detail |
|---|---|---|
| `contract_exceeds_2x_revenue` | DANGER | Zmluva 1 291 200 EUR presahuje 2x rocne trzby (454 385 EUR). Pomer zmluvy k trzby = 2,84x. Firma by musela vsetky svoje trzby za takmer 3 roky venovat len tomuto kontraktu. |
| `missing_rpvs` | WARNING | Zmluva presahuje 100 000 EUR s verejnym sektorom (PE-ES, n.o. je neziskova organizacia). Firma by mala byt registrovana v RPVS ako partner verejneho sektora — nutna kontrola v RPVS registri. |

Pravidla ktore neboli aktivovane:
- `negative_equity` — vlastny kapital je kladny (59 691 EUR)
- `severe_loss` — firma je v zisku (5 079 EUR), nie v strate
- `tax_unreliable` — firma je danovo spolahlivy subjekt
- `unusually_high_profit` — ziskova marza 1,1 % je nizka, nie neobvykle vysoka
- `young_company` — firma bola zalozena v 2018, kontrakt podpisany v 2024 (6 rokov po zalozeni)

### Hodnotenie

**Riziko: MEDIUM** — Zmluva za 1 291 200 EUR predstavuje 2,84-nasobok rocnych trzib firmy (454 385 EUR), co je v pasme MEDIUM (1-3x trzby pri kladnom vlastnom imani). Firma ma kladny vlastny kapital (59 691 EUR), co znamena ze nie je technicky insolventna, ale celkova zadlzenost 77,58 % je vysoka. Ziskova marza je len 7,08 % (hruba) a cisty zisk 5 079 EUR je minimalny — firma nema financnu rezervu na zvladnutie zakazky tejto velkosti z vlastnych zdrojov.

### Doplnkova analyza

**Kapacitna analyza:**
- Pri aktualnych trzbach 454 385 EUR/rok by firma potrebovala 2,84 roka cistych trzib na pokrytie zmluvy
- Cisty zisk 5 079 EUR neumoznuje vyrazne investicie do realizacie
- Celkova zadlzenost 77,58 % naznacuje ze firma uz vyuziva cudzie zdroje vo velkom rozsahu
- Vlastny kapital 59 691 EUR vs. hodnota zmluvy 1 291 200 EUR — pomer 1:21,6

**Casovy kontext:**
- Zmluva bola zverejnena az 489 dni po podpise (2024-10-04 → 2026-02-05), co je extremne nescore zverejnenie
- Zakon ukladal povinnost zverejnit do 30 dni; 489 dni je 16-nasobok zakonnej lehoty
- Zdielany podpisujuci (Phdr. Lubica Geczyova podpisuje za 3 roznych dodavatelov) zvysuje podozrenie na prepojene subjekty

**Odporucanie pre dalsie kroky:**
1. **RPVS kontrola** — overit ci je SFINGA s.r.o. registrovana v Registri partnerov verejneho sektora (povinnost pri zmluach nad 100 000 EUR)
2. **FOAF.sk** — zmapovat korporatnu siet a zistit prepojenia na dalsich dodavatelov (signatory overlap)
3. **UVO kontrola** — overit ci existuje verejne obstaravanie pre tuto zakazku
4. **PE-ES, n.o. preskumanie** — overit financie a pozadie objednavatela (neziskova organizacia objednava stavebne prace za 1,29M EUR)

---

**Enrichment ukonceny.** SFINGA s.r.o. je firma s trzby 454 385 EUR, ktora ziskala kontrakt za 1 291 200 EUR (2,84x trzby). Hoci nie je danovy dlznik a ma kladny vlastny kapital, kombinacia vysokej zadlzenosti (77,58 %), minimalneho zisku (5 079 EUR) a extremne neskoreho zverejnenia (489 dni) vyvolava opravnene otazky o jej schopnosti zakazku realizovat. Toto su stopy, nie verdikty — je potrebne dalsie preskumanie cez RPVS, FOAF a UVO.

*Zdroje: finstat.sk/51671824, crz.db (lokalna databaza), zmluvy.zltastopa.sk*
