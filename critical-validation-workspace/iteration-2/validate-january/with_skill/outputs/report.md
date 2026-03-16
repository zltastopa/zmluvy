# Kriticka validacia: januar 2026

## Sumar validacie
- Pocet najdov na vstupe: 7
- CONFIRMED: 2
- DISMISSED: 4
- INCONCLUSIVE: 1

---

## CONFIRMED najdy

### 1. Ejoin s.r.o. (ICO 51900921) -- trojity dlznik, zmluvy s mestami -- DANGER

**Povodny najd:** Ejoin s.r.o. je dvojity dlznik VSZP + SocPoist, zmluva 97K EUR.

**Validacne kroky:**
1. Batch register lookup pre ICO 51900921 cez VSZP, SocPoist a FS databazy
2. Kontrola vsetkych zmluv dodavatela v CRZ
3. Kontrola v RUZ -- firma zalozena 2018-08-21, s.r.o.

**Vysledky registrov:**
- VSZP dlznik: 7 237,96 EUR (cin=51900921)
- Socialna poistovna dlznik: 37 378,36 EUR (zverejnene 2026-02-23)
- Financna sprava danovy dlznik: 6 626,36 EUR
- RUZ equity: ziadny zaznam (nema ulozenu uctovnu zavierku)
- DPH deregistracia: nie

**Zmluvy v CRZ:**
| ID | Objednavatel | Suma | Nazov |
|---|---|---|---|
| 12001689 | Mesto Nove Mesto nad Vahom | 87 369,18 EUR | Zmluva o dielo c. 1/2026/OV |
| 11874721 | Mesto Sabinov | 97 217,95 EUR | Zmluva o vystavbe a prevadzkovani nabijacej infrastruktury |
| 11971207 | Mesto Sabinov | 0,00 EUR | Dodatok c. 1 |
| 9170286 | Presovsky samospravny kraj | 66 657,60 EUR | Zmluva o dielo |

**Preco to nie je falesny pozitiv:**
- Ejoin je TROJITY dlznik -- dlzi vsetkym trom registrom (VSZP, SocPoist, FS), spolu 51 242,68 EUR
- Firma je sukromna s.r.o., nie statna organizacia -- dlznicky status je relevantny
- Nema ulozenu uctovnu zavierku v RUZ, co znaci netransparentnost
- Aktivne ziskava zakazky od miest (Sabinov, Nove Mesto nad Vahom, Presovsky VUC) napriek dlhom

**Klucove cisla:** ICO 51900921, dlhy VSZP 7 238 EUR + SocPoist 37 378 EUR + FS 6 626 EUR, zmluvy spolu cca 251K EUR

---

### 2. SMART CORPORATION s.r.o. -- 9,25M EUR bez ICO na nahradne diely -- WARNING

**Povodny najd:** SMART CORPORATION s.r.o. ma zmluvu za 9,25M EUR bez ICO na nahradne diely zeleznicnych vozidiel.

**Validacne kroky:**
1. Vyhladanie zmluvy v CRZ -- potvrdena: ID 11827594, objednavatel Zeleznicna spolocnost Slovensko, a.s.
2. Kontrola dodavatel_ico -- prazdne pole (empty string)
3. Vyhladanie v RUZ: SMART CORPORATION, s. r. o. existuje pod ICO 45552584

**Vysledky:**
- Zmluva: Kupna zmluva c. 4600008608/VS/2025 na dodanie nahradnych dielov zeleznicnych kolajovych vozidiel EPJ 561 (KISS)
- Suma: 9 246 530,00 EUR
- Dodavatel_ico v CRZ: prazdne
- Skutocne ICO v RUZ: 45552584

**Preco to nie je falesny pozitiv:**
- SMART CORPORATION je slovenska s.r.o. (nie zahranicny subjekt) -- musi mat ICO v zmluve
- Firma existuje v RUZ pod ICO 45552584, takze chybajuce ICO nie je dovod zahranicneho posobenia
- Bez ICO nemozno automaticky skontrolovat danove dlhy, VSZP/SocPoist dlhy, ani vlastne imanie
- Suma 9,25M EUR je vysoka na to, aby bola bez riadnej identifikacie dodavatela
- Ide o specificky tovar (nahradne diely KISS vlakov) s obmedzenym trhom -- riziko monopolneho dodavatela

**Klucove cisla:** zmluva ID 11827594, suma 9 246 530 EUR, chybajuce ICO (skutocne ICO 45552584), objednavatel ZSSK

---

## INCONCLUSIVE najdy

### 3. Vikendove zverejnenie 31.1.2026 (sobota) -- Slovak Telekom 22,7M, Alanata 14,8M

**Co sme overili:**
1. Potvrdene: 31.1.2026 je sobota, zverejnenych 158 zmluv s celkovym objemom 44,7M EUR
2. 4 zmluvy nad 1M EUR: Slovak Telekom 22,7M (Financne riaditelstvo SR), Alanata 14,8M (Min. dopravy), Orange 3,9M (MPSVR), STRABAG 1,6M (MPSVR)
3. V januari 2026 bolo na vikendy zverejnenych 656 zmluv (373 sobota + 283 nedela) z celkovych 49 953
4. Alanata a.s. -- zalozena 2022-06-02, NACE: Poradenstvi tykajuce sa pocitacov, pomerne mlada firma
5. Slovak Telekom -- velky telekomunikacny operator, zmluva na "pozarucny servis a sluzby HW a SW podpory centralnej IT infrastruktury financnej spravy"

**Preco to zostava nejasne:**
- Vikendove zverejnenie 158 zmluv naznacuje automaticky batch system CRZ, nie manualny upload
- Slovak Telekom zmluva (22,7M) je IT servis pre Financne riaditelstvo -- moze byt legitimna, ale vysoka suma vyzaduje kontrolu UVO sutaze
- Alanata a.s. je relativne mlada firma (2022) s velkou zmluvou 14,8M pre Min. dopravy -- "Zmluva o poskytovani sluzieb" je velmi vseobecny nazov
- Samotne vikendove zverejnenie je pravdepodobne technicky artefakt (automaticky system), nie pokus o skryvanie

**Dalsie kroky:**
- FinStat enrichment pre Alanata (ICO 54629331) -- overit obrat, pocet zamestnancov, ci firma velka dost na 14,8M kontrakt
- UVO procurement lookup -- overit sutaz pre obe zmluvy (Slovak Telekom aj Alanata)
- RPVS lookup pre Alanata -- overit konecnych uzivatelov vyhod
- foaf.sk pre Alanata -- mapovat siet prepojenych osob

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | Sulc Matej -- 659 zmluv so STVR za 747K EUR | **Datovy artefakt (NULL ICO zlucovanie).** STVR (Slovenska televizia a rozhlas) ma 2 372 roznych freelancerov bez ICO s celkovym poctom 3 618 zmluv. Samotny Sulc Matej ma v CRZ iba 1 zmluvu so STVR. Celkovo vsetci "Sulc" maju 8 zmluv za 30 754 EUR. Typicky broadcaster freelancer pattern -- najvacsi freelancer ma len 18 zmluv. Povodny najd 659 zmluv bol artefaktom zlucenia vsetkych dodavatelov bez ICO. |
| 2 | Fond na podporu sportu -- 60 000 000 EUR okruhla suma | **Standardna statna alokacia.** Fond na podporu sportu je statny fond so zakonnym rozpoctom. Okruhle sumy su standardne pre statutarne rozpoctove prevody. Odpoveda patternu "State fund annual allocations (Fond na podporu sportu)" -- nevyzaduje dalsi dopyt. |
| 3 | UK Bratislava -- 206,5M EUR dotacia od Ministerstva skolstva | **Standardna ministerska dotacia pre univerzitu.** Odpoveda patternu "Ministry -> university dotacie -- Normal annual budget allocations, not procurement." Ministerstvo skolstva rocne prideluje rozpoctove prostriedky univerzitam, co je bezny mechanizmus statneho financovania vysokeho skolstva. |
| 4 | Operacne stredisko ZZS SR -- 30,8M EUR, zaporne vlastne imanie -2,65M | **Statna prispevkova organizacia.** Operacne stredisko zachrannej zdravotnej sluzby SR je statna prispevkova organizacia (zachranka). Odpoveda patternu "State org negative equity -- Hospitals, rescue services, prispevkove organizacie often have negative equity by design." Zaporne vlastne imanie je bezne pre statne zdravotnicke zariadenia, ktore su financovane zo statneho rozpoctu. |

---

**Validacia ukoncena.** 2 najdy potvrdene, 4 vylucene, 1 vyzaduje dalsie overenie.

Potvrdene zlte stopy:
- **Ejoin s.r.o.** -- trojity dlznik (VSZP + SocPoist + FS) aktivne ziskavajuci verejne zakazky
- **SMART CORPORATION s.r.o.** -- chybajuce ICO pri 9,25M EUR zmluve, hoci firma existuje v registri

Tieto najdy su stopy, nie verdikty. Odporucame dalsie overenie cez FinStat, UVO a RPVS.
