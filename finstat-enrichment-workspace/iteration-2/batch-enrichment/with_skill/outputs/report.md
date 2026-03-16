# FinStat enrichment: Top dodavatelia Q1 2026 (januar - marec)

## Sumar
- Pocet dodavatelov analyzovanych: 200
- Uspesne scrapovanych z FinStat: 197 (148 novych + 49 cachovanych)
- Financne zlte stopy: 278 DANGER, 144 WARNING
- Najkritickejsi dodavatel: PERSET a.s. (ICO 48239089) -- zmluva 110.4x trzby, bez vlastneho imania v DB
- Vynechane statne institucie: Fond na podporu vzdelavania (ICO 47245531), Sprava rezortnych zariadeni MK SR (ICO 56767242)

**Poznamka:** Toto su stopy, nie verdikty. Kazdy nalez vyzaduje dalsie overenie.

**Metodicka poznamka -- ramcove zmluvy:** Pri ramcovych zmluvach a viacrocnych kontraktoch je celkova suma anualizovana pred porovnanim s trzby. Napr. ramcova zmluva na 145 000 000 EUR s predpokladanym trvanim 7 rokov = ~20,7 mil. EUR/rok.

---

## Dodavatel 1: PERSET a.s. (ICO 48239089)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 294 963 EUR |
| Zisk (profit) | nezisteny |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 12,31 % |
| Datum vzniku | 25. jula 2015 |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 12047388 | 32 569 732 EUR | Zmluva o ZP k Zmluve o spolupraci c. OKVZoSFP0001 s.r.o. - PERSET a.s. |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 32 569 732 EUR > 2x trzby 294 963 EUR (110,4x) |

### Hodnotenie
**Riziko: CRITICAL** -- Firma s trzby necelych 295 000 EUR ziskala zakazku za 32,6 mil. EUR, co predstavuje 110-nasobok jej rocnych trzby. Zadlzenost je nizka (12 %), ale absolutna kapacita firmy je nesmierne nedostatocna na realizaciu takejto zakazky. Vysoko podozrive.

---

## Dodavatel 2: Reality development a.s. (ICO 36781959)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 44 200 EUR |
| Zisk (profit) | nezisteny |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 87,29 % |
| Datum vzniku | 25. maja 2007 |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 12069749 | 5 596 582 EUR | Zmluva o zriadeni zalozneho prava k nehnutelnostiam c. OKVZoSFZ0029 |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 5 596 582 EUR > 2x trzby 44 200 EUR (126,6x) |

### Hodnotenie
**Riziko: CRITICAL** -- Firma s minimalnym obratom 44 200 EUR a vysokou zadlzenostou (87 %) figuruje v zmluve za 5,6 mil. EUR (126,6-nasobok trzby). Ide o zmluvu o zriadeni zalozneho prava, co naznacuje, ze firma moze byt len vlastnikom nehnutelnosti. Aj tak je disproporcia medzi financnym profilom a hodnotou zmluvy extremna.

---

## Dodavatel 3: Biomedical Engineering, s.r.o. (ICO 45329818)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 357 811 EUR |
| Zisk (profit) | 215 057 EUR |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 62,49 % |
| Datum vzniku | 13. januara 2010 |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 12051747 | 9 991 432 EUR | Zmluva o poskytnuti nenavratneho financneho prispevku c. 37/2026 |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 9 991 432 EUR > 2x trzby 357 811 EUR (27,9x) |
| unusually_high_profit | WARNING | Zisk 215 057 EUR > 50 % trzby 357 811 EUR (60 %) |

### Hodnotenie
**Riziko: CRITICAL** -- NFP zmluva za takmer 10 mil. EUR pri trzby len 358 000 EUR (27,9-nasobok). Neobvykle vysoka ziskovost (60 % trzby) naznacuje moznu shell company alebo firmu zijucu prevazne z grantov. Objednavatel: Ministerstvo zdravotnictva SR.

---

## Dodavatel 4: WAY INDUSTRIES, a.s. (ICO 44965257)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 13 208 407 EUR |
| Zisk (profit) | nezisteny |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 108,62 % |
| Datum vzniku | 17. septembra 2009 |
| Danova spolahlivost | spolahlivy |
| VSZP dlznik | 62 094 EUR |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 12012856 | 145 000 000 EUR | Ramcova zmluva |

### Uprava pre ramcovu zmluvu
Ramcova zmluva bez uvedenej platnosti. Predpokladane trvanie obrannych ramcovych zmluv je typicky 4-7 rokov. Pri 7 rokoch: 145 000 000 / 7 = **20 714 286 EUR/rok** (1,57x trzby). Pri 4 rokoch: 145 000 000 / 4 = **36 250 000 EUR/rok** (2,74x trzby).

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Celkova suma 145 000 000 EUR > 2x trzby 13 208 407 EUR (11,0x); anualizovane pri 7r: 1,57x |

### Hodnotenie
**Riziko: MEDIUM** (po anualizacii pri 7r) / **HIGH** (pri 4r alebo kratsom trvani) -- Po anualizacii 7-rocnej ramcovej zmluvy klesa pomer na 1,57x trzby, co je v rozmedzi MEDIUM. Avsak: zadlzenost presahuje 100 % (technicky insolvencia), firma je dlznikom VSZP (62 094 EUR), a vlastny kapital nie je dostupny. Objednavatel: Ministerstvo obrany SR. Bez znalosti skutocneho trvania zmluvy je riziko neiste.

---

## Dodavatel 5: INVEST 9 - Westend Gate a.s. (ICO 36288411)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 3 596 779 EUR |
| Zisk (profit) | nezisteny |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 80,55 % |
| Datum vzniku | 25. marca 2006 |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11847539 | 42 277 656 EUR | Zmluva o najme nebytovych priestorov a parkovacich miest |

### Uprava pre dlhodobu zmluvu
Ide o najomnu zmluvu (priestory a parkovacie miesta) -- typicky viacrocna. Bez uvedenej platnosti. Pri 10 rokoch: 42 277 656 / 10 = **4 227 766 EUR/rok** (1,18x trzby). Pri 5 rokoch: **8 455 531 EUR/rok** (2,35x trzby).

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 42 277 656 EUR > 2x trzby 3 596 779 EUR (11,8x); anualizovane pri 10r: 1,18x |

### Hodnotenie
**Riziko: LOW** (pri 10r) / **MEDIUM** (pri 5r) -- INVEST 9 je realitna spolocnost (Westend Gate), zmluva o najme je ich core business. Anualizovane na 10 rokov klesa pomer na 1,18x, co je v norme. Vysoka zadlzenost (80 %) je typicka pre realitne spolocnosti. Objednavatel: VsZP a.s.

---

## Dodavatel 6: EURO-STUKONZ a.s. (ICO 35972297)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 3 814 505 EUR |
| Zisk (profit) | 150 069 EUR |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 85,47 % |
| Datum vzniku | 31. decembra 2005 |
| Danova spolahlivost | menej spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11862436 | 9 313 931 EUR | Dodatok c. 3 k Zmluve o dielo |
| 12029110 | 1 653 256 EUR | Zmluva o dielo c. 0464/TTSK/2025 |
| 12092718 | 562 988 EUR | Zmluva o dielo c. 206/2026 |

**Celkova suma Q1 2026: 11 530 176 EUR (3,02x trzby)**

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Dodatok 9 313 931 EUR > 2x trzby 3 814 505 EUR (2,4x) |
| tax_unreliable | DANGER | Index danovej spolahlivosti: menej spolahlivy |

### Hodnotenie
**Riziko: HIGH** -- Kombinacia dvoch DANGER signalom: danovo nespolahlivy dodavatel s celkovym objemom zmluv 3x prevysujucim trzby. Vysoka zadlzenost (85 %). Stavebna firma (zmluvy o dielo) s kapacitnym problemom. Objednavatelia: UK Bratislava, TTSK.

---

## Dodavatel 7: DICIT spol. s r.o. (ICO 43953794)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 3 297 844 EUR |
| Zisk (profit) | 127 861 EUR |
| Vlastny kapital (equity) | 1 237 031 EUR (z RUZ) |
| Celkova zadlzenost | 55,69 % |
| Datum vzniku | 25. januara 2008 |
| Danova spolahlivost | vysoko spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11930567 | 12 104 418 EUR | Zmluva o poskytovani sluzieb |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 12 104 418 EUR > 2x trzby 3 297 844 EUR (3,7x) |

### Hodnotenie
**Riziko: HIGH** -- Zmluva presahuje trzby 3,7-nasobne, co je nad hranicou HIGH. Pozitivne: kladny vlastny kapital (1,24 mil. EUR), vysoko spolahlivy danovy status, prijemna ziskovost. Avsak kapacita na 12 mil. EUR zakazku je otazna.

---

## Dodavatel 8: CSM Industry s.r.o. (ICO 50720350)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 6 894 389 EUR |
| Zisk (profit) | 6 640 EUR |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 87,23 % |
| Datum vzniku | 9. februara 2017 |
| Danova spolahlivost | vysoko spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11831514 | 15 218 685 EUR | Nakup 15 kusov pracovneho stroja - specialny dokoncovacistroj |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 15 218 685 EUR > 2x trzby 6 894 389 EUR (2,2x) |

### Hodnotenie
**Riziko: MEDIUM** -- Pomer 2,2x je tesne nad hranicou, pri dodavke strojov moze byt firma len obchodnym sprostredkovatelom (nemusebytvyrobca). Takmer nulovy zisk (6 640 EUR pri trzby 6,9 mil.) naznacuje nizkomarginovy obchod. Vysoka zadlzenost (87 %). Objednavatel: MZP SR.

---

## Dodavatel 9: NEOXX a.s. (ICO 00603783)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 5 236 183 EUR |
| Zisk (profit) | 43 290 EUR |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 59,44 % |
| Datum vzniku | 17. januara 1991 |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11861184 | 14 402 963 EUR | Zmluva na poskytovanie sluzieb SAP maintenance a podpory uzivatelov SAP S4/HANA |
| 11860276 | 8 904 756 EUR | Zmluva o dielo |

**Celkova suma Q1 2026: 23 307 719 EUR (4,45x trzby)**

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 14 402 963 EUR > 2x trzby 5 236 183 EUR (2,8x) |

### Hodnotenie
**Riziko: HIGH** -- Celkovy objem 23,3 mil. EUR je 4,45-nasobok rocnych trzby. SAP maintenance zmluvy su casto viacrocne -- ak je zmluva na 4 roky, anualizovana suma klesa na ~5,8 mil. EUR/rok (1,1x trzby = LOW). Bez informacie o trvani zmluvy je riziko formalne HIGH, ale IT sluzby casto funguju s viacrocnym plnenim. Objednavatel: SEPS a.s.

---

## Dodavatel 10: Dopravny podnik mesta Ziliny s.r.o. (ICO 36007099)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 3 881 908 EUR |
| Zisk (profit) | nezisteny |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 92,86 % |
| Datum vzniku | 1. augusta 1996 |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 12082932 | 13 755 840 EUR | Zmluva o poskytnuti NFP c. Z401203G500 - Nakup ekologickych vozidiel MHD |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 13 755 840 EUR > 2x trzby 3 881 908 EUR (3,5x) |

### Hodnotenie
**Riziko: MEDIUM** -- Ide o NFP (nenavratny financny prispevok) na nakup ekologickych vozidiel MHD. DPmZ je mestsky podnik, nie sukromny dodavatel v klasickom zmysle. NFP zmluvy maju specificky charakter -- prijemca nemusel mat trzby zodpovedajuce hodnote prispevku. Formalne HIGH podla pomeru, ale v kontexte NFP pre mestsky dopravny podnik je riziko znizene.

---

## Dodavatel 11: zares, spol. s r.o. (ICO 35778806)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 5 153 511 EUR |
| Zisk (profit) | 89 178 EUR |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 12,49 % |
| Datum vzniku | 20. decembra 1999 |
| Danova spolahlivost | vysoko spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 12069757 | 35 000 000 EUR | Ramcova zmluva |

### Uprava pre ramcovu zmluvu
Platnost do 2030-03-05 (4 roky od podpisu). Anualizovane: 35 000 000 / 4 = **8 750 000 EUR/rok** (1,70x trzby).

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Celkova suma 35 000 000 EUR > 2x trzby; anualizovane na 4 roky: 8 750 000 EUR/rok (1,70x) |

### Hodnotenie
**Riziko: MEDIUM** (po anualizacii) -- Anualizovana suma 8,75 mil. EUR/rok je 1,70x trzby, co je v rozmedzi MEDIUM (1-3x). Pozitivne: velmi nizka zadlzenost (12 %), vysoko spolahlivy danovy status, firma existuje od 1999. Objednavatel: Subjekty verejnej spravy.

---

## Dodavatel 12: STS KOVO, s.r.o. (ICO 31656935)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 2 638 535 EUR |
| Zisk (profit) | 51 523 EUR |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 48,10 % |
| Datum vzniku | 12. augusta 1992 |
| Danova spolahlivost | vysoko spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 12037469 | 8 642 826 EUR | Zmluva o dielo c. 2026/104 |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 8 642 826 EUR > 2x trzby 2 638 535 EUR (3,3x) |

### Hodnotenie
**Riziko: HIGH** -- Zmluva presahuje trzby 3,3-nasobne. Objednavatel: Ministerstvo obrany SR. Prijemna zadlzenost a vysoko spolahlivy status, ale kapacita na realizaciu takejto zakazky je otazna pri danych trzbach.

---

## Dodavatel 13: SWAN, a.s. (ICO 35680202)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 156 261 127 EUR |
| Zisk (profit) | nezisteny |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 62,67 % |
| Datum vzniku | 18. decembra 1995 |
| Danova spolahlivost | menej spolahlivy |

### Zmluvy v CRZ (Q1 2026)
Celkova suma Q1 2026: 12 668 453 EUR cez 13 zmluv

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| tax_unreliable | DANGER | Index danovej spolahlivosti: menej spolahlivy |

### Hodnotenie
**Riziko: MEDIUM** -- Trzby su dostatocne (156 mil. EUR), kontrakt je len zlomok obratu. Problem je v danovej nespolahlivosti -- u velkeho telekomunikacneho operatora je to prekvapive a zasluzuje si pozornost.

---

## Dodavatel 14: INMEDIA, spol. s r.o. (ICO 36019208)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 38 186 117 EUR |
| Zisk (profit) | 1 624 730 EUR |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 46,09 % |
| Datum vzniku | 25. marca 1997 |
| Danova spolahlivost | menej spolahlivy |

### Zmluvy v CRZ (Q1 2026)
Celkova suma Q1 2026: 5 779 311 EUR cez 159 zmluv

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| tax_unreliable | DANGER | Index danovej spolahlivosti: menej spolahlivy |

### Hodnotenie
**Riziko: MEDIUM** -- Kontrakt/trzby pomer je nizky (0,15x = LOW). Problem je danova nespolahlivost. INMEDIA je velka medialna spolocnost s 159 zmluvami v Q1 -- vysoka koncentracia statnych zakazok u danovo nespolahlivej firmy je stopa hodna sledovania.

---

## Dodavatel 15: Bytovy podnik Dubravka, spol. s r.o. (ICO 35828994)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 847 966 EUR |
| Zisk (profit) | nezisteny |
| Vlastny kapital (equity) | nezisteny |
| Celkova zadlzenost | 104,28 % |
| Datum vzniku | 10. januara 2002 |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (Q1 2026)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11879501 | 2 150 000 EUR | Zmluva o uvere |
| 11922308 | 2 150 000 EUR | Zmluva o zriadeni zalozneho prava na pohladavky FPUO |
| 11889649 | 1 650 000 EUR | Zmluva o uvere |
| 11889722 | 1 041 400 EUR | Zmluva o uvere |

**Celkova suma Q1 2026: 8 417 720 EUR (9,93x trzby)**

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Viacere uverove zmluvy > 2x trzby |

### Hodnotenie
**Riziko: HIGH** -- Zadlzenost nad 100 % (technicky insolvencia), viacere uverove zmluvy za celkovo takmer 8,5 mil. EUR pri trzbach len 848 000 EUR. Kontextove zmienenie: bytove podniky casto financuju rekonstrukcie cez uvery s kolateralom vo forme fondov udrzby, takze uverova struktura je ciastocne ocakavatelna, ale rozsah je extremny.

---

## Suhrn najrizikovejsich dodavatelov

| # | Dodavatel | ICO | Riziko | Hlavne stopy |
|---|---|---|---|---|
| 1 | PERSET a.s. | 48239089 | **CRITICAL** | Zmluva 110x trzby, nezname financie |
| 2 | Reality development a.s. | 36781959 | **CRITICAL** | Zmluva 127x trzby, minimalne trzby 44k EUR |
| 3 | Biomedical Engineering, s.r.o. | 45329818 | **CRITICAL** | NFP 28x trzby, neobvykle vysoky zisk (60 %) |
| 4 | EURO-STUKONZ a.s. | 35972297 | **HIGH** | Danovo nespolahlivy + zmluvy 3x trzby |
| 5 | DICIT spol. s r.o. | 43953794 | **HIGH** | Zmluva 3,7x trzby |
| 6 | STS KOVO, s.r.o. | 31656935 | **HIGH** | Zmluva 3,3x trzby (obranne zakazky) |
| 7 | NEOXX a.s. | 00603783 | **HIGH** | Celkovo 4,5x trzby (SAP zmluvy, mozno viacrocne) |
| 8 | Bytovy podnik Dubravka | 35828994 | **HIGH** | Zadlzenost 104 %, uverove zmluvy 10x trzby |
| 9 | WAY INDUSTRIES, a.s. | 44965257 | **MEDIUM-HIGH** | Ramcova 145M, zadlzenost 108 %, dlznik VSZP |
| 10 | CSM Industry s.r.o. | 50720350 | **MEDIUM** | Zmluva 2,2x trzby, nulovy zisk |
| 11 | SWAN, a.s. | 35680202 | **MEDIUM** | Danovo nespolahlivy telekom operator |
| 12 | INMEDIA, spol. s r.o. | 36019208 | **MEDIUM** | Danovo nespolahlivy, 159 zmluv v Q1 |
| 13 | zares, spol. s r.o. | 35778806 | **MEDIUM** | Ramcova 35M/4r = 8,75M/rok (1,7x) |
| 14 | INVEST 9 - Westend Gate a.s. | 36288411 | **LOW-MEDIUM** | Najom 42M, ale core business realitnej firmy |
| 15 | Dopravny podnik Ziliny | 36007099 | **LOW-MEDIUM** | NFP 13,7M, mestsky podnik |

---

## Statisticky prehlad pipeline

| Metrika | Hodnota |
|---|---|
| Obdobie | Q1 2026 (januar - marec) |
| Celkovy pocet dodavatelov | 200 |
| Uspesne scrapovanych | 197 |
| Zlte stopy: DANGER | 278 |
| Zlte stopy: WARNING | 144 |
| Z toho contract_exceeds_2x_revenue | 42 |
| Z toho tax_unreliable | 236 |
| Z toho unusually_high_profit | 140 |
| Z toho young_company | 4 |

## Odporucania pre dalsi vyskum

1. **PERSET a.s.** (ICO 48239089) -- preverit cez RPVS a foaf.sk, kto su skutoeni vlastnici a ci existuje prepojenie s objednavatelom
2. **Reality development a.s.** (ICO 36781959) -- preverit ucely zalozneho prava a ci firma nieje len schranka
3. **Biomedical Engineering, s.r.o.** (ICO 45329818) -- preverit historiu grantov a ci firma realizuje projekty priamo alebo subdodavkami
4. **WAY INDUSTRIES, a.s.** (ICO 44965257) -- preverit skutocnu dlzku ramcovej zmluvy a suvis s VSZP dlhom
5. **EURO-STUKONZ a.s.** (ICO 35972297) -- preverit dovody danovej nespolahlivosti a stavebnu kapacitu

---

**Enrichment ukonceny.** Najzavaznejsie nalezy su tri dodavatelia s CRITICAL rizikom -- PERSET a.s. (zmluva 110x trzby), Reality development a.s. (zmluva 127x trzby) a Biomedical Engineering (NFP 28x trzby). Dalej su styroch dodavatelia s HIGH rizikom kombinujuci kapacitne problemy s danovou nespolahlivostou ci extremnou zadlzenostou. Po aplikovani anualizacie na ramcove zmluvy (WAY INDUSTRIES, zares, ESMO) sa ich riziko znizilo z HIGH na MEDIUM. Vsetky nalezy su stopy, nie verdikty, a vyzaduju dalsie overenie (RPVS, foaf.sk, UVO).
