# Validacny report — januar 2026

Datum validacie: 2026-03-16
Datovy zdroj: Datasette (zmluvy.zltastopa.sk/data/crz), lokalna crz.db ako fallback

> Upozornenie: Tieto zistenia su stopy, nie verdikty.

---

## Suhrn klasifikacie

| # | Nalez | Verdikt | Zavaznost |
|---|-------|---------|-----------|
| 1 | Vikendove zverejnenie 31.1. — Slovak Telekom 22.7M, Alanata 14.8M | **CONFIRMED** | Stredna |
| 2 | Ejoin s.r.o. — dvojity dlznik, zmluva 97K | **CONFIRMED** | Vysoka |
| 3 | Sulc Matej — 659 zmluv so STVR za 747K | **DISMISSED** | N/A |
| 4 | Fond na podporu sportu — 60M okruhla suma | **INCONCLUSIVE** | Nizka |
| 5 | UK Bratislava — 206.5M dotacia od Min. skolstva | **INCONCLUSIVE** | Nizka |
| 6 | SMART CORPORATION — 9.25M bez ICO | **CONFIRMED** | Vysoka |
| 7 | Operacne stredisko ZZS SR — 30.8M, zaporne vlastne imanie | **CONFIRMED** | Stredna |

**Skore: 4 CONFIRMED, 2 INCONCLUSIVE, 1 DISMISSED**

---

## Detailna validacia

### 1. Vikendove zverejnenie 31.1.2026 (sobota) — Slovak Telekom 22.7M, Alanata 14.8M EUR

**Verdikt: CONFIRMED**

**Overene fakty:**
- Datum 31.1.2026 je skutocne **sobota** (potvrdene cez Python `datetime` aj SQLite `strftime('%w')` = 6).
- V ten den bolo na CRZ zverejnenych **158 zmluv** v celkovej hodnote **44 725 337 EUR**.
- Dve najvacsie zmluvy:
  - **ID 11926779** — Slovak Telekom, a.s. (ICO 35763469): **22 745 437,37 EUR** — pozarucny servis IT infrastruktury financnej spravy, rezort MF SR. Zverejnene 31.1.2026 o 14:26. Podpisane v piatok 30.1.2026.
  - **ID 11926714** — Alanata a.s. (ICO 54629331): **14 833 000,50 EUR** — zmluva o poskytovani sluzieb, rezort MDV SR. Zverejnene 31.1.2026 o 9:57. Podpisane v stredu 28.1.2026.
- Zlte stopy pre Slovak Telekom: `amount_outlier` (6.4x stddev pre software_it), `signatory_overlap` (Mgr. Jozef Kiss podpisuje za 25 dodavatelov).
- Zlte stopy pre Alanata: `amount_outlier` (4.1x stddev pre software_it), `signatory_overlap`, `missing_expiry`.

**Kontextova analyza:**
- Obe zmluvy boli podpisane pocas pracovneho tyzdna, ale zverejnene v sobotu. CRZ system technicky umoznuje zverejnenie kedykolvek.
- Vikendove zverejnenie velkych zmluv znizuje medialnu a verejnu pozornost. Samo o sebe nie je protizakonne, ale kombinacia vysokych sum a vikendu je nezvycajna.
- Odporuca sa overit transparentnost verejneho obstaravania pre obe zakazky.

---

### 2. Ejoin s.r.o. (ICO 51900921) — dvojity dlznik VSZP + SocPoist, zmluva 97K EUR

**Verdikt: CONFIRMED**

**Overene fakty:**
- Zmluva **ID 11874721**: „zmluva o vystavbe a prevadzkovani nabijacej infrastruktury v meste Sabinov", objednavatel Mesto Sabinov, suma **97 217,95 EUR**, zverejnena 20.1.2026.
- Dlznicky status potvrdeny v troch registroch:
  - **VSZP**: 1 zaznam (flag `vszp_debtor`)
  - **Socialna poistovna**: dlh **37 378,36 EUR** (flag `socpoist_debtor`)
  - **Financna sprava**: danovy dlznik, dlh **6 626,36 EUR** (flag `fs_tax_debtor`)
  - **Danova nespolahlivost**: flag `tax_unreliable`
- Dalsie zlte stopy:
  - `nace_mismatch` — NACE 27120 (vyroba elektrickych distribucnych zariadeni) vs. zmluva na stavebne prace (construction_renovation)
  - `signatory_overlap` — Michal Vasek podpisuje za 6 roznych dodavatelov
  - `missing_expiry` — neuvedena platnost zmluvy
- Celkovo **7 zlych stop** na jednej zmluve.

**Hodnotenie:** Nalez je **zavaznejsi nez povodne uvedeny** — Ejoin je trojity dlznik (VSZP + SocPoist + FS), nie iba dvojity. Celkovy dlh voci statnym instutuciam: cca **51 000 EUR**. Mesto Sabinov uzavrelo zmluvu s danovo nespolahlivou firmou.

---

### 3. Sulc Matej — 659 zmluv so STVR za 747K EUR, potencialne delenie zakazky

**Verdikt: DISMISSED**

**Overene fakty:**
- V celej databaze existuje iba **1 zmluva** dodavatela "Sulc Matej" (resp. "Šulc Matej") s objednavatelom "Slovenska televizia a rozhlas", v sume **24 000 EUR**.
- Sirsie vyhladavanie vsetkych variant mena (Sulc, Šulc, s/bez diakritiky) potvrdzuje celkovo iba **1 zmluvu**.
- STVR ma celkovo **2 460 zmluv** v databaze. Ziadny dodavatel nema viac ako 17 zmluv (najvyssie: Semjan Stefan, 17 zmluv za 2 017 EUR).
- Cisla **659 zmluv** a **747K EUR sa nedaju reprodukovat** z dat v databaze.

**Hodnotenie:** Falozny pozitiv. Pravdepodobne chybna agregacia alebo halucinacia AI modelu v povodnej analyze. Delenie zakazky nie je relevantne pri jednej zmluve za 24K EUR.

---

### 4. Fond na podporu sportu — 60 000 000 EUR okruhla suma

**Verdikt: INCONCLUSIVE**

**Overene fakty:**
- Zmluva **ID 11967251**: „Zmluva o poskytnuti prispevku na rok 2026", dodavatel: Ministerstvo cestovneho ruchu a sportu SR (ICO 55930611), objednavatel: Fond na podporu sportu, suma presne **60 000 000,00 EUR**, zverejnena 9.2.2026.
- Jediny flag: `missing_expiry` (neuvedena platnost).

**Kontextova analyza:**
- Ide o **rocny statny prispevok** ministerstva pre Fond na podporu sportu. Fond je zakonom zriadena institucia (zakon c. 310/2019 Z.z.).
- Okruhla suma 60M EUR je typicka pre rozpoctove transfery — suma sa odvija od schvaleneho statneho rozpoctu.
- **Nevinne vysvetlenie**: Rozpoctove prispevky sa bezne stanovuju na okruhle sumy.
- **Podozrive**: Absencia platnosti zmluvy a nedostatocna transparentnost rozdelenia prostriedkov.

**Hodnotenie:** Okruhla suma je pri statnych transferoch normalny jav. Riziko nizke, ale chybajuca platnost a transparentnost rozdelenia si zasluzia pozornost.

---

### 5. UK Bratislava — 206.5M EUR dotacia od Ministerstva skolstva

**Verdikt: INCONCLUSIVE**

**Overene fakty:**
- Zmluva **ID 11902705**: „Zmluva o poskytnuti dotacie na rok 2026", dodavatel: Univerzita Komenskeho v Bratislave (ICO 00397865), objednavatel: Ministerstvo skolstva, vyskumu, vyvoja a mladeze SR, suma **206 524 376,98 EUR**, zverejnena 27.1.2026.
- Zlte stopy: `amount_outlier` (24.9x stddev pre grant_subsidy), `not_in_ruz`, `signatory_overlap` (Tomas Drucker za 22 dodavatelov), `missing_expiry`.
- V databaze neexistuje porovnatelna historicka dotacia nad 50M EUR pre UK BA.

**Kontextova analyza:**
- **Nevinne vysvetlenie**: UK BA je najvacsia slovenska univerzita (~22 000 studentov). Rocne dotacie pre velke univerzity bezne dosahuju stovky milionov EUR (platy, prevadzka, vyskum). Suma 206.5M nie je okruhla — naznacuje detailny vypocet podla normativov.
- Flag `not_in_ruz` je ocakavany — univerzity nie su obchodne spolocnosti registrovane v RUZ.
- Flag `amount_outlier` 24.9x je vysoky, ale kategoria `grant_subsidy` ma nizky priemer kvoli mnozstvu malych grantov.

**Hodnotenie:** S vysokou pravdepodobnostou legitimny rozpoctovy transfer. Extremna vyska flagu amount_outlier je artefakt porovnavania s kategoriou, kde prevazuju male granty. Absencia historickych dat v databaze vsak znemoznuje potvrdenie trendu.

---

### 6. SMART CORPORATION s.r.o. — 9.25M EUR bez ICO na nahradne diely

**Verdikt: CONFIRMED**

**Overene fakty:**
- Zmluva **ID 11827594**: „Kupna zmluva c. 4600008608/VS/2025 na dodanie nahradnych dielov zeleznicnych kolajovych vozidiel EPJ 561 (KISS)", dodavatel: SMART CORPORATION, s.r.o., ICO: **prazdne**, objednavatel: Zeleznicna spolocnost Slovensko, a.s., suma **9 246 530,00 EUR**, zverejnena 8.1.2026.
- Zlte stopy:
  - `missing_ico` — dodavatel bez ICO
  - `amount_outlier` — 9.25M EUR je 3.0x stddev pre procurement_purchase (priemer 163 598 EUR)
- V celej databaze existuje len **1 zmluva** pre SMART CORPORATION.

**Kontextova analyza:**
- Zmluva za takmer **9.25M EUR bez uvedenia ICO dodavatela** je zavazny nedostatok transparentnosti. Bez ICO nie je mozne:
  - Overit existenciu firmy v Obchodnom registri
  - Skontrolovat danovu spolahlivost a dlznicky status
  - Preverit vlastnicku strukturu a konecnych uzivatelov vyhod
  - Overit NACE kod a odvetvie
- EPJ 561 (KISS) su elektricke jednotky od Stadler Rail — nahradne diely su vysoko specializovane. Treba overit, ci SMART CORPORATION je autorizovany dealer alebo prostredník.

**Hodnotenie:** Najzavaznejsi nalez v tejto analyze. Zmluva za 9.25M EUR s dodavatelom bez ICO, bez moznosti akejkolvek kontroly. Odporuca sa urgentne zistit ICO, overit existenciu firmy a transparentnost obstaravania.

---

### 7. Operacne stredisko ZZS SR — 30.8M EUR, zaporne vlastne imanie -2.65M EUR

**Verdikt: CONFIRMED**

**Overene fakty:**
- Zmluva **ID 11875441**: „KONTRAKT uzatvoreny medzi MZ SR a OSZZS SR na rok 2026", dodavatel: Ministerstvo zdravotnictva SR (ICO 00165565), objednavatel: Operacne stredisko ZZS SR (ICO 36076643), suma **30 773 241,00 EUR**, zverejnena 20.1.2026.
- Jediny flag: `not_in_ruz` (dodavatel = ministerstvo, nie je v RUZ — ocakavane).
- **Zaporne vlastne imanie potvrdene** z tabulky `ruz_equity`:
  - ICO 36076643: vlastne imanie **-2 654 296,48 EUR**

**Kontextova analyza:**
- OS ZZS SR je statna prispevkova organizacia zodpovedna za riadenie zachrannej zdravotnej sluzby. Rocny kontrakt s MZ SR je standardny mechanizmus financovania.
- Zaporne vlastne imanie (-2.65M EUR) znamena, ze zavazky prevysuju majetok organizacie.
- U statnych organizacii zaporne VI neznaci nutne insolvencnost (stat rucí za zavazky), ale indikuje systemove financne problemy.
- Flag `negative_equity` na tejto zmluve chyba — moze ist o medzeru vo flagovani, pretoze flag kontroluje dodavatela (MZ SR), nie objednavatela (OS ZZS SR).

**Hodnotenie:** Kontrakt samotny je standardny rozpoctovy transfer. Zaporne vlastne imanie prijemcu (-2.65M EUR) je potvrdeny varovny signal. Odporuca sa overit aktualny stav financneho zdravia OS ZZS a dovody zaporneho VI.

---

## Metodicke poznamky

1. **Datasette API** pouzite ako primarny zdroj pre vsetky dopyty (tabulky `zmluvy`, `red_flags`, `flag_rules`, `vszp_debtors`, `socpoist_debtors`, `ruz_equity`).
2. **Lokalna crz.db** pouzita ako fallback pre nalez c. 3 (Sulc Matej), kde Datasette vracel chybu na diakritiku v URL.
3. **Den v tyzdni** (nalez c. 1) overeny cez Python `datetime` aj SQLite `strftime('%w')`.
4. **Nalez c. 3** (Sulc Matej) je jednoznacne falozny pozitiv — v databaze existuje 1 zmluva za 24K EUR, nie 659 za 747K EUR.
5. **Nalezy c. 4 a 5** (Fond na podporu sportu, UK BA) su legitimne statne transfery, kde zlte stopy su artefakty porovnavania s beznym priemerom.

## Odporucania pre dalsiu investigaciu

1. **SMART CORPORATION s.r.o.** (nalez 6): Najvyssia priorita. Zistit skutocne ICO, overit existenciu v OR SR, overit UVO zakazku pre ZSSK.
2. **Ejoin s.r.o.** (nalez 2): Informovat Mesto Sabinov o dlznickom statuse dodavatela (trojity dlznik). Overit klauzuly zmluvy o bezuhonnosti.
3. **Slovak Telekom / Alanata** (nalez 1): Overit transparentnost verejneho obstaravania. Casovanie na sobotu si zasluzi pozornost.
4. **OS ZZS SR** (nalez 7): Ziskat aktualne financne vykazy za 2024/2025, overit dovod zaporneho VI.
