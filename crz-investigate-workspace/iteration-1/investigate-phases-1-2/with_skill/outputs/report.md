# CRZ Investigativna analyza: 2026-03-01 -- 2026-03-07

---

# Faza 1: SQL Analytics

## Sumar
- Pocet zmluv v obdobi: 10 332
- Celkova suma: 658 911 762,63 EUR
- Pocet spustenych dopytov: 20
- Pocet dopytov s vysledkami: 17 (dopyt 10 Neuvedene, 11 Skupina dodavatelov a 19 Spiace firmy bez vysledkov)

## Top 5 najdov

1. **Prahovanie pod 215K EUR -- 4:1 nerovnomernost** -- 12 zmluv tesne pod EU prahom (210-215K) oproti iba 3 tesne nad (215-220K). Tento pomer (4:1) naznacuje systematicke vyhybanie sa povinnosti europskej sutaze.

2. **Zeleznicne stavby a.s. Kosice -- dvojity dlznik s verejna zakazkou** -- Firma s dlhom 158 313 EUR voci VSZP a 225 531 EUR voci Socialnej poistovni uzavrela zmluvu o uznani dlhu za 21 084 EUR. ICO 31714421.

3. **SVS Nitra s.r.o. -- sukromna firma so zapornym vlastnym imanim -242 237 EUR ziskala zakazku za 287 558 EUR** -- Sukromna stavebna firma (nie statna organizacia) s vyraznym zapornym vlastnym imanim ziskala zmluvu o dielo od Mesta Trencianske Teplice.

4. **HDH development s.r.o. -- sukromna firma so zapornym vlastnym imanim -89 462 EUR ziskala zakazku za 107 994 EUR** -- Sukromna inzinierska firma so zapornym vlastnym imanim ziskala zmluvu o poskytovani sluzieb od Spravy NP Muranska planina.

5. **ELITTE s.r.o. a TREBAN AT s.r.o. -- dvojiti dlznici s dlhovymi zmluvami** -- Obe firmy su dlznikmi VSZP aj Socialnej poistovne. ELITTE (dlh VSZP 24 336 EUR, SocPoist 14 983 EUR), TREBAN AT (dlh VSZP 15 851 EUR, SocPoist 41 451 EUR). Obe uzavreli zmluvy o uznani dlhu s VZP.

---

## 1. Toky penazi

### 1.1 Top dodavatelia podla celkovej sumy

| Dodavatel | ICO | Pocet | Celkom (EUR) |
|-----------|-----|-------|--------------|
| Narodna dialnicna spolocnost, a.s. | 35919001 | 9 | 260 640 495,27 |
| (NULL ICO -- 2 275 roznych dodavatelov) | - | 2 722 | 42 677 326,32 |
| MIRRI SR | 50349287 | 46 | 35 176 032,50 |
| zares, spol. s r.o. | 35778806 | 1 | 34 999 999,99 |
| MPSVR SR | 00681156 | 16 | 10 260 449,20 |
| Biomedical Engineering, s.r.o. | 45329818 | 1 | 9 991 432,10 |
| MZP SR | 42181810 | 4 | 9 875 943,00 |
| Ditec, a.s. | 31385401 | 4 | 9 475 108,20 |
| STVR | 56398255 | 5 | 7 210 333,00 |
| ELCON BRATISLAVA, a.s. | 35711299 | 1 | 6 246 063,00 |

**Interpretacia:** NDS dominuje s 260,6M EUR (dialnicne zakazky). Druhy riadok je artefakt -- 2 275 roznych dodavatelov bez ICO (fyzicke osoby, freelanceri) zgrupenych dohromady. MIRRI poskytuje NFP dotacie. zares, spol. s r.o. dostal jednu zakazku za 35M od hl. mesta Bratislavy.

### 1.2 Koncentracia objednavatel-dodavatel

| Objednavatel | Dodavatel | Pocet | Celkom (EUR) |
|--------------|-----------|-------|--------------|
| Ministerstvo dopravy SR | NDS, a.s. | 1 | 260 633 521,57 |
| SEPS, a.s. | Skupina dodavatelov Elektrovod + OMEXOM | 1 | 35 629 534,23 |
| Hlavne mesto SR Bratislava | zares, spol. s r.o. | 1 | 34 999 999,99 |
| MZ SR | Biomedical Engineering, s.r.o. | 1 | 9 991 432,10 |
| MSVVaM SR | Ditec, a.s. | 4 | 9 475 108,20 |
| Nitriansky samospravny kraj | MIRRI SR | 2 | 8 087 495,88 |
| MIRRI | STVR | 2 | 7 204 674,38 |
| Trnavsky samospravny kraj | MIRRI SR | 2 | 6 644 449,32 |
| SEPS, a.s. | ELCON BRATISLAVA, a.s. | 1 | 6 246 063,00 |
| NURC | MZ SR | 1 | 6 150 000,00 |

**Interpretacia:** 61 parov dodavatel-objednavatel presahlo 1M EUR. Najvacsie sumy su standardne infrastrukturne a dotacne toky (NDS, MIRRI). Zvlast zaujimava je zmluva zares s.r.o. za 35M od Bratislavy a Biomedical Engineering za 10M od MZ SR.

### 1.3 Servisne kategorie

| Kategoria | Pocet | Celkom (EUR) |
|-----------|-------|--------------|
| grant_subsidy | 742 | 356 966 988,65 |
| construction_renovation | 333 | 123 284 207,71 |
| easement_encumbrance | 160 | 16 119 596,74 |
| procurement_purchase | 292 | 15 263 987,38 |
| software_it | 176 | 14 880 249,96 |
| other | 365 | 12 162 480,60 |
| professional_consulting | 536 | 11 604 137,95 |

**Interpretacia:** Dotacie a granty tvoria 54% celkoveho objemu. Stavebne zakazky su druhe s 18%.

---

## 2. Manipulacia obstaravania

### 2.1 Delenie zakazky

Najdene 128 parov dodavatel-objednavatel s 5+ zmluvami (kazda pod 50 000 EUR).

Najvyznamnejsie:

| Dodavatel | ICO | Objednavatel | Pocet | Celkom (EUR) |
|-----------|-----|--------------|-------|--------------|
| Martin Juricka, Katarina Jurickova | - | SIEA | 31 | 155 700,00 |
| Zeleznice SR | 31364501 | Miroslav Tomanek a Jozefina Burcova | 19 | 85 797,89 |
| Toth Martin | - | UPSVaR Bratislava | 21 | 82 829,70 |
| Tesfamariam Teklu Gebretsadik | - | UPJS Kosice | 31 | 75 609,00 |
| Homolova Tothova Veronika | - | STVR | 129 | 57 370,00 |
| DXC Technology Slovakia s.r.o. | 35785306 | MO SR | 6 | 51 898,62 |

**Interpretacia:** Vacsina "delenia zakazky" su v skutocnosti freelancerske zmluvy (Erasmus granty, opatrovatelske dohody, pohrebne prenajmy). DXC Technology s 6 zmluvami pre MO SR za 51 898 EUR je jediny komereny pripad hodny pozornosti, ale sumy su niske.

### 2.2 Prahovanie pod EU sutaznym limitom (215K EUR)

| Pasmo | Pocet | Celkom (EUR) |
|-------|-------|--------------|
| Tesne pod (210-215K) | 12 | 2 538 339,63 |
| Tesne nad (215-220K) | 3 | 651 599,99 |

**Pomer: 4:1 v prospech zmluv tesne pod prahom.**

Vybrane zmluvy tesne pod prahom:
- CS, s.r.o. -- Zmluva o dielo, 214 896,13 EUR (Sprava a udrzba ciest Trnavsky kraj)
- Obec Dulovce -- Plan obnovy, 213 361,68 EUR (SIEA)
- TERRATECHNIK -- Zmluva o dielo, 213 122,54 EUR (Podtatranska vodarenska)
- MS Druzstevna Sala -- Plan obnovy, 212 881,10 EUR (SIEA)
- Obec Nizna -- Plan obnovy, 212 618,38 EUR (SIEA)
- TOPSTAV -- Dodatok k ZoD, 210 177,58 EUR (Mesto Hurbanovo)
- MAHOLZ s.r.o. -- Kupna zmluva, 210 099,00 EUR (BBSK)
- SFRB zmluvne zabezpecenie -- 210 000-210 170 EUR (2 zmluvy)
- Slov. sporitelna uver -- 210 000 EUR
- CSOB platobne karty -- 210 000 EUR

**Interpretacia:** Z 12 zmluv tesne pod prahom su 3 Plan obnovy od SIEA (standardizovane sumy), 2 SFRB zalozne prava a 1 bankovy uver -- tieto su nevinne. Zvysne (CS s.r.o., TERRATECHNIK, TOPSTAV, MAHOLZ) su stavebne zakazky, kde je vyhybanie sa EU sutaze realne mozne.

### 2.3 Okruhle sumy (nasobky 100K)

| ID | Nazov zmluvy | Dodavatel | Suma (EUR) |
|----|-------------|-----------|------------|
| 12048092 | Terminovany uver | VUB | 4 000 000,00 |
| 12053659 | Environmentalny fond uver | Env. fond | 2 800 000,00 |
| 12065292 | Dotacia MPSVR | Jednota dochodcov | 800 000,00 |
| 12064722 | Terminovany uver | VUB | 500 000,00 |
| 12058676 | Dotacia na sportoviska | Mesto Partizanske | 400 000,00 |
| 12059640 | Dotacia | Mesto Partizanske | 400 000,00 |
| 12067567 | SFRB zalozne pravo | Vlastnici bytov | 300 000,00 |
| 12062918 | Ramcova kupna zmluva | SEKO Trencin | 200 000,00 |
| 12066041 | Ramcova dohoda potraviny | KON-RAD | 200 000,00 |

**Interpretacia:** Vacsina okruhlych sum su bankove uvery (VUB), statne dotacie (MPSVR, Env. fond, SFRB) a ramcove zmluvy -- u ktorych su okruhle sumy standardne.

---

## 3. Casove anomalie

### 3.1 Zverejnenie cez vikend

| ID | Dodavatel | Suma (EUR) | Datum | Den |
|----|-----------|------------|-------|-----|
| 12048092 | VUB, a.s. | 4 000 000,00 | 2026-03-01 (Ne) | Nedela |
| 12048038 | TAMALEX s.r.o. | 982 170,10 | 2026-03-01 (Ne) | Nedela |
| 12048040 | Metrostav DS a.s. | 725 699,98 | 2026-03-01 (Ne) | Nedela |
| 12048042 | Metrostav DS a.s. | 330 624,00 | 2026-03-01 (Ne) | Nedela |
| 12048076 | Tech. sluzby Novot | 133 878,44 | 2026-03-01 (Ne) | Nedela |

**Interpretacia:** Vsetky vikendove zmluvy boli zverejnene v nedelu 1. marca 2026. Celkovo v tento den bolo zverejnenych iba 35 zmluv (oproti 2 400-2 700 v bezne pracovne dni), takze ide skor o automatizovany upload nez o ukryvanie zmluv.

### 3.2 Neskor zverejnene zmluvy

| ID | Dodavatel | Suma (EUR) | Datum podpisu | Datum zverejnenia | Omeskanie |
|----|-----------|------------|---------------|--------------------| ----------|
| 12050023 | Obec Kosicka Polianka | 181 653,08 | 0202-02-19 | 2026-03-02 | 666 214 dni |

**Interpretacia:** Jediny vysledok je zjavny datovy artefakt -- datum podpisu "0202-02-19" je chybny zaznam, nie skutocne omeskanie. DISMISSED.

---

## 4. Fantomovi dodavatelia

### 4.1 Dodavatelia bez ICO s vysokou hodnotou (>100K EUR)

| ID | Dodavatel | Suma (EUR) | Objednavatel |
|----|-----------|------------|--------------|
| 12058856 | Ministerstvo fondov a reg. politiky | 980 230,94 | Obec Bobrov |
| 12049281 | Lek. fakulta UK + SAV konzorcium | 847 530,00 | UK JLF Martin |
| 11067904 | Skupina dodavatelov Elektrovod+OMEXOM | 35 629 534,23 | SEPS |
| 12065054 | Min. zahr. veci Madarskej republiky | 223 646,20 | BBSK |
| 12053309 | CS, s.r.o. | 214 896,13 | SUC TTSK |
| 12062103 | CSOB, a.s. | 210 000,00 | ZSSK |
| 12068394 | Zuzana Vaseckova | 174 482,55 | Matica slovenska |

**Interpretacia:** Vacsina vysokohodnotnych zmluv bez ICO su ministerstva, zahranicne entity (Madarsko) alebo konzorcia. CS, s.r.o. bez ICO pri stavebnej zakazke za 214 896 EUR je podozrive -- blizko EU prahu a bez identifikacie dodavatela.

### 4.2 Neuvedene dodavatelia
Ziaden vysledok nad 10 000 EUR.

### 4.3 Skupiny dodavatelov (konzorcia)
Ziaden vysledok (Elektrovod+OMEXOM nemal v nazve "skupina dodavatelov" podla filtru -- ale objavil sa v dotaze 9 bez ICO).

---

## 5. Extrakcie

### 5.1 Pokuty zvyhodnujuce dodavatela (supplier_advantage)

| ID | Nazov | Dodavatel | Suma (EUR) |
|----|-------|-----------|------------|
| 12053590 | Dodatok c. 2 k Zmluve o uvere | Mesto Senica | 1 763 380,00 |
| 12056515 | Environmentalny fond uver | Env. fond | 412 050,00 |
| 12062096 | Dohoda o uznani zavazku | Liptovska vodarenska | 381 283,32 |
| 12066703 | NFP zmluva MIRRI | MIRRI | 226 063,88 |
| 12052516 | Kupna zmluva | BIOHEM a.s. | 208 558,80 |

**Interpretacia:** Najvacsie zmluvy so zvyhodnenim dodavatela su uvery (SFRB/Env. fond) a NFP zmluvy -- u ktorych je asymetria pokut standardna (stat ako veritel). BIOHEM a.s. s kupnou zmluvou za 208 558 EUR je jediny komereny pripad.

### 5.2 Bezodplatne zmluvy
Celkom 131 bezodplatnych zmluv. Vacsina su kolektivne zmluvy, zmluvy o dodavke plynu/energie, najmy hrobovych miest, a zmluvy o spolupracovani. Najvyssia hodnotova zmluva oznacena ako bezodplatna: NFP MIRRI-BBSK 5 637 500 EUR (2x duplikat) -- NFP zmluvy standardne deklarovane ako bezodplatne.

### 5.3 Skryte entity (3+ v zmluve)

| ID | Dodavatel | Suma (EUR) | Pocet skrytych entit |
|----|-----------|------------|----------------------|
| 12052716 | Zilinsky samospravny kraj | 0,00 | 19 |
| 12053546 | MPSVR SR | 0,00 | 7 |
| 12059258 | OptiStav s.r.o. | 370 394,82 | 5 |
| 12070012 | Ruzinovský sportovy klub | 632 000,00 | 4 |
| 12048423 | StarFilm Pictures s.r.o. | 307 500,00 | 3 |

**Interpretacia:** Zmluvy s najvacsim poctom skrytych entit su dotacne zmluvy a zmluvy o spolupraci. OptiStav (370K, 5 entit) a StarFilm Pictures (307K, 3 entity) su hodne dalsieho preverenia.

---

## 6. Dlznicki

### 6.1 VSZP dlznici so statnou zakazkou

| Dodavatel | ICO | Pocet zmluv | Celkom zmluvy (EUR) | Dlh VSZP (EUR) |
|-----------|-----|-------------|---------------------|----------------|
| ZELEZNICNE STAVBY, A.S. KOSICE | 31714421 | 1 | 21 084,87 | 158 313,56 |
| ELITTE S.R.O. | 44518030 | 1 | 24 346,17 | 24 336,17 |
| CHIRASYS SR S.R.O. | 45604410 | 1 | 10 313,42 | 17 866,68 |
| TREBAN AT, S.R.O. | 47401001 | 1 | 15 851,46 | 15 851,46 |

**Interpretacia:** Zeleznicne stavby a.s. Kosice vynika s dlhom 158K EUR voci VSZP. Kontrakty su vsak "Uznanie dlhu a dohoda o splateni" -- tieto firmy nie su dodavateliami v klasickom zmysle, ale dlznikmi, ktori si uznavaju dlh voci VZP.

### 6.2 Socialnej poistovne dlznici

| Dodavatel | ICO | Celkom zmluvy (EUR) | Dlh SocPoist (EUR) |
|-----------|-----|---------------------|--------------------|
| EDI777 s.r.o. | 50677641 | 112 500,00 | 0,00 |
| LAKAVA Kvalita s.r.o. | 45658633 | 66 297,00 | 166,60 |
| Socialny podnik s.r.o. | 54487471 | 52 938,28 | 0,00 |
| RELES ELEKTRO s.r.o. | 51466759 | 44 939,00 | 101,82 |
| PRIEMSTAV s.r.o. | 44578563 | 39 295,49 | 5 558,09 |
| ZELEZNICNE STAVBY, A.S. | 31714421 | 21 084,87 | 225 531,34 |
| KRANKAS s.r.o. | 36372111 | 100,00 | 73 960,40 |

**Interpretacia:** EDI777 s.r.o. je najvyznamnejsie -- zmluva za 112 500 EUR s deklarovanym dlhom SocPoist 0 EUR (moze byt splneny). PRIEMSTAV s dlhom 5 558 EUR a kontraktom 39 295 EUR je mierny pripad. KRANKAS s dlhom 73 960 EUR a kontraktom len 100 EUR je zaujimava anomalia.

### 6.3 Dvojiti dlznici (VSZP + SocPoist sucasne)

| Dodavatel | ICO | Celkom zmluvy (EUR) | Dlh VSZP (EUR) |
|-----------|-----|---------------------|----------------|
| ZELEZNICNE STAVBY, A.S. KOSICE | 31714421 | 21 084,87 | 158 313,56 |
| ELITTE S.R.O. | 44518030 | 24 346,17 | 24 336,17 |
| TREBAN AT, S.R.O. | 47401001 | 15 851,46 | 15 851,46 |
| SIRO, S.R.O. | 36217506 | 3 058,11 | 3 000,66 |

**Interpretacia:** 4 firmy su dvojitymi dlznikmi. Vsetky ich zmluvy su vsak "Uznanie dlhu a dohoda o splateni" s VZP -- nie su to klasicke verejne zakazky, ale formalizacia existujuceho dlhu.

---

## 7. Bonusove kontroly

### 7.1 Dodavatelia so zapornym vlastnym imanim

| Dodavatel | ICO | Pocet | Celkom (EUR) | Vlastne imanie (EUR) |
|-----------|-----|-------|--------------|----------------------|
| SVS Nitra, s.r.o. | 35922737 | 1 | 287 558,49 | -242 237,00 |
| Zakladna skola Eliasa Laniho | 37808591 | 1 | 268 241,69 | -1 929,00 |
| HDH development, s.r.o. | 35912804 | 1 | 107 994,00 | -89 462,00 |

**Interpretacia:** ZS Eliasa Laniho je rozpoctova organizacia v samosprave -- zaporne vlastne imanie je bezne. SVS Nitra a HDH development su sukromne s.r.o., co je vyznamnejsie.

### 7.2 Spiace firmy (dormant-then-active)
Ziaden vysledok.

### 7.3 Denne rozlozenie objemu

| Den | Pocet | Celkom (EUR) | Den v tyzdni |
|-----|-------|--------------|--------------|
| 2026-03-05 (St) | 2 561 | 378 378 359,03 | Stvrtok |
| 2026-03-04 (Ut) | 2 667 | 142 898 113,82 | Streda |
| 2026-03-02 (Po) | 2 548 | 71 852 415,49 | Pondelok |
| 2026-03-03 (Ut) | 2 440 | 59 430 728,48 | Utorok |
| 2026-03-01 (Ne) | 35 | 6 338 542,15 | Nedela |
| 2026-03-07 (So) | 81 | 13 603,66 | Sobota |

**Interpretacia:** Stvrtok 5.3.2026 mal najvyssi objem (378M EUR) vdaka jednej obrovskej NDS zmluve (260M EUR). Vikend (nedela, sobota) mal minimalny pocet zmluv (35 a 81).

---

## Zhrnutie najdov

| # | Nazov najdu | Kategoria | Severity | Pocet zaznamov |
|---|-------------|-----------|----------|----------------|
| 1 | NULL ICO zgrupovania (2 275 freelancerov) | Fantomovi dodavatelia | Artefakt | 2 722 |
| 2 | Prahovanie pod 215K EUR (12 vs 3) | Manipulacia obstaravania | Warning | 15 |
| 3 | Vikendove zverejnenie 1.3.2026 | Casove anomalie | Info | 5 |
| 4 | Neskor zverejnena zmluva (666K dni) | Casove anomalie | Artefakt | 1 |
| 5 | Okruhle sumy (nasobky 100K) | Manipulacia obstaravania | Info | 12 |
| 6 | Supplier advantage penalties | Extrakcie | Warning | 5 |
| 7 | Bezodplatne zmluvy | Extrakcie | Info | 131 |
| 8 | Skryte entity (3+) | Extrakcie | Warning | 65 |
| 9 | VSZP dlznici | Dlznicki | Warning | 30 |
| 10 | SocPoist dlznici | Dlznicki | Warning | 21 |
| 11 | Dvojiti dlznici (VSZP+SocPoist) | Dlznicki | Danger | 4 |
| 12 | Zaporne vlastne imanie (sukromne firmy) | Bonusove kontroly | Danger | 2 |
| 13 | CS s.r.o. bez ICO, tesne pod prahom | Fantomovi dodavatelia | Warning | 1 |
| 14 | Contract splitting DXC Technology | Manipulacia obstaravania | Info | 6 |

**Tieto najdy este neboli validovane** -- pokracujeme Fazou 2 (kriticka validacia).

---
---

# Faza 2: Kriticka validacia

## Sumar validacie
- Pocet najdov na vstupe: 14
- CONFIRMED: 3
- DISMISSED: 8
- INCONCLUSIVE: 3

---

## CONFIRMED najdy

### 1. SVS Nitra, s.r.o. -- sukromna stavebna firma so zapornym vlastnym imanim ziskava zakazku -- Danger

**Povodny najd:** SVS Nitra, s.r.o. (ICO 35922737), sukromna s.r.o. so zapornym vlastnym imanim -242 237 EUR, ziskala zmluvu o dielo za 287 558,49 EUR od Mesta Trencianske Teplice.

**Validacne kroky:**
1. Overenie v ruz_entities: potvrdene -- Spol. s r.o., sukromne tuzemske, NACE: Vystavba obytnych a neobytnych budov, zalozena 2005-02-24.
2. Overenie v ruz_equity: vlastne imanie -242 237 EUR.
3. Overenie v registroch dlznikov: firma nie je evidovana v VSZP ani SocPoist registri.

**Preco to nie je falesny pozitiv:**
- Nejde o statnu organizaciu ani prispevkovu organizaciu, kde by zaporne vlastne imanie bolo bezne.
- Je to sukromna stavebna firma -- zaporne vlastne imanie -242K EUR pri zakazke 287K naznacuje financne problemy.
- Firma moze mat problemy s plnenim zmluvy.

**Klucove cisla:** Zmluva ID 12064598, ICO 35922737, suma 287 558,49 EUR, vlastne imanie -242 237 EUR. CRZ: https://www.crz.gov.sk/zmluva/12064598/

---

### 2. HDH development, s.r.o. -- sukromna inzinierska firma so zapornym vlastnym imanim ziskava zakazku -- Danger

**Povodny najd:** HDH development, s.r.o. (ICO 35912804), sukromna s.r.o. so zapornym vlastnym imanim -89 462 EUR, ziskala zmluvu o dielo za 107 994 EUR od Spravy NP Muranska planina.

**Validacne kroky:**
1. Overenie v ruz_entities: potvrdene -- Spol. s r.o., sukromne tuzemske, NACE: Ostatne inzinierske cinnosti, zalozena 2004-12-17.
2. Overenie v ruz_equity: vlastne imanie -89 462 EUR.
3. Overenie v registroch dlznikov: firma nie je evidovana v VSZP ani SocPoist registri.

**Preco to nie je falesny pozitiv:**
- Nejde o statnu organizaciu -- je to sukromna inzinierska firma.
- Pomer: zakazka 107 994 EUR presahuje absolutnu hodnotu zaporneho imania (89 462 EUR).
- Zmluva o poskytovani sluzieb pre narodny park -- statny objednavatel by mal overovat financne zdravie dodavatela.

**Klucove cisla:** Zmluva ID 12063040, ICO 35912804, suma 107 994,00 EUR, vlastne imanie -89 462,00 EUR. CRZ: https://www.crz.gov.sk/zmluva/12063040/

---

### 3. Prahovanie pod EU sutaznym limitom -- 4 stavebne zakazky tesne pod 215K -- Warning

**Povodny najd:** 12 zmluv v pasme 210-215K EUR oproti 3 v pasme 215-220K EUR (pomer 4:1). Statisticky nerovnomerny rozlozenie naznacuje vyhybanie sa EU sutazi.

**Validacne kroky:**
1. Kontrola typov zmluv: 3 z 12 su Plan obnovy granty od SIEA (standardizovane sumy), 2 su SFRB zalozne prava, 1 je bankovy uver, 1 je CSOB zmluva o platobnych kartach -- tieto 7 su nevinne.
2. 4-5 zvysnycH zmluv su stavebne zakazky: CS s.r.o. (214 896 EUR), TERRATECHNIK (213 122 EUR), TOPSTAV (210 177 EUR), MAHOLZ (210 099 EUR).
3. CS s.r.o. navyse nema ICO v systeme.

**Preco to nie je falesny pozitiv:**
- Po vyluceni nevinnych typov (dotacie, uvery, SFRB) ostavaju 4-5 stavebnych zakazok tesne pod prahom.
- CS, s.r.o. bez ICO s cenou 214 896 EUR (118 EUR pod prahom) od Spravy ciest TTSK je najsuspektnejsia.
- Aj ked samotne jednotlive pripady mozu byt nahodne, vzor poukazuje na systematicke vyhybanie sa.

**Klucove cisla:**
- CS, s.r.o.: ID 12053309, 214 896,13 EUR, bez ICO
- TERRATECHNIK: ID 12054420, 213 122,54 EUR
- TOPSTAV: ID 12058250, 210 177,58 EUR (dodatok!)
- MAHOLZ: ID 12053796, 210 099,00 EUR

---

## INCONCLUSIVE najdy

### 4. CS, s.r.o. -- bez ICO, stavebna zakazka tesne pod EU prahom

**Co sme overili:** Zmluva o dielo za 214 896,13 EUR pre Spravu a udrzbu ciest Trnavsky kraj. Dodavatel nema ICO v systeme CRZ, co je neobvykle pre slovensku s.r.o.
**Preco to zostava nejasne:** Nevieme, ci ICO chyba len v CRZ alebo ci firma realne nema ICO (napr. zahranicna entita). Cena je 118 EUR pod EU prahom 215 000 EUR.
**Dalsie kroky:** Overit na FinStat/ORSR podla nazvu "CS, s.r.o.", skontrolovat original zmluvy na CRZ (https://www.crz.gov.sk/zmluva/12053309/).

### 5. OptiStav s.r.o. -- zmluva za 370K so 5 skrytymi entitami

**Co sme overili:** Zmluva o dielo c. Z26 za 370 394,82 EUR s 5 skrytymi entitami v texte zmluvy.
**Preco to zostava nejasne:** Nevieme, ake entity su skryte -- mozu byt subdodavatelia, rucitelia, alebo ine strany. Vyssi pocet skrytych entit je neobvykly pre standardnu zmluvu o dielo.
**Dalsie kroky:** Prezriet extrakciu (extraction_json), skontrolovat FinStat pre ICO OptiStavu, overit foaf.sk sietove prepojenia.

### 6. StarFilm Pictures s.r.o. -- koprodukcna zmluva za 307K so 3 skrytymi entitami

**Co sme overili:** Koprodukcna zmluva za 307 500 EUR so 3 skrytymi entitami.
**Preco to zostava nejasne:** Koprodukcne zmluvy vo filmovom priemysle bezne zahrnuju viacero stran. 3 skryte entity mozu byt koproducenti.
**Dalsie kroky:** Overit na FinStat, skontrolovat ci ide o standardnu filmovu koprodukciu alebo neobvyklu strukturu.

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | NULL ICO zgrupovania (2 275 freelancerov) | **Datovy artefakt.** 2 275 roznych mien zgrupenych pod NULL ICO. Klasicky Sulc Matej pattern -- nejde o jedneho dodavatela ale o tisicky freelancerov (Erasmus, STVR, APVV). |
| 2 | Vikendove zverejnenie 1.3.2026 | **Standardny vzor.** Iba 35 zmluv zverejnenych v nedelu (oproti 2 400-2 700 v pracovne dni). VUB uver a Metrostav ramcove zmluvy su rutinne. Niska aktivita naznacuje automatizovany upload, nie ukryvanie. |
| 3 | Neskor zverejnena zmluva (666K dni) | **Datovy artefakt.** Datum podpisu "0202-02-19" je zjavne chybny -- chybajuce tisicrocne v datume. Skutocny datum podpisu je pravdepodobne 2025-02-19 alebo 2026-02-19. |
| 4 | Okruhle sumy (nasobky 100K) | **Nevinny vzor.** 9 z 12 zmluv su bankove uvery (VUB), statne dotacie (MPSVR, Env. fond) a SFRB zalozne prava, kde su okruhle sumy standardne. Ramcove zmluvy (SEKO, KON-RAD) maju odhadovane objemy. |
| 5 | Supplier advantage penalties -- uvery a NFP | **Nevinny vzor.** Top 4 zmluvy so zvyhodnenim dodavatela su uvery (SFRB, Env. fond) a NFP zmluvy od MIRRI. Asymetricky pokutovy rezim je standardny pre veritelske zmluvy. |
| 6 | Bezodplatne zmluvy | **Nevinny vzor.** 131 bezodplatnych zmluv su kolektivne zmluvy, zmluvy o dodavke energii, najmy hrobovych miest, a NFP zmluvy. Vsetko standardne typy bezodplatnych zmluv. |
| 7 | ZS Eliasa Laniho -- zaporne vlastne imanie | **Statna organizacia.** Rozpoctova organizacia v samosprave (vlastnictvo uzemnej samospravy). Zaporne vlastne imanie -1 929 EUR je bezne pre skolske zariadenia. |
| 8 | Dvojiti dlznici (Zeleznicne stavby, ELITTE, TREBAN AT, SIRO) | **Kontextovy nevinny vzor.** Vsetky 4 zmluvy su "Uznanie dlhu a dohoda o jeho splatkach" s VZP a.s. -- firmy si formalizuju existujuci dlh, nie su prijemcami novych verejnych zakazok. |

---

**Validacia ukoncena.** 3 najdy potvrdene, 8 vylucene, 3 vyzaduje dalsie overenie.

---

## Fazove hradlo: Pokracovanie

Podla pravidiel crz-investigate:
- 3 CONFIRMED najdy --> Odporucanie: Fazy 3-4 na potvrdene ICO (SVS Nitra 35922737, HDH development 35912804, CS s.r.o.). Faza 5 na najsilnejsi lead (SVS Nitra).
- 3 INCONCLUSIVE najdy --> Faza 3 (FinStat) na overenie CS s.r.o., OptiStav, StarFilm Pictures.

*(Fazy 3-5 neboli vykonane podla zadania -- iba Fazy 1-2.)*

---

## Zaver

Obdobie 1.-7. marca 2026 obsahovalo 10 332 zmluv v celkovej hodnote 658,9M EUR. Z 20 analytickych dopytov sme identifikovali 14 potencialnych zlty stop. Po kritickej validacii:

**3 potvrdene zlte stopy:**
1. SVS Nitra, s.r.o. (ICO 35922737) -- sukromna stavebna firma s vlastnym imanim -242K EUR ziskala zakazku 287K EUR od Mesta Trencianske Teplice.
2. HDH development, s.r.o. (ICO 35912804) -- sukromna inzinierska firma s vlastnym imanim -89K EUR ziskala zakazku 108K EUR od Spravy NP Muranska planina.
3. Prahovanie pod EU limitom -- 4 stavebne zakazky tesne pod 215K EUR, najsuspektnejsia CS, s.r.o. (214 896 EUR, bez ICO).

**3 inconclusive najdy** vyzadujuce dalsie preverenie (FinStat, PDF review).

**8 dismissed najdov** -- datove artefakty, standardne statne toky, a dlhove dohody.

Tieto najdy su **stopy, nie verdikty**. Dalsie kroky: financna enrichment (FinStat), overenie obstaravania (UVO), a kontrola vlastnickych struktur (RPVS, foaf.sk).

> *Dakujeme Zltej Stope*
