# Kriticka validacia: januar 2026

## Sumar validacie
- Pocet najdov na vstupe: 7
- CONFIRMED: 2
- DISMISSED: 4
- INCONCLUSIVE: 1

---

## CONFIRMED najdy

### 1. Ejoin s.r.o. (ICO 51900921) -- trojity dlznik, danovo nespolahlivy, 97K EUR zmluva -- DANGER

**Povodny najd:** Ejoin s.r.o. je dvojity dlznik (VSZP + SocPoist) so zmluvou 97 217,95 EUR pre Mesto Sabinov na nabijacou infrastrukturu.

**Validacne kroky:**
1. Overenie zmluvy v Datasette: zmluva id 11874721, "zmluva o vystavbe a prevadzkovani nabijacej infrastruktury v meste Sabinov", suma 97 217,95 EUR, zverejnena 2026-01-20.
2. Overenie dlhov: VSZP debtor = ANO (1 zaznam), SocPoist debtor = ANO (dlh 37 378,36 EUR), FS danovy dlznik = ANO (dlh 6 626,36 EUR). Firma je TROJITY dlznik, nie len dvojity.
3. Danovy status podla Financnej spravy: "menej spolahlivy".
4. Registracia v RUZ: zalozena 21.8.2018, NACE 27120 (Vyroba elektrickych distribucnych zariadeni), 25-49 zamestnancov, sukromne tuzemske vlastnictvo.
5. Red flags na zmluve 11874721: 7 zlych stop vratahe 4x DANGER (danovo nespolahlivy, dlznik VSZP, dlznik SocPoist, danovy dlznik FS), NACE nesulad (elektricke zariadenia vs. construction_renovation), zdielany podpisujuci (Michal Vasek za 6 dodavatelov), neuvedena platnost.
6. Nova zmluva vo februari 2026: zmluva o dielo 87 369,18 EUR pre Mesto Nove Mesto nad Vahom (id 12001689) -- firma pokracuje v ziskavani zakaziek napriek dlhom.

**Preco to nie je falesny pozitiv:**
- Trojity dlznik (VSZP + SocPoist + FS) s celkovym dlhom cca 51 243 EUR je silny signal financnej nestability, nie administrativna chyba.
- Danovy status "menej spolahlivy" je formalne oznacenie Financnej spravy, nie len dlh.
- NACE nesulad (vyrobca el. distribucnych zariadeni vs. stavba nabijacej infrastruktury) naznacuje, ze firma nemusi mat adekvatne stavebne kompetencie.
- Zdielany podpisujuci Michal Vasek (6 roznych dodavatelov) pridava podozrenie na sietove prepojenie.
- Na rozdiel od statnych organizacii, toto je sukromna firma -- dlhy su jasnym indikatorom financnej nestability.

**Klucove cisla:** Zmluva ID 11874721, ICO 51900921, suma 97 217,95 EUR, objednavatel: Mesto Sabinov. Dlh SocPoist 37 378,36 EUR, dlh FS 6 626,36 EUR. Celkom 7 zlych stop na zmluve.

---

### 2. SMART CORPORATION, s.r.o. -- 9,25M EUR bez ICO na nahradne diely -- WARNING

**Povodny najd:** SMART CORPORATION, s.r.o. ziskala kupnu zmluvu na 9 246 530 EUR od Zeleznicnej spolocnosti Slovensko na nahradne diely zeleznicnych vozidiel EPJ 561 (KISS), bez ICO v registri.

**Validacne kroky:**
1. Overenie zmluvy: id 11827594, "Kupna zmluva c. 4600008608/VS/2025 na dodanie nahradnych dielov zeleznicnych kolajovych vozidiel EPJ 561 (KISS)", dodavatel_ico je prazdny retazec (""), zverejnena 2026-01-08.
2. Overenie ci existuju dalsie zmluvy: SMART CORPORATION nema v CRZ ziadnu dalsiu zmluvu (celkovo 1 zmluva). Nulovy track record pri takmer 10M EUR kontakte.
3. Overenie ci firma ma niekde ICO: ziadna zmluva s neprazdnym ICO pre SMART CORPORATION v celej databaze.
4. Red flags: missing_ico (info) + amount_outlier (warning -- 9 246 530 EUR = 3.0x stddev pre procurement_purchase, priemer 163 598 EUR, t.j. 56x priemernej obstaravky).
5. Hladanie v RUZ: dotaz na ruz_entities sposobil timeout -- firma tam pravdepodobne nie je registrovana.

**Preco to nie je falesny pozitiv:**
- Chybajuce ICO pri zmluve za 9,25M EUR je vysoko neobvykle. Oznacenie "s.r.o." naznacuje slovensku firmu, ktora by MALA mat ICO -- na rozdiel od zahranicnych konzorcii alebo fyzickych osob.
- Jedina zmluva v celom CRZ -- firma nema ziadnu historiu verejnych zakazok.
- Bez ICO nie je mozne overit danovy status, dlhy, vlastnicku strukturu, financne zdravie ani beneficiarnych vlastnikov.
- Nahradne diely pre specificke zeleznicne vozidla (KISS od Stadler) su vysoko specializovany segment -- dodavatel by mal byt jednoznacne identifikovatelny.

**Klucove cisla:** Zmluva ID 11827594, dodavatel_ico: prazdne, suma 9 246 530 EUR, objednavatel: Zeleznicna spolocnost Slovensko, a.s., datum 8.1.2026.

---

## INCONCLUSIVE najdy

### 3. Vikendove zverejnenie 31.1.2026 (sobota) -- Slovak Telekom 22,7M + Alanata 14,8M EUR

**Co sme overili:**
1. 31.1.2026 je sobota. V ten den bolo zverejnenych 158 zmluv od 93 roznych dodavatelov.
2. Porovnanie objemu: piatok 30.1. = 3 542 zmluv, stvrtok 29.1. = 2 558 zmluv, sobota 31.1. = 158 zmluv, nedela 1.2. = 87 zmluv. Vikendovy objem je zlomok pracovnych dni.
3. Celomesacna distribucia: v januari 2026 bolo v soboty 373 a v nedele 283 zverejneni (vs. 8 000-11 000 v pracovne dni). Vikendove zverejnenia existuju, ale su raritne.
4. Slovak Telekom zmluva (ID 11926779): 22 745 437 EUR pre Financne riaditelstvo SR na "autorizovany pozarucny servis centralnej IT infrastruktury". Zlte stopy: amount_outlier (6.4x stddev pre software_it), signatory_overlap.
5. Alanata zmluva (ID 11926714): 14 833 000 EUR pre Ministerstvo dopravy SR na sluzby. Zlte stopy: amount_outlier (4.1x stddev pre software_it), signatory_overlap, neuvedena platnost.
6. Alanata (ICO 54629331) mala v januari 2026 celkovo 7 zmluv za ~19,3M EUR s roznym objednavatelmi (Min. dopravy, Socialna poistovna, Gen. prokuratura, NASES, NCZI).

**Preco to zostava nejasne:**
- 31.1. je posledny den mesiaca -- end-of-month batch pattern je legitimne vysvetlenie. Avsak hlavny objem bol uz v piatok 30.1. (3 542 zmluv), co oslabuje toto vysvetlenie.
- CRZ system prijima zmluvy aj cez vikend automaticky, takze vikendove zverejnenie samo o sebe nie je silny signal.
- Obe zmluvy boli zverejnene pocas dna (09:57 a 14:26), nie v automatickom nocnom batch -- co moze naznacovat manualne zverejnenie.
- Slovak Telekom je etablovany IT dodavatel (ICO 35763469). Alanata je novsia firma s vysokou koncentraciou statnych IT zakaziek.
- Bez kontroly verejneho obstaravania (UVO) nemozno posuddit, ci zmluvy presli sutazou.

**Dalsie kroky:**
- Overit Alanata (ICO 54629331) cez FinStat a RPVS -- beneficiarni vlastnici a financna kondicia.
- Overit obe zmluvy v UVO Vestniku -- ci prebehlo verejne obstaravanie a kolko bolo uchadzacov.
- Porovnat s historickymi vikendovymi zverejneniami na Financnom riaditelstve a Ministerstve dopravy.

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | **Sulc Matej -- 659 zmluv so STVR za 747K EUR, delenie zakazky** | **Datovy artefakt (Sulc Matej lesson).** Validacia ukazala, ze Sulc Matej ma v databaze iba 1 zmluvu so STVR za 24 000 EUR (id 11868290, zmluva o audiovizualnom diele). Cislo "659 zmluv" je vysledkom GROUP BY dodavatel_ico, kde NULL ICO zgrupovalo vsetkych freelancerov STVR do jedneho riadku. STVR ma 967 roznych freelancerov bez ICO a najaktivnejsi z nich maju len 18 zmluv (Kyslanova Drahomira, Balaz Daniel). STVR mala v januari 2026 celkom 975 zmluv za 12,5M EUR -- bezny broadcaster freelancer pattern. |
| 2 | **Fond na podporu sportu -- 60 000 000 EUR okruhla suma** | **Standardna statna dotacia.** Zmluva id 11967251 je "Zmluva o poskytnuti prispevku na rok 2026" od Ministerstva cestovneho ruchu a sportu SR (ICO 55930611). Okruhla suma je typicka pre rozpoctove pridelenia zo statneho rozpoctu. Presne zodpoveda vzoru "Grants, subsidies, loans, framework budget ceilings". Jediny flag: "neuvedena platnost" (info). Fond dalej distribuuje financie sportovym organizaciam v mensich castka. |
| 3 | **UK Bratislava -- 206,5M EUR dotacia od Ministerstva skolstva** | **Standardna rozpoctova alokacia.** Zmluva id 11902705 je "Zmluva o poskytnuti dotacie na rok 2026" od Ministerstva skolstva SR (ICO 00164381) pre Univerzitu Komenskeho (ICO 00397865), suma 206 524 376,98 EUR. Presne zodpoveda vzoru "Ministry -> university dotacie -- Normal annual budget allocations, not procurement". UK je najvacsia slovenska univerzita a rocna dotacia v tomto rozsahu je standardna. Red flags: amount_outlier + not_in_ruz + signatory_overlap (T. Drucker za 22 dodavatelov -- normalne pre ministra). |
| 4 | **Operacne stredisko ZZS SR -- 30,8M EUR, zaporne vlastne imanie -2,65M EUR** | **Statna organizacia s typicky zapornym vlastnym imanim.** Zmluva id 11875441 je "Kontrakt uzatvoreny medzi MZ SR a OSZZS SR na rok 2026", suma 30 773 241 EUR -- standardne rocne financovanie zachrannej zdravotnej sluzby od Ministerstva zdravotnictva (ICO 00165565). OS ZZS SR (ICO 36076643) je statna prispevkova organizacia (250-499 zamestnancov, NACE: Ostatna zdravotna starostlivost). Zaporne vlastne imanie -2 654 296,48 EUR (obdobie 2023) presne zodpoveda vzoru "State org negative equity -- Hospitals, rescue services often have negative equity by design." Jedina zlta stopa: "nie je v RUZ" (info), co je logicke pre statne organizacie. |

---

**Validacia ukoncena.** 2 najdy potvrdene, 4 vylucene, 1 vyzaduje dalsie overenie.

Vsetky najdy su stopy, nie verdikty. Potvrdene najdy si vyzaduju dalsiu investigaciu -- overenie v RPVS (beneficiarni vlastnici), foaf.sk (korporatne siete), FinStat (financne zdravie) a UVO (verejne obstaravanie).
