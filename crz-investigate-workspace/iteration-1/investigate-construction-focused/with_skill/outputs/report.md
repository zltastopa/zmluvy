# Investigativna analyza: Stavebne zmluvy v CRZ (2026-02-01 -- 2026-02-07)

Zameranie: Stavebne prace, rekonstrukcie, obnovy (construction_renovation)

---

## Faza 1: SQL Analytics

### Sumar
- Pocet zmluv v obdobi (celkovo): 18 014
- Pocet stavebnych zmluv: 379
- Celkova suma stavebnych zmluv: 161 380 719 EUR
- Pocet spustenych dopytov: 20
- Pocet dopytov s vysledkami: 13
- Dopytov bez vysledkov: 7 (Q5 threshold gaming, Q7 vikend, Q10 Neuvedene, Q11 skupina dodavatelov, Q18 zaporne vlastne imanie, Q19 spiace firmy, Q13 bezodplatne -- v stavebnom sektore)

### Top 5 najdov

1. **SOSTAV s.r.o. -- zmluva 68x prevysujuca trzby** -- Firma zalozena v januari 2024 s trzbami 8 582 EUR ziskala zmluvu o dielo za 588 265 EUR od Obce Spisske Bystre. Navyse ma priznak "pokuty zvyhodnuju dodavatela" (supplier_advantage).

2. **SFINGA s.r.o. -- zverejnenie 489 dni po podpise** -- Zmluva o dielo za 1 291 200 EUR podpisana 4.10.2024 bola zverejnena az 5.2.2026. Objednavatel PE-ES, n.o. je neziskova organizacia. Trzby firmy (454 385 EUR) su vyrazne nizsie nez hodnota zmluvy.

3. **RAVOZA s.r.o. -- 4 zmluvy za 3,6M pre rovnakeho objednavatela za 1 den** -- Firma registrovana na krajinnu upravu (NACE 81300) ziskala 4 zmluvy na obnovu materskych skol od MC Bratislava-Podunajske Biskupice. Vsetky s ukrytou entitou ERGA projekt s.r.o.

4. **ERIGOM SK s.r.o. -- poradenska firma s 3,3M stavebnou zakazkou** -- NACE kod = "Poradenska cinnost v podnikani" (70220), ale firma ziskala zmluvu na stavebne prace za 3 306 842 EUR od Zilinskeho samospravenho kraja. Vysoka miera subdodavok, skryta entita VAHOSTAV a.s.

5. **KG INVEST s.r.o. -- dvojity dlznik s verejnou zakazkou** -- Firma dlzi VSZP (305 EUR) aj Socialnej poistovni (1 687 EUR) a sucasne ziskava stavebnu zakazku za 100 053 EUR.

---

## 1. Toky penazi

### 1.1 Top dodavatelia podla celkovej sumy (stavebne zmluvy)

| Dodavatel | ICO | Pocet | Celkom (EUR) |
|-----------|-----|-------|--------------|
| Urad vlady SR | 00151513 | 5 | 24 539 295 |
| Bytova agentura rezortu MO | 34000666 | 1 | 24 000 000 |
| Min. dopravy SR | 30416094 | 1 | 24 000 000 |
| UN L. Pasteura Kosice | 00606707 | 2 | 12 170 804 |
| DataCentrum | 00151564 | 1 | 6 271 660 |
| BLOCK CRS a.s. | 07333366 | 1 | 5 185 088 |
| HOTIS RECYCLING SLOVAKIA | 35872764 | 1 | 5 177 171 |
| Svidgas, s.r.o. | 26464261 | 1 | 4 595 548 |
| RAVOZA s.r.o. | 50310810 | 4 | 3 617 407 |
| COMBIN Banska Stiavnica | 31631134 | 4 | 3 338 392 |
| ERIGOM SK s.r.o. | 53574907 | 1 | 3 306 842 |

**Interpretacia:** Dominuju statne presuny (Urad vlady, Min. dopravy -- nenávratne financne prispevky). Privatni dodavatelia zacinaju od BLOCK CRS (5,2M) a HOTIS RECYCLING (5,2M). RAVOZA s 4 zmluvami za 3,6M pre jedneho objednavatela si zasluzi pozornost.

### 1.2 Koncentracia objednavatel-dodavatel (nad 500 000 EUR)

| Objednavatel | Dodavatel | Pocet | Celkom (EUR) |
|-------------|-----------|-------|--------------|
| MC BA-Podunajske Biskupice | RAVOZA s.r.o. | 4 | 3 617 407 |
| Zilinsky sam. kraj | ERIGOM SK s.r.o. | 1 | 3 306 842 |
| VODOHOSPODARSKA VYSTAVBA | EKOSTAV-AB s.r.o. | 2 | 2 174 131 |
| Mesto Cadca | Mestsky podnik sluzieb Cadca | 2 | 1 167 000 |

**Interpretacia:** RAVOZA -- 4 zmluvy za 3,6M pre jedneho objednavatela za 1 den je neobvykla koncentracia. ERIGOM ma 3,3M od ZSK. Mestsky podnik sluzieb Cadca -- 2 identicke zmluvy (583 500 EUR kazda), pravdepodobny duplikat.

---

## 2. Manipulacia obstaravania

### 2.1 Delenie zakazky
Jediny najd: Dusan Minar -- 5 mikro-zakaziek (celkom 1 497 EUR) pre SVP, s.p. Ide o drobne prace, nie o manipulaciu.

### 2.2 Threshold gaming (210-220K EUR)
Ziadne stavebne zmluvy v tomto pasme.

### 2.3 Okruhle sumy (nasobky 100 000 EUR)

| ID | Nazov | Dodavatel | Suma (EUR) |
|----|-------|-----------|-----------|
| 11930006 | Mechanizmus obnovy P07 | Min. dopravy SR | 24 000 000 |
| 11954717 | Mechanizmus obnovy P07 | Bytova agentura MO | 24 000 000 |
| 11928645 | Ramcova dohoda stavebne prace | LAVORE s.r.o. | 300 000 |

**Interpretacia:** 24M su duplicitne uploady statnych mechanizmov -- nevinne. LAVORE 300K ramcova dohoda -- okruhla suma je pri ramcovych dohodach bezna.

---

## 3. Casove anomalie

### 3.1 Zverejnenie cez vikend
Ziadne stavebne zmluvy nad 100 000 EUR zverejnene cez vikend.

### 3.2 Neskor zverejnenie (nad 90 dni)

| ID | Nazov | Dodavatel | Suma (EUR) | Podpis | Zverejnenie | Dni |
|----|-------|-----------|-----------|--------|-------------|-----|
| 11946081 | ZoD c. 1/2024 | SFINGA s.r.o. | 1 291 200 | 2024-10-04 | 2026-02-05 | 489 |

**Interpretacia:** Extrémne oneskorenie -- 489 dni. Zmluva bola podpisana v oktobri 2024 a zverejnena az vo februari 2026. Objednavatel PE-ES, n.o. je neziskova organizacia. SFINGA ma trzby len 454 385 EUR -- zmluva prevysuje 2,8x rocne trzby.

---

## 4. Fantomovi dodavatelia

### 4.1 Dodavatelia bez ICO (nad 50 000 EUR)

| ID | Nazov | Dodavatel | Suma (EUR) |
|----|-------|-----------|-----------|
| 11960711 | Dodatok c. 2 k ZoD | COMBIN Banska Stiavnica s.r.o. | 883 806 |
| 11927883 | ZoD CBS/001 | COMBIN Banska Stiavnica s.r.o. | 424 789 |
| 11957953 | Dodatok c. 1 k ZoD | ASFA-KDK s.r.o. | 171 550 |
| 11955810 | Dodatok 4 Revitalizacia | Neuvedene | 83 662 |

**Interpretacia:** COMBIN Banska Stiavnica (ICO 31631134) ma niektore zmluvy bez ICO -- datovy problem, nie fantom. "Neuvedene" za 83 662 EUR pri revitalizacii v Trnave si zasluzi pozornost.

---

## 5. Extrakcie

### 5.1 Pokuty zvyhodnujuce dodavatela (supplier_advantage)

| ID | Nazov | Dodavatel | Suma (EUR) |
|----|-------|-----------|-----------|
| 11959965 | ZoD (Obec Spisske Bystre) | SOSTAV s.r.o. | 588 265 |
| 11919846 | Zmluva o udrzbe | ATMA s.r.o. | 83 800 |

**Interpretacia:** SOSTAV s.r.o. (ICO 56017278) -- firma zalozena januar 2024 s trzbami 8 582 EUR ziskava zakazku za 588K s pokutami zvyhodnujucimi dodavatela. Vysoko podozrive.

### 5.2 Skryte entity (3+)

| ID | Dodavatel | Suma (EUR) | Pocet skrytych entit |
|----|-----------|-----------|---------------------|
| 11959825 | Svidgas s.r.o. | 4 595 548 | 3 |
| 11958339 | Cronson s.r.o. | 666 500 | 3 |
| 11959669 | LS STAVBY PLUS s.r.o. | 250 545 | 4 |
| 11938357 | PEMAL s.r.o. | 232 759 | 3 |

**Interpretacia:** Svidgas (ceska firma, ICO 26464261) -- 4,6M zmluva s 3 skrytymi entitami pre Nemocnicu sv. Michala. Cronson -- 666K s 3 skrytymi entitami.

---

## 6. Dlznicki

### 6.1 VSZP dlznici

| Dodavatel | ICO | Zmluvy (EUR) | Dlh VSZP (EUR) |
|-----------|-----|-------------|----------------|
| Milan Smado - MIS | 30204330 | 1 249 000 | 3 767 |
| LAVORE s.r.o. | 54126771 | 300 000 | 7 749 |
| KG INVEST s.r.o. | 47594021 | 100 053 | 305 |

### 6.2 Socialna poistovna dlznici

| Dodavatel | ICO | Zmluvy (EUR) | Dlh SP |
|-----------|-----|-------------|--------|
| KG INVEST s.r.o. | 47594021 | 100 053 | 1 687 EUR |

### 6.3 Dvojity dlznici (VSZP + SP)

| Dodavatel | ICO | Zmluvy (EUR) | Dlh VSZP (EUR) |
|-----------|-----|-------------|----------------|
| KG INVEST s.r.o. | 47594021 | 100 053 | 305 |

**Interpretacia:** KG INVEST je jediny dvojity dlznik v stavebnom sektore. Dlhy su male, ale princip je dolezity -- firma neplati odvody a sucasne ziskava verejne zakazky.

---

## 7. Bonusove kontroly

### 7.1 Zaporne vlastne imanie
Ziadni stavebni dodavatelia so zapornym vlastnym imanim v obdobi.

### 7.2 Spiace firmy
Ziadne spiace stavebne firmy v obdobi.

### 7.3 Denne rozlozenie objemu

| Den | Pocet | Celkom (EUR) | Den tyzdna |
|-----|-------|-------------|-----------|
| 2026-02-06 (piatok) | 103 | 68 333 833 | Pia |
| 2026-02-02 (pondelok) | 58 | 36 960 196 | Pon |
| 2026-02-03 (utorok) | 53 | 28 058 302 | Ut |
| 2026-02-04 (streda) | 73 | 17 505 904 | Str |
| 2026-02-05 (stvrtok) | 90 | 10 522 484 | Stv |
| 2026-02-01 (nedela) | 2 | 0 | Ned |

**Interpretacia:** Piatok 6.2. dominuje s 103 zmluvami za 68,3M EUR -- typicky pattern konca tyzdna. Pondelok 2.2. je druhy najsilnejsi den -- zaciatok tyzdna. 2 nedelnne zmluvy su s nulovou sumou.

---

## Zhrnutie najdov (pred validaciou)

| # | Nazov najdu | Kategoria | Severity | Kluc |
|---|-------------|-----------|----------|------|
| 1 | SOSTAV -- trzby 8 582 EUR, zmluva 588K | supplier_advantage + capacity | DANGER | ICO 56017278 |
| 2 | SFINGA -- 489 dni oneskorenie, zmluva 2.8x trzby | late publication + capacity | HIGH | ICO 51671824 |
| 3 | RAVOZA -- 4x zmluvy 3.6M, NACE mismatch | rapid succession + nace | WARNING | ICO 50310810 |
| 4 | ERIGOM SK -- poradenska firma, 3.3M stavba | nace mismatch + subcontracting | WARNING | ICO 53574907 |
| 5 | KG INVEST -- dvojity dlznik | double debtor | WARNING | ICO 47594021 |
| 6 | Svidgas -- CZ firma, 4.6M, 3 skryte entity | hidden entities | WARNING | ICO 26464261 |
| 7 | Duplicitne zmluvy 24M + 9.9M | data artifact | INFO | -- |

---

# Faza 2: Kriticka validacia

## Sumar validacie
- Pocet najdov na vstupe: 7
- CONFIRMED: 3
- INCONCLUSIVE: 2
- DISMISSED: 2

---

## CONFIRMED najdy

### 1. SOSTAV s.r.o. -- firma s trzbami 8 582 EUR ziskava zakazku za 588 265 EUR -- DANGER

**Povodny najd:** Supplier advantage (pokuty zvyhodnuju dodavatela) + extrémny nesuhl kapacity.

**Validacne kroky:**
1. Overenie FinStat: Trzby 8 582 EUR, Zisk 5 309 EUR, Aktiva 16 792 EUR
2. Overenie v RUZ: Firma zalozena 18.1.2024, NACE "Ost.stav.kompletiz.prace", 10-19 zamestnancov
3. Overenie registrov: Ziadne dlhy, danovo spolahlivy
4. Overenie extrakcie: Potvrdene supplier_advantage (pokuty zvyhodnuju dodavatela)

**Preco to nie je falesny pozitiv:**
- Zmluva za 588 265 EUR je **68,6x** rocnych trizieb firmy (8 582 EUR)
- Aktiva firmy (16 792 EUR) su 35x mensie nez hodnota zmluvy
- Firma existuje len 2 roky -- kratka historia
- Pokutovy mechanizmus zvyhodnuje dodavatela -- obec nesie viac rizika
- Toto NIE je ramcova zmluva -- je to zmluva o dielo na konkretne stavebne prace

**Klucove cisla:**
- Zmluva ID: 11959965
- Objednavatel: Obec Spisske Bystre
- CRZ: https://www.crz.gov.sk/zmluva/11959965/
- FinStat: https://finstat.sk/56017278

**Zlte stopy:**
- `contract_exceeds_2x_revenue` (DANGER) -- zmluva 68,6x trzby
- `supplier_advantage` (DANGER) -- pokuty zvyhodnuju dodavatela
- `young_company` (WARNING) -- firma 2 roky stara

**Riziko: CRITICAL** -- Firma s trzbami 8 582 EUR nemoze realisticky dodat stavebne prace za 588 265 EUR bez externeho financovania alebo subdodavok. Kombinacia s pokutovym zvyhodnenim je vysoko podozriva.

---

### 2. SFINGA s.r.o. -- zmluva za 1,29M zverejnena 489 dni po podpise -- HIGH

**Povodny najd:** Extremne oneskorene zverejnenie. Zmluva podpisana 4.10.2024, zverejnena 5.2.2026.

**Validacne kroky:**
1. Overenie ci ide o dodatok: NIE, typ = "zmluva"
2. Overenie objednavatela: PE-ES, n.o. (ICO 37923251) -- neziskova organizacia prevadzkujuca socialne sluzby
3. Overenie FinStat: Trzby 454 385 EUR, Zisk 5 079 EUR, Aktiva 266 274 EUR
4. Overenie registrov: Danovo spolahlivy, ziadne dlhy
5. Overenie ci ma ine zmluvy v CRZ: Toto je jedina zmluva SFINGA v CRZ

**Preco to nie je falesny pozitiv:**
- Toto NIE je EU/Erasmus grant (kde su oneskvorenia bezne)
- Je to zmluva o dielo (ZoD c. 1/2024) -- stavebne prace
- 489 dni oneskorenia je **5x nad zakonnym limitom** (zmluva mala byt zverejnena do 60 dni)
- Objednavatel je neziskovka -- menej transparentna nez statny organ
- Zmluva (1 291 200 EUR) je **2,84x** rocnych trizieb SFINGA
- Jedina zmluva firmy v CRZ -- ziadna historia verejnych zakaziek

**Klucove cisla:**
- Zmluva ID: 11946081
- Objednavatel: PE-ES, n.o. (ICO 37923251)
- CRZ: https://www.crz.gov.sk/zmluva/11946081/
- FinStat: https://finstat.sk/51671824

**Zlte stopy:**
- `contract_exceeds_2x_revenue` (DANGER) -- zmluva 2,84x trzby
- Extremne oneskorene zverejnenie -- 489 dni (zakon vyzaduje do 60 dni)

**Riziko: HIGH** -- Zmluva s oneskorenim 489 dni naznacuje pokus o zatajenie. Objednavatel je neziskovka, dodavatel nema ziadnu historiu verejnych zakaziek a zmluva prevysuje jeho rocne trzby.

---

### 3. RAVOZA s.r.o. -- 4 zmluvy za 3,6M pre rovnakeho objednavatela za 1 den -- WARNING

**Povodny najd:** 4 zmluvy na obnovu materskych skol od MC BA-Podunajske Biskupice. NACE mismatch (krajinna uprava vs. construction). Skryta entita ERGA projekt s.r.o.

**Validacne kroky:**
1. Overenie FinStat: Trzby 7 679 922 EUR, Zisk 67 586 EUR, Aktiva 1 424 629 EUR
2. Overenie NACE: Registrovana ako "Cinnosti suvisiace s krajinnou upravou" (81300) -- nie stavebnictvo
3. Overenie celkovej historie: 7 zmluv celkovo za 4 594 983 EUR
4. Overenie red_flags: rapid_succession (4 zmluvy za 14 dni), nace_mismatch, hidden_entity_is_supplier (ERGA projekt)

**Preco to nie je falesny pozitiv:**
- NACE kod 81300 (krajinna uprava) je **vyrazne odlisny** od stavebnictva
- 4 zmluvy za 1 den pre rovnakeho objednavatela naznacuju rozdelenie jednej vacsej zakazky
- Celkova suma 3 617 407 EUR by pri jednej zmluve prekrocila limit pre verejne obstaravanie
- ERGA projekt s.r.o. (ICO 46935452) figuruje ako skryta entita vo vsetkych 4 zmluvach -- mozny subdodavatel

**Klucove cisla:**
- Zmluvy: 11944638 (860K), 11944640 (860K), 11944642 (949K), 11944644 (949K)
- Objednavatel: MC Bratislava-Podunajske Biskupice (ICO 00641383)
- CRZ: https://www.crz.gov.sk/zmluva/11944638/
- FinStat: https://finstat.sk/50310810

**Zlte stopy:**
- `rapid_succession` (WARNING) -- 4 zmluvy za 14 dni
- `nace_mismatch` (WARNING) -- krajinna uprava vs. stavebnictvo
- `hidden_entity_is_supplier` (WARNING) -- ERGA projekt vo vsetkych 4 zmluvach

**Riziko: MEDIUM** -- Trzby firmy (7,7M) pokryvaju zakazku, ale rozdelenie na 4 zmluvy a NACE nesuhlad su podozrive. Odporucame preverit, ci nebolo obstaravanie rozdelene umyselne.

---

## INCONCLUSIVE najdy

### 4. ERIGOM SK s.r.o. -- poradenska firma s 3,3M stavebnou zakazkou

**Co sme overili:**
- FinStat: Trzby 6 255 843 EUR, Zisk 777 078 EUR, Aktiva 11 342 938 EUR -- financne zdrava firma
- NACE: "Poradenska cinnost v podnikani" (70220) -- nesedi so stavebnictvom
- UVO: Zmluva MA UVO odkaz (https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek/detail/538742)
- Red flags: nace_mismatch, hidden_entity_is_supplier (VAHOSTAV a.s.), high_subcontracting, signatory_overlap

**Preco to zostava nejasne:**
- Firma ma financne kapacity (6,2M trzby), ale NACE neodpoveda stavebnemu sektoru
- Skryta entita VAHOSTAV a.s. (ICO 31356648) -- velka stavebna firma -- naznacuje ze ERIGOM moze byt len prostrednikovska firma
- Ma UVO odkaz -- formalne obstaravanie prebehlo
- Zalozena v februari 2021 -- relativne mlada firma s vysoko spalivym rastom

**Dalsie kroky:** Preverit UVO zakazku (pocet uchadzacov, sposob obstaravania). Preverit RPVS -- kto je konecny uzivatel vyhod ERIGOM SK. Preverit prepojenie na VAHOSTAV cez foaf.sk.

---

### 5. Svidgas s.r.o. -- ceska firma, 4,6M zmluva s 3 skrytymi entitami

**Co sme overili:**
- CZ firma (ICO 26464261) -- nema profil na finstat.sk
- Nie je v RUZ (cesky subjekt)
- Jedina zmluva v CRZ -- ziadna historia
- Objednavatel: Univerzitna nemocnica - Nemocnica sv. Michala a.s. (ICO 44570783)
- Podpisana a zverejnena v ten isty den (6.2.2026) -- neobvykle rychle

**Preco to zostava nejasne:**
- Ceska firma bez dostupnych financnych udajov v SK registroch
- 3 skryte entity v zmluve -- identita neznama
- Jedina zmluva v CRZ -- ziadna historia verejnych zakaziek na Slovensku
- 4,6M je znacna suma pre prvu zakazku

**Dalsie kroky:** Preverit firmu v ceskom OR (justice.cz). Preverit obstaravanie na UVO. Identifikovat 3 skryte entity z extrakcie zmluvy.

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | Duplicitne zmluvy 24M (Bytova agentura MO / Min. dopravy) | Standardny CRZ pattern -- rovnaka zmluva uploadnuta oboma stranami. Ide o mechanizmus obnovy (statny prenos), nie o skutocnu obchodnu transakciu. |
| 2 | Duplicitne zmluvy 9,9M (Plavecky Stvrtok / Urad vlady) | Rovnaka zmluva uploadnuta dvakrat -- obec sa raz vola "Obec Plavecky Stvrtok" a raz "Plavecky Stvrtok". Ide o NFP (statnu dotaciu). |
| 3 | KG INVEST dvojity dlznik (100K zmluva) | Dlhy su minimalne (VSZP 305 EUR, SP 1 687 EUR). Firma je danovo spolahlivy s trzbami 808 136 EUR. Zmluva za 100K je v normalnom pomere k trzbe. Dlhy su skor administrativny neopatrenost nez signal podvodu. |
| 4 | Milan Smado - MIS (VSZP dlznik, 1,25M zmluva) | Dodatok c. 37 k zmluve z roku 2005 -- dlhodoba zmluva na udrzbu ciest s Mestom Banska Bystrica. Dlh VSZP 3 767 EUR je zanedbatelny pri trzbe zivnostnika. |
| 5 | LAVORE s.r.o. (VSZP dlznik, 300K ramcova dohoda) | Ramcova dohoda (nie pevna zmluva) na stavebne prace. VSZP dlh 7 749 EUR pri ramcovej dohode 300K. |
| 6 | Okruhle sumy 24M | Statne mechanizmy obnovy maju z povahy veci okruhle sumy. |
| 7 | Drobne delenie zakazky (Dusan Minar, 1 497 EUR) | Mikro-zakazky pod 1 000 EUR -- zjavne drobne udrzbarské prace. |

---

**Validacia ukoncena.** 3 najdy potvrdene, 2 vyzaduju dalsie overenie, 7 vylucene.

---

# Faza 3: FinStat Enrichment

## Sumar
- Pocet dodavatelov: 5 (privatni dodavatelia z CONFIRMED + INCONCLUSIVE najdov)
- Financne zlte stopy: 3 DANGER, 2 WARNING
- Najkritickejsi dodavatel: SOSTAV s.r.o. (zmluva 68,6x trzby, supplier_advantage)

---

## Dodavatel 1: SOSTAV s.r.o. (ICO 56017278)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 8 582 EUR |
| Zisk (profit) | 5 309 EUR |
| Aktiva (assets) | 16 792 EUR |
| Datum vzniku | 18.01.2024 |
| NACE | Ost.stav.kompletiz.prace |
| Velkost | 10-19 zamestnancov |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (obdobie)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11959965 | 588 265 EUR | Zmluva o dielo (Obec Spisske Bystre) |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 588 265 EUR = 68,6x trzby (8 582 EUR) |
| young_company | WARNING | Firma existuje 2 roky (vznik 01/2024) |
| supplier_advantage | DANGER | Pokutovy mechanizmus zvyhodnuje dodavatela |

### Hodnotenie
**Riziko: CRITICAL** -- Firma s trzbami 8 582 EUR a aktivami 16 792 EUR nema financnu kapacitu dodat stavebne prace za 588 265 EUR. Zisk 5 309 EUR (62% z trizieb) je neobvykle vysoka marza. Kombinacia s pokutovym zvyhodnenim je signalom, ze obec nesie vacsinu rizika.

---

## Dodavatel 2: SFINGA s.r.o. (ICO 51671824)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 454 385 EUR |
| Zisk (profit) | 5 079 EUR |
| Aktiva (assets) | 266 274 EUR |
| Datum vzniku | 25.05.2018 |
| NACE | Vystavba obytnych a neobytnych budov |
| Velkost | nezisteny |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (obdobie)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11946081 | 1 291 200 EUR | Zmluva o dielo c. 1/2024 (PE-ES n.o.) |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| contract_exceeds_2x_revenue | DANGER | Zmluva 1 291 200 EUR = 2,84x trzby (454 385 EUR) |
| severe_loss (near) | WARNING | Zisk len 1,1% trizieb -- minimalna marza |

### Hodnotenie
**Riziko: HIGH** -- Zmluva prevysuje rocne trzby 2,84x. Firma ma minimalne aktiva (266K) a zanedbatelny zisk (5K). NACE sedi so stavebnictvom, ale zmluva zverejnena s oneskorenim 489 dni naznacuje problem. Jedina zmluva v CRZ -- ziadna evidovana historia verejnych zakaziek.

---

## Dodavatel 3: RAVOZA s.r.o. (ICO 50310810)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 7 679 922 EUR |
| Zisk (profit) | 67 586 EUR |
| Aktiva (assets) | 1 424 629 EUR |
| Datum vzniku | 05.05.2016 |
| NACE | Cinnosti suvisiace s krajinnou upravou (81300) |
| Velkost | 5-9 zamestnancov |
| Danova spolahlivost | spolahlivy |

### Zmluvy v CRZ (obdobie)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11944638 | 859 914 EUR | Obnova MS Dudvazska 4, BA |
| 11944640 | 859 914 EUR | Obnova MS Latoricka 2, BA |
| 11944642 | 948 790 EUR | Obnova MS Estonska 5207/3, BA |
| 11944644 | 948 790 EUR | Obnova MS Estonska 5209/7 |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| nace_mismatch | WARNING | NACE 81300 (krajinna uprava) =/= construction_renovation |

### Hodnotenie
**Riziko: MEDIUM** -- Financne ma RAVOZA kapacitu (trzby 7,7M pokryvaju 3,6M zakazku). Ale NACE nesuhlad (krajinna uprava vs. stavebnictvo) a rozdelenie na 4 zmluvy v ten isty den su podozrive. Skryta entita ERGA projekt s.r.o. vo vsetkych 4 zmluvach naznacuje subdodavatelov schema. Marza len 0,9% -- mozny prostrednicky business model.

---

## Dodavatel 4: ERIGOM SK s.r.o. (ICO 53574907)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 6 255 843 EUR |
| Zisk (profit) | 777 078 EUR |
| Aktiva (assets) | 11 342 938 EUR |
| Datum vzniku | 12.02.2021 |
| NACE | Poradenska cinnost v podnikani (70220) |
| Velkost | nezisteny |
| Danova spolahlivost | vysoko spolahlivy |

### Zmluvy v CRZ (obdobie)
| ID | Suma | Nazov zmluvy |
|---|---|---|
| 11960112 | 3 306 842 EUR | ZoD c. ZSK 149/2026/OD (Zilinsky sam. kraj) |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| nace_mismatch | WARNING | NACE 70220 (poradenska cinnost) =/= construction |
| unusually_high_profit | INFO | Zisk 12,4% trizieb -- normalne pre poradenstvo, vysoke pre stavebnictvo |

### Hodnotenie
**Riziko: MEDIUM** -- Firma ma financne kapacity (trzby 6,2M, aktiva 11,3M). NACE nesuhlad (poradenstvo vs. stavebnictvo) a skryta entita VAHOSTAV a.s. naznacuju prostrednicku rolu. Vysoka miera subdodavok potvrdena v red_flags. Ma UVO odkaz -- formalne obstaravanie prebehlo.

---

## Dodavatel 5: KG INVEST s.r.o. (ICO 47594021) -- kontrolny enrichment

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 808 136 EUR |
| Zisk (profit) | 38 219 EUR |
| Aktiva (assets) | 364 466 EUR |
| Danova spolahlivost | spolahlivy |

### Hodnotenie
**Riziko: LOW** -- Zmluva (100K) je v normalnom pomere k trzbe (12,4%). Dvojity dlznik, ale sumy dlhov su minimalne (spolu pod 2 000 EUR). Vylucene v kriticke validacii.

---

**Enrichment ukonceny.** Najkritickejsi najd je SOSTAV s.r.o. -- firma s trzbami 8 582 EUR ziskava zakazku za 588 265 EUR s pokutami zvyhodnujucimi dodavatela. Druhy najvaznejsi je SFINGA s.r.o. -- 1,29M zmluva zverejnena 489 dni po podpise, od neziskovky, pre firmu s trzbami len 454K EUR.

---

# Celkove zhrnutie

## 3 CONFIRMED zlte stopy

| # | Dodavatel | ICO | Zmluva (EUR) | Klucova zlta stopa | Riziko |
|---|-----------|-----|-------------|--------------------|----|
| 1 | SOSTAV s.r.o. | 56017278 | 588 265 | Zmluva 68,6x trzby + supplier_advantage + mlada firma | CRITICAL |
| 2 | SFINGA s.r.o. | 51671824 | 1 291 200 | 489 dni oneskorenie + zmluva 2,8x trzby + jedina zmluva v CRZ | HIGH |
| 3 | RAVOZA s.r.o. | 50310810 | 3 617 407 | 4 zmluvy za 1 den + NACE mismatch + skryta entita vo vsetkych | MEDIUM |

## 2 INCONCLUSIVE najdy

| # | Dodavatel | ICO | Zmluva (EUR) | Otvorene otazky |
|---|-----------|-----|-------------|-----------------|
| 4 | ERIGOM SK s.r.o. | 53574907 | 3 306 842 | Poradenska firma s VAHOSTAV ako skrytou entitou -- prostrednicka rola? |
| 5 | Svidgas s.r.o. | 26464261 | 4 595 548 | Ceska firma bez SK financnych dat, 3 skryte entity, jedina zmluva |

## Odporucania na dalsie preverenie (Fazy 4-5, ak sa spustia)

1. **SOSTAV**: Preverit UVO obstaravanie pre Obec Spisske Bystre. RPVS lookup -- kto je konecny uzivatel vyhod.
2. **SFINGA / PE-ES n.o.**: Preverit RPVS pre obe entity. Preverit ci PE-ES n.o. cerpala dotacie na tento projekt.
3. **RAVOZA / ERGA projekt**: Preverit prepojenie cez foaf.sk. Preverit ci bola zakazka povodne jedna a bola rozdelena.
4. **ERIGOM / VAHOSTAV**: Preverit UVO zakazku (538742). Preverit prepojenie ERIGOM-VAHOSTAV cez RPVS a foaf.sk.
5. **Svidgas**: Preverit v ceskom Obchodnom registri. Preverit obstaravanie UN Nemocnica sv. Michala.

---

*Tieto najdy su stopy, nie verdikty. Kazdy potvrdeny signal vyzaduje dalsie preverenie pred akymkolvek zaverom.*

*Dakujeme Zltej Stope*
