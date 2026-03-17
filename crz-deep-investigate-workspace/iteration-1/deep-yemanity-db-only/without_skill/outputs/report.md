# Hlbkova investigativa: YEMANITY s.r.o. (ICO 55002072)

**Datum analyzy:** 2026-03-17
**Zdroj dat:** lokalna databaza crz.db
**Upozornenie:** Toto su stopy, nie verdikty. Kazdy nalez vyzaduje dalsie overenie.

---

## 1. Profil spolocnosti

| Parameter | Hodnota |
|---|---|
| **Nazov** | YEMANITY s.r.o. |
| **ICO** | 55002072 |
| **DIC** | 2121846254 |
| **Sidlo** | Vychylovka 1045, 023 05 Nova Bystrica |
| **Datum vzniku** | 16.11.2022 |
| **Pravna forma** | Spol. s r. o. |
| **NACE** | 70220 - Poradenske cinnosti v podnikani |
| **Velkost** | 1 zamestnanec (mikro) |
| **Region** | Zilinsky kraj, okres Cadca |
| **Danovy status** | Spolahlivy |
| **Konatelia** | Jan Sutiak, Filip Sobol |

**Klucovy nalez:** Firma registrovana ako poradenska spolocnost s 1 zamestnancom ziskala stavebne zakazky v celkovej hodnote 892 261,56 EUR za necelych 2 mesiacov.

---

## 2. Prehlad zmluv

| ID | Nazov zmluvy | Objednavatel | Suma (EUR) | Datum podpisu | UVO |
|---|---|---|---|---|---|
| 11889441 | Vystavba posilnovne pri VSH, Majova 19 Bratislava | Ekonomicka univerzita v Bratislave | 467 641,57 | 16.01.2026 | [UVO 544941](https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek/detail/544941) -- S110 |
| 12036751 | Zmluva o dielo -- Doplnkova budova pri ZpS Goral v Skalitom | Obec Skalite | 266 657,41 | 25.02.2026 | [UVO 548246](https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek/detail/548246) |
| 12058696 | Dodatok c. 1 k zmluve o dielo 802/2025 (ZS Jarna, Zilina) | Mesto Zilina | 351,99 | 27.02.2026 | -- |
| 12059873 | Kupna zmluva (bez ICO) | Obec Stara Bystrica | 0,00 | 03.03.2026 | -- |
| 12075436 | Dodatok k zmluve (Skalite -- recyklovane materialy) | Obec Skalite | 0,00 | 04.03.2026 | -- |
| 12088132 | Zvysenie bezpecnosti budov V1 a V2 EUBA -- stavebna cast | Ekonomicka univerzita v Bratislave | 157 610,59 | 10.03.2026 | -- |

**Celkom: 6 zmluv, suma 892 261,56 EUR, 4 unikatni objednavatelia, casove rozpatie 54 dni (16.01. -- 10.03.2026)**

---

## 3. Zlte stopy -- suhrn

| Zavaznost | Zlta stopa | Pocet zmluv |
|---|---|---|
| Warning | Nesulad odvetvia (NACE) | 4 |
| Warning | Mikro dodavatel, velka zmluva | 3 |
| Warning | Zdielany podpisujuci | 3 |
| Warning | Skryta cena | 1 |
| Info | Neuvedena platnost | 5 |
| Info | Dodavatel bez ICO | 1 |

**Celkom: 16 zlte stopy na 6 zmluvach**

---

## 4. Detailna analyza -- hlavne zistenia

### 4.1 NACE nesulad: poradenska firma realizuje stavebne prace

Toto je najzavaznejsia zlta stopa. YEMANITY s.r.o. je registrovana pod NACE 70220 (Poradenske cinnosti v podnikani), no vsetky jej zmluvy su stavebneho charakteru:

- **Vystavba posilnovne** (467 641 EUR)
- **Stavba doplnkovej budovy pri zariadeni pre seniorov** (266 657 EUR)
- **Zvysenie bezpecnosti budov -- stavebna cast** (157 610 EUR)
- **Debarierizacia ZS Jarna** (dodatok, 351 EUR)

Firma s 1 zamestnancom a poradenskou registraciou nemoze realisticky realizovat tieto stavebne prace vlastnymi kapacitami. S vysokou pravdepodobnostou ide o sprostredkovatela, ktory prace zadava subdodavatelom. Extrakcie potvrdili, ze zmluvy 12036751 a 12088132 explicitne spominaju subdodavky.

V databaze sme nasli 10 dalsich firiem s NACE 70220, ktore ziskali stavebne zakazky nad 50 000 EUR. Tento vzorec nie je ojedinely, ale v pripade YEMANITY je objem neobvykle vysoky na mikro firmu.

### 4.2 Mikro dodavatel s velkymi zakazkami

Firma s 1 zamestnancom ziskala 3 zmluvy nad 50 000 EUR:
- 467 641,57 EUR (posilnovna)
- 266 657,41 EUR (Skalite -- Goral)
- 157 610,59 EUR (bezpecnost EUBA)

**Celkovy objem 892 261 EUR v priebehu 54 dni** je extremne neobvykly pre mikro firmu zalozenu v roku 2022. Chybajuce financne udaje v tabulke `supplier_financials` a `ruz_equity` naznacuju, ze firma este nebola financne profilovana.

### 4.3 Geograficka koncentracia -- Kysucke obce

YEMANITY sidli v **Novej Bystrici** (okr. Cadca). Dvaja z jej objednavatelov su susedne obce v tom istom regione:
- **Obec Skalite** (023 14) -- susedna obec, 2 zmluvy v hodnote 266 657 EUR
- **Obec Stara Bystrica** (023 04) -- susedna obec, 1 zmluva (kupna zmluva bez sumy)

Geograficka blízkost dodavatela a objednavatela v malom vidiekom regione zvysuje riziko lokalnych vazieb a potencialneho konfliktu zaujmov.

### 4.4 Projekt bezpecnosti EUBA -- rozdelenie zakazky?

Projekt "Zvysenie bezpecnosti vyucbovych budov V1 a V2" Ekonomickej univerzity v Bratislave bol rozdeleny na dve casti:
- **Time & Data s.r.o.** (ICO 44862831) -- dodavka a montaz turniketov a EPS: **384 990,80 EUR** (zmluva 11949257, podpis 05.02.2026, s UVO linkom)
- **YEMANITY s.r.o.** -- stavebna cast: **157 610,59 EUR** (zmluva 12088132, podpis 10.03.2026, **bez UVO linku**)

**Celkova hodnota projektu:** 542 601,39 EUR

Zvlastne zistenia:
1. Stavebna cast (YEMANITY) **nema odkaz na verejne obstaravanie** na UVO, zatial co technologicka cast (Time & Data) ma
2. Rozdelenie na stavebnu a technologicku cast moze byt legitimne, ale absencia UVO linku pre stavebnu cast za 157 610 EUR je podozriva
3. YEMANITY ziskala od EUBA uz predtym zakazku za 467 641 EUR -- opakujuci sa dodavatel

### 4.5 Posilnovna EUBA -- S110 zakazka s nizkym limitom

Zmluva na vystavbu posilnovne (467 641,57 EUR) odkazuje na **S110** zakona o verejnom obstaravani. Paragraf 110 upravuje zakazky s nizkou hodnotou, co znamena menej prisne pravidla obstaravania. Pre stavebne prace je limit zakazky s nizkou hodnotou 180 000 EUR (od roku 2024).

**Suma 467 641 EUR vyrazne prekracuje limit S110 pre zakazky s nizkou hodnotou.** Toto vyzaduje dalsie overenie -- bud ide o chybne oznacenie, alebo o obidenie limitov.

### 4.6 Zmluva so Skalitym -- EU financovanie

Zmluva na doplnkovu budovu pri ZpS Goral v Skalitom (266 657 EUR) je financovana z **programu Polsko-Slovensko** (EU). Nasledny dodatok (12075436) upravuje poziadavky na **recyklovane materialy** v sulade s **Planom obnovy**.

Toto je relevantne, pretoze EU-financovane projekty podliehaju prisnejsiemu dohladua mikro firma s poradenskou registraciou by mala mat problemy splnit kvalifikacne podmienky pre stavebne prace.

### 4.7 Zmluva s Mestom Zilina -- chybajuci povodny kontrakt

Dodatok c. 1 k zmluve o dielo 802/2025 (351,99 EUR) sa odkazuje na povodnu zmluvu o diele na "ciastocnu debarierizaciu budovy ZS Jarna v Ziline". **Povodna zmluva sa vsak v databaze nenachadza.** Bud bola uzavreta pred sledovanym obdobim, alebo este nebola zverejnena.

Dodatok podpisuje primator **Mgr. Peter Fiabane**, ktory podla zlte stopy "zdielany podpisujuci" figuruje ako signatarka za 24 roznych dodavatelov -- to je vsak ocakavane pre primarora.

### 4.8 Zmluva so Starou Bystricou -- bez ICO a bez sumy

Kupna zmluva (12059873) s Obcou Stara Bystrica bola zverejnena **bez ICO dodavatela** a **bez sumy**. Firma je identifikovana len podla nazvu "YEMANITY s.r.o." Toto je neobvykle -- pri standardnych zmluvach sa ICO uvadza vzdy.

### 4.9 Osobne prepojenia -- Filip Sobol

Filip Sobol je jednym z konatelov YEMANITY (podpisoval dodatok 12058696). V databaze sme nasli aj **osobnu zmluvu** Sobola Jana (ID 11866536) -- kupna zmluva s Obcou Rovinka za 71 820 EUR, podpisana 19.01.2026. Nie je potvrdene, ci ide o tu istu osobu alebo pribuzneho.

### 4.10 Casova os -- rychly rast

| Datum | Udalost |
|---|---|
| 16.11.2022 | Vznik spolocnosti |
| 16.01.2026 | 1. zmluva -- posilnovna EUBA (467 641 EUR) |
| 25.02.2026 | 2. zmluva -- ZpS Goral Skalite (266 657 EUR) |
| 27.02.2026 | 3. zmluva -- dodatok ZS Jarna Zilina (351 EUR) |
| 03.03.2026 | 4. zmluva -- kupna zmluva Stara Bystrica (0 EUR) |
| 04.03.2026 | 5. zmluva -- dodatok Skalite (0 EUR) |
| 10.03.2026 | 6. zmluva -- bezpecnost EUBA (157 610 EUR) |

Firma bola 3 roky neaktivna (alebo mala len minimalnu cinnost mimo CRZ) a naraz ziskala zakazky za takmer 900 000 EUR v priebehu 54 dni.

---

## 5. Kontrola v registroch

| Register | Vysledok |
|---|---|
| **Danova spolahlivost (FS)** | Spolahlivy |
| **RUZ** | Evidovana, 1 zamestnanec, NACE 70220 |
| **VSZP dlznici** | Nie je dlznikom |
| **Socialna poistovna** | Nie je dlznikom |
| **Danovi dlznici FS** | Nie je dlznikom |
| **DPH deregistracia** | Nie je deregistrovana |
| **Vlastne imanie (ruz_equity)** | Ziadne udaje |
| **Financie (supplier_financials)** | Ziadne udaje |
| **Korporatna dan (fs_corporate_tax)** | Ziadne udaje |

Firma nema negativne zaznamy v ziadnom z kontrolovanych registrov. Absencia financnych udajov vsak znamena, ze nie je mozne overit ekonomicku kapacitu na realizaciu zakaziek tohto rozsahu.

---

## 6. Hodnotenie rizik

### Vysoke riziko
1. **Systematicky NACE nesulad** -- poradenska firma realizuje vylucne stavebne zakazky (4 z 4 relevantnych zmluv)
2. **Mikro firma s extremnym objemom** -- 892 261 EUR na 1 zamestnanca za 54 dni
3. **Absencia UVO linku** pre zmluvu za 157 610 EUR v ramci vacsieho projektu (542 601 EUR celkom)
4. **Mozne obidenie S110 limitu** -- posilnovna za 467 641 EUR oznacena ako S110 zakazka

### Stredne riziko
5. **Geograficka koncentracia** -- 2 z 4 objednavatelov su susedne obce sidla firmy
6. **Opakujuci sa objednavatel** -- Ekonomicka univerzita zadala 2 zakazky za 625 252 EUR
7. **Chybajuci povodny kontrakt** -- dodatok k zmluve 802/2025 bez povodnej zmluvy v databaze
8. **Zmluva bez ICO a sumy** -- kupna zmluva so Starou Bystricou

### Nizke riziko / Informativne
9. **Ziadna zmluva nema uvedenu platnost** (5 z 5)
10. **Firma je danovo spolahlivy subjekt** -- pozitivne

---

## 7. Odporucania na dalsie overenie

1. **FinStat / ucctovne zavierky** -- overit trzby, zisk a aktiva YEMANITY za roky 2023-2025. Ak su trzby minimalne, potvrdzuje to profil "spacej firmy".
2. **RPVS** -- zistit konecnych uzivatelov vyhod. Kto skutocne stoji za firmou?
3. **FOAF.sk** -- zmapovat korporatnu siet konatelov Jana Sutiaka a Filipa Sobola. Existuju prepojenia na ine stavebne firmy?
4. **UVO** -- overit obstaravanie na posilnovnu (544941) -- kolko ponuk bolo predlozenych? A overit, preco zmluva na bezpecnost EUBA (157 610 EUR) nema UVO link.
5. **Subdodavatelia** -- zmluvy 12036751 a 12088132 spominaju subdodavky. Kto su skutoční realizatori stavebnych prac?
6. **Zmluva 802/2025 so Zilinou** -- dohladat povodnu zmluvu a jej hodnotu.
7. **Obec Stara Bystrica** -- preverit kupnu zmluvu bez sumy a ICO.

---

## 8. Zaver

YEMANITY s.r.o. vykazuje viacero zavaznych zlte stopy, ktore v kombinacii vytvaraju podozrivy vzorec:

Poradenska mikro firma s jednym zamestnancom, zalozena v roku 2022, bez dolozenej stavebnej kapacity a bez znamych financnych vysledkov, ziskala za 54 dni stavebne zakazky v hodnote **892 261 EUR** od styroch verejnych objednavatelov. Firma s najvacsou pravdepodobnostou sluzi ako sprostredkovatel, ktory prace realizuje cez subdodavatelov. Otazkou zostava, preco verejni objednavatelia zvolia poradenskeho sprostredkovatela namiesto priameho zadania stavebnej firme, a ci obstaravacie procesy boli vedene transparentne.

Najnalehavejsie je overenie obstaravania na posilnovnu EUBA (467 641 EUR oznacenych ako S110) a chybajuceho UVO zaznamu pre stavebnu cast bezpecnostneho projektu (157 610 EUR).
