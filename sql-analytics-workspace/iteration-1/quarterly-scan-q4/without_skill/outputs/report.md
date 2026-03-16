# Analyza zmluv Q4 2025 (oktober - december)

## Prehlad

| Metrika | Hodnota |
|---------|---------|
| Celkovy pocet zmluv | 1 773 |
| Celkova suma | 1 453 460 661,74 EUR |
| Priemerna suma | 1 083 863,28 EUR |
| Najvyssia suma | 1 032 689 734,00 EUR |
| Obdobie | 2025-10-01 az 2025-12-31 |

## Mesacny rozpad

| Mesiac | Pocet zmluv | Celkova suma (EUR) |
|--------|-------------|---------------------|
| Oktober 2025 | 162 | 16 921 496,64 |
| November 2025 | 675 | 26 389 122,25 |
| December 2025 | 936 | 1 410 150 042,85 |

**December dominuje** -- 97% celkovej hodnoty Q4 a 53% poctu zmluv. Toto je typicky "koncorocny rush" -- objem v decembri je 83x vysssi nez v oktobri a 53x vysssi nez v novembri.

### Koncorocny rush -- posledne dni decembra

| Den | Pocet | Suma (EUR) |
|-----|-------|------------|
| 22. dec | 36 | 6 047 612 |
| 23. dec | 31 | 35 225 265 |
| 24. dec (Stedry den!) | 4 | 21 524 |
| 29. dec | 40 | 14 784 860 |
| 30. dec | 52 | 4 441 204 |
| 31. dec (Silvester) | 25 | 130 313 |

Velky objem kontraktov (193 zmluv, 60,6 mil. EUR) bol zverejneny v poslednych 10 dnoch roka.

---

## Najvacsie zmluvy Q4 2025

### 1. TATRA DEFENCE SYSTEMS -- 1,033 mld. EUR
- **Zmluva:** Ramcova zmluva c. SEMOD-179/2025-7
- **Objednavatel:** Ministerstvo obrany SR
- **Zverejnenie:** 17.12.2025
- **Poznamka:** Jedna zmluva tvori **71% celej hodnoty Q4**. Ide o vojenskotechnicky kontrakt -- ICO 08993289 (firma zalozena 2019).

### 2. GRAND POWER -- 82,2 mil. EUR
- **Zmluva:** Ramcova dohoda
- **Objednavatel:** Ministerstvo obrany SR
- **Zverejnenie:** 17.12.2025
- **Poznamka:** Druha obrovska obrana zmluva v ten isty den. Grand Power je slovensky vyrobca zbrani.

### 3. DataCentrum -- 34,1 mil. EUR
- **Zmluva:** Kontrakt medzi MF SR a DataCentrom na rok 2026
- **Objednavatel:** Ministerstvo financii SR
- **Zverejnenie:** 23.12.2025

### 4-5. Environmentalny fond -- 2x velke dotacie
- 30 mil. EUR pre Vodohospodarsku vystavbu
- 22,1 mil. EUR pre MH Teplarensky holding
- Celkovo Environmentalny fond poskytol 15 zmluv za 95,7 mil. EUR

### 6. GMT development -- 13,6 mil. EUR
- **Zmluva:** Dodatok c. 4 k zmluve o dielo (naviac prace)
- **Objednavatel:** Gymnazium P.O. Hviezdoslava, Kezmarok
- **Poznamka:** Nezvycajne vysoka suma pre strednu skolu.

---

## Rezorty -- kto minul najviac

| Rezort | Pocet | Suma (EUR) |
|--------|-------|------------|
| Ministerstvo obrany SR | 20 | 1 115 480 785 |
| Subjekty verejnej spravy | 872 | 111 744 320 |
| Ministerstvo zivotneho prostredia SR | 24 | 97 245 740 |
| Ministerstvo financii SR | 7 | 34 750 025 |
| Urad podpredsedu vlady SR (Plan obnovy) | 5 | 24 326 250 |
| Ministerstvo podohospodarstva SR | 14 | 14 546 674 |

Ministerstvo obrany tvori 77% celkovej hodnoty Q4, ale iba s 20 zmluvami -- extrenmna koncentracia.

---

## Red flags -- automaticke varovania

Celkovo bolo identifikovanych **2 653 red flagov** na zmluvach z Q4 2025.

| Typ flagu | Pocet | Zavaznost |
|-----------|-------|-----------|
| missing_expiry | 1 322 | Nizka -- chyba datum platnosti |
| missing_ico | 505 | Stredna -- dodavatel bez ICO |
| hidden_price | 432 | Vysoka -- zmluvy s nulovou/chybajucou sumou |
| not_in_ruz | 220 | Stredna -- dodavatel nie je v registri |
| rapid_succession | 48 | Vysoka -- rychle uzatvaranie zmluv po sebe |
| tax_unreliable | 28 | Vysoka -- danovo nespolahlivy dodavatel |
| weekend_signing | 24 | Stredna -- podpis cez vikend |
| fs_tax_debtor | 16 | Vysoka -- danovy dlznik |
| fresh_company | 12 | Vysoka -- nova firma |
| socpoist_debtor | 9 | Vysoka -- dlznik Socialnej poistovne |
| supplier_monopoly | 7 | Stredna -- monopolny dodavatel |
| missing_attachment | 7 | Vysoka -- chyba priloha |
| micro_supplier_large_contract | 5 | Vysoka -- mala firma, velka zmluva |
| dormant_then_active | 5 | Vysoka -- "spiaca" firma |
| fs_vat_deregistered | 4 | Vysoka -- odregistrovany platca DPH |
| negative_equity | 3 | Vysoka -- negativne vlastne imanie |
| threshold_gaming | 2 | Vysoka -- hra s prahovou hodnotou |
| hidden_entities | 1 | Vysoka -- skryte entity |

### Klucove statistiky:
- **432 zmluv (24%)** ma skrytu/nulovu cenu -- neumoznuje kontrolu hospodarnosti
- **28 zmluv** s danovo nespolahlyvymi dodavatelmi, najvacsia: SWAN a.s. za 7,98 mil. EUR
- **12 zmluv** s cerstvymi firmami (zalozene nedavno)

---

## Najviac rizikovi dodavatelia (kumulacia flagov)

### Slavomir Adamjak (ICO 41350260) -- 6 typov flagov
- Nulova hodnota zmluv, ale 6 roznych typov varovani

### AGROMECHANIKA s.r.o. (ICO 47132809) -- 4 typy flagov, 260 755 EUR
- Styri rozne typy varovani na firmu s relativne malym objemom

### RVL s.r.o. (ICO 48224014) -- 4 typy flagov, 1,18 mil. EUR
- **Zmluva o dielo c. 4/11/2025** pre Mesto Cierna nad Tisou, 295 345 EUR
- Flagy: `fs_tax_debtor`, `micro_supplier_large_contract`, `missing_expiry`, `socpoist_debtor`
- Firma je danovy dlznik A dlznik Socialnej poistovne, pritom dostava verejne zakazky

---

## Podozrive vzory

### 1. Kloboucka lesni s.r.o. -- cerstva firma s 13,2 mil. EUR kontraktom
- **ICO:** 57109095 (organizacna zlozka ceskiej firmy)
- **Zmluva:** Ramcova dohoda na poskytovanie lesnickych sluzieb
- **Objednavatel:** Narodne lesnicke centrum
- **Problem:** `fresh_company` flag. Toto je jedina zmluva tejto firmy v celej databaze. Firma s ICO zacnajucim na 57 je relativne nova, a hned dostava 13+ milionovy kontrakt.

### 2. Reinter s.r.o. -- dormant firma, 5,19 mil. EUR kontrakt na Luniku IX
- **ICO:** 46005218
- **Zmluva:** Zmluva o dielo pre Mestsku cast Kosice - Lunik IX
- **Problem:** `dormant_then_active` flag. Firma mala obdobie neaktivity a nasledne ziskala velky kontrakt. Celkovo iba 10 zmluv v databaze.

### 3. Threshold gaming -- dve zmluvy tesne pod hranicou
- **DREVEX EU s.r.o.** (ICO 36835463) -- 212 783 EUR pre Obec Liptovske Sliace
- **USD Lucenec s.r.o.** (ICO 47575832) -- 212 180 EUR pre Mesto Kosice (fontana v parku)
- Obe sumy su podozrivo blizko prahovej hodnote pre verejne obstaravanie.

### 4. SWAN a.s. -- danovo nespolahlivy dodavatel s 8 mil. EUR kontraktom
- **ICO:** 35680202
- Zmluva o poskytnuti dotacie (7,98 mil. EUR) z Uradu podpredsedu vlady pre Plan obnovy
- Druha zmluva (58 449 EUR) pre Kancelariu Najvyssieho sudu
- Firma je flagovana ako `tax_unreliable`

### 5. Oneskorene zverejnenie
- **DOMOV SENIOROV Tatranska Strba** -- zmluva podpisana 23.7.2024, zverejnena az 12.12.2025 (507 dni!)
- **Univerzita Komenskeho / APVV** -- 368 dni oneskorenie
- Podla zakona by zmluva mala byt zverejnena do 90 dni

### 6. Fond na podporu vzdelavania -- 457 zmluv s jednou osobou
- Dodavatel: Fond na podporu vzdelavania (ICO 47245531)
- Objednavatel: Tomas Hengerics
- 457 zmluv v jednom kvartali za celkovo 4,2 mil. EUR
- Ide o pozicky studentom, ale enormny pocet s jednym menom je neobvykly

### 7. GMT development s.r.o. -- 13,6 mil. EUR dodatok pre gymnazium
- **ICO:** 47981563
- Dodatok c. 4 k zmluve o dielo -- "prace naviac" v hodnote 13,6 mil. EUR
- Objednavatel: Gymnazium P.O. Hviezdoslava, Kezmarok
- Nezvycajne vysoka suma pre stredoskolske zariadenie

---

## Typologia zmluv

| Typ | Pocet | Suma (EUR) |
|-----|-------|------------|
| Zmluva | 1 764 | 1 453 304 936 |
| Dodatok | 9 | 155 725 |

| Druh | Pocet | Suma (EUR) |
|------|-------|------------|
| Zmluva | 1 706 | 1 423 930 714 |
| Objednavka | 66 | 29 526 679 |

---

## Opakovane dvojice dodavatel-objednavatel

| Dodavatel | Objednavatel | Pocet | Suma (EUR) |
|-----------|-------------|-------|------------|
| Environmentalny fond | MH Teplarensky holding | 5 | 48 580 819 |
| abib s.r.o. | CVTI SR | 3 | 5 674 881 |
| Fond na podporu vzdelavania | Tomas Hengerics | 457 | 4 208 268 |
| PREMONA s.r.o. | Zeleznice SR | 3 | 2 473 182 |
| Univerzita Komenskeho | APVV | 4 | 928 942 |

---

## Zhrnutie a odporucania

### Hlavne zistenia:
1. **Extremna koncentracia v decembri** -- 97% hodnoty kvartalu, co naznacuje koncorocne "precpavanie" rozpoctu
2. **Obrana dominuje** -- dve ramcove zmluvy MO SR za 1,115 mld. EUR (77% celej hodnoty Q4)
3. **432 zmluv (24%) bez ceny** -- systematicky problem transparentnosti
4. **Cerstva firma Kloboucka lesni** ziskala 13,2 mil. EUR kontrakt ako svoju jedinu zmluvu v databaze
5. **Dormant firma Reinter** ziskala 5,19 mil. EUR na Luniku IX
6. **Danovo nespolahlivy SWAN** dostal 8 mil. EUR z Planu obnovy
7. **Oneskorene zverejnovanie** -- niektoré zmluvy su zverejnene az 500+ dni po podpise

### Odporucane dalsie kroky:
- Hlbkova analyza Kloboucka lesni s.r.o. (ICO 57109095) -- RPVS, vlastnicka struktura
- Preverenie Reinter s.r.o. (ICO 46005218) -- preco bola firma neaktivna a co sa zmenilo
- Kontrola GMT development (ICO 47981563) -- 13,6 mil. EUR za "prace naviac" pre gymnazium
- Overenie SWAN a.s. (ICO 35680202) -- danovy status vs. 8 mil. EUR dotacia
- Preverenie RVL s.r.o. (ICO 48224014) -- dlznik SP aj danovemu uradu, napriek tomu dodavatel

---

*Analyza vygenerovana 2026-03-16 z databazy CRZ (crz.db). Obdobie: Q4 2025 (1.10.2025 -- 31.12.2025).*
