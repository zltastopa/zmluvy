# Kriticka validacia: februar 2026

## Sumar validacie
- Pocet najdov na vstupe: 6
- CONFIRMED: 3
- DISMISSED: 2
- INCONCLUSIVE: 1

---

## CONFIRMED najdy

### 1. WAY INDUSTRIES a.s. (ICO 44965257) -- 145M EUR od MO SR, trojity dlznik -- DANGER

**Povodny najd:** Ramcova zmluva za 145 000 000 EUR od Ministerstva obrany SR. Dodavatel je dlznik VSZP (62 094 EUR), Socialnej poistovne (179 116 EUR) a Financnej spravy (320 636 EUR).

**Validacne kroky:**
1. Overeny kontrakt v CRZ (id 12012856): Ramcova zmluva, datum podpisu 2026-02-13, zverejnena 2026-02-19.
2. VSZP register: potvrdeny dlh 62 094,28 EUR (zamestnvatel, zverejnene 2026-02-28).
3. Red flags v databaze: `socpoist_debtor` (179 116,09 EUR), `vszp_debtor`, `fs_tax_debtor` (320 635,53 EUR), `amount_outlier` (48x stddev), `signatory_overlap` (Ing. Martin Catlos podpisuje za 17 dodavatelov).
4. RUZ: sukromna firma, Akc. spol., 150-199 zamestnancov, NACE 28920 (Vyroba banicskych strojov), zalozena 2009-09-17, sidlo Krupina.

**Preco to nie je falesny pozitiv:**
- Trojity dlznik (VSZP + SocPoist + FS) -- celkovy dlh cca 562 000 EUR -- indikuje systemove financne problemy dodavatela.
- Suma 145M EUR je 48-nasobok smerodajnej odchylky pre procurement kontrakty -- extremne vysoka aj pre obrannu zakazku.
- Zdielany podpisujuci (Catlos) za 17 roznych dodavatelov -- signalizuje potencialnu siet prepojenych firiem.
- Obrana nie je dovod na vynimku z financnej spolahlivosti dodavatela -- stat by nemal davat 145M firme, ktora neplati odvody.

**Klucove cisla:** Zmluva ID 12012856, ICO 44965257, suma 145 000 000 EUR, VSZP dlh 62 094 EUR, SocPoist dlh 179 116 EUR, FS dlh 320 636 EUR.

---

### 2. PERSET a.s. + Asset Real a.s. -- identicke sumy 32.57M EUR pre Bratislavu -- WARNING

**Povodny najd:** Dve rozne firmy (PERSET a.s., ICO 48239089 a Asset Real a.s., ICO 36745022) maju zmluvy s Hlavnym mestom SR Bratislava na uplne rovnaku sumu 32 569 732 EUR.

**Validacne kroky:**
1. Overene kontrakty: PERSET (id 12047388) a Asset Real (id 12047390) -- "Zmluva o ZP k Zmluve o spolupraci", obe s rovnakou sumou.
2. Red flags: obe zmluvy maju `amount_outlier` (20.2x stddev), `hidden_entities`, `signatory_overlap` (JUDr. Robert Kovacic podpisuje za 3 dodavatelov).
3. RUZ: PERSET a.s. -- 3-4 zamestnanci, NACE 68200 (Real estate), zalozena 2015. Asset Real a.s. -- nezisteny pocet zamestnancov, NACE 82990, zalozena 2007.
4. Ani jedna firma nema zaznam v ruz_equity (chybaju financne vykazy).
5. Obe zmluvy su typu "Zmluva o ZP" (zriadenie prava) k tej istej Zmluve o spolupraci (OKVZoSFP0001).

**Preco to nie je falesny pozitiv:**
- Identicka suma 32 569 732 EUR pre dve rozne firmy NIE je duplicitny upload (rozne ID, rozne nazvy zmluv, rozni dodavatelia).
- PERSET ma len 3-4 zamestnancov a kontrakt za 32.5M -- extremny nesulad velkosti.
- Spolocny podpisujuci (JUDr. Kovacic) za obe firmy -- naznacuje prepojenie.
- NACE kod 68200 (nehnutelnosti) a 82990 (ine podnikatelske sluzby) -- nie su stavebne firmy, ale maju zmluvy o vecnom bremene za desiatky milionov.
- Zmluvy suvisias rovnakou zmluvou o spolupraci -- moze ist o legitimne vecne bremena v ramci infrastrukturneho projektu, ale prepojenie cez podpisujuceho a identicke sumy vyzaduju dalsie preverenie.

**Klucove cisla:** Zmluvy ID 12047388 a 12047390, ICO 48239089 a 36745022, suma 2x 32 569 732 EUR, objednavatel Hlavne mesto SR Bratislava (ICO 00603481).

---

### 3. SFINGA s.r.o. -- zmluva za 1.29M EUR zverejnena 489 dni po podpise -- WARNING

**Povodny najd:** Zmluva o dielo c. 1/2024 za 1 291 200 EUR zverejnena az 489 dni po podpise (podpis 2024-10-04, zverejnenie 2026-02-05).

**Validacne kroky:**
1. Overeny kontrakt (id 11946081): Zmluva o dielo c. 1/2024, dodavatel SFINGA s.r.o. (ICO 51671824), objednavatel PE-ES, n.o.
2. Vypocet oneskorenia: julianday('2026-02-05') - julianday('2024-10-04') = 489 dni -- potvrdene.
3. RUZ: SFINGA s.r.o., NACE 41209 (Vystavba budov), nezistena velkost, zalozena 2018-05-25.
4. Toto je jedina zmluva SFINGA s.r.o. v databaze.
5. Objednavatel je neziskova organizacia (PE-ES, n.o.), nie statny organ.
6. Ziadne zaznamy v ruz_equity -- financne vykazy nedostupne.

**Preco to nie je falesny pozitiv:**
- 489 dni oneskorenia NIE je Erasmus/EU program (nazov je "Zmluva o dielo", stavebna firma).
- Zakonny limit na zverejnenie je max 3 mesiace -- 489 dni je 5.4-nasobok zakonneho limitu.
- Firma ma len jednu zmluvu v celom CRZ -- ziadna historia predchadzajucich zakazok.
- Objednavatel je neziskovka, nie statny organ -- menej transparentnosti.
- Chybajuce financne vykazy (nie je v ruz_equity) znemoznuju posudenie financneho zdravia.

**Klucove cisla:** Zmluva ID 11946081, ICO 51671824, suma 1 291 200 EUR, podpis 2024-10-04, zverejnenie 2026-02-05, oneskorenie 489 dni.

---

## INCONCLUSIVE najdy

### 4. Angel Antonio Carbonell Barrachina -- 169 zmluv s Min. skolstva za 2.9M bez ICO

**Co sme overili:**
- V databaze je len 1 zmluva na meno "Angel Antonio Carbonell Barrachina" za 18 000 EUR (id 11976224, Prikazna zmluva).
- Min. skolstva ma celkovo 314 zmluv bez ICO (4.1M EUR) s 221 roznymi dodavatelmi.
- Ostatni dodavatelia su zahranicni akademici (Archie C.A. Clements, Alberto Cuoci, Johan Hartle, Servanne Woodward, atd.) -- vsetci s prikaznymi zmluvami za 18 000 EUR.

**Preco to zostava nejasne:**
- Povodny najd uvazdal 169 zmluv za 2.9M EUR, ale data ukazuju len 1 zmluvu za 18 000 EUR. Bud sa povodna analyza tykala agregovanych dat za NULL ICO skupinu, alebo boli pouzite ine kriteria vyhladavania.
- Jeden kontrakt za 18 000 EUR pre zahranicneho akademika je uplne standardny (prikazna zmluva = consultancy/advisory). Ale povodny claim o 169 zmluvach sa nepodarilo reprodukovat.

**Dalsie kroky:** Overit povodny SQL dopyt, ktory generoval finding. Ak islo o agregovany pocet za vsetky NULL ICO entity, ide o klasicky Sulc Matej artefakt a finding by mal byt DISMISSED. Ak existuju dalsie zmluvy pod variantami mena, treba hladat v PDF prilohach.

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 5 | Ministerstvo dopravy -> SFRB -- 490M EUR jedina zmluva | **SFRB (Statny fond rozvoja byvania)** -- instant-dismiss pattern. Kontrakt (id 11990665) je "Dodatok c.2 k Zmluve o financovani c. 850/CC00/2024". Ide o standardny mechanizmus statneho financovania bytovej vystavby -- SFRB je statny fond, ktory distribuuje prostriedky na byvanie. Dodatky k financnym zmluvam medzi ministerstvom a jeho podradenym fondom su rutinna rozpoctova operacia. |
| 6 | Jana KEPICOVA -- 13 382 zmluv za 85.6M EUR bez ICO | **NULL ICO artefakt** (Sulc Matej vzor). V databaze existuje len 1 zmluva na meno "Jana KEPICOVA" za 290,80 EUR. Povodny finding 13 382 zmluv vznikol agregaciou vsetkych zmluv s prazdnym ICO do jednej skupiny. Skutocna Jana KEPICOVA nema ziadny anomalny pocet zmluv. |

---

**Validacia ukoncena.** 3 najdy potvrdene, 2 vylucene, 1 vyzaduje dalsie overenie.

*Stopy, nie verdikty -- kazdy potvrdeny najd vyzaduje dalsie preverenie cez FinStat, RPVS, foaf.sk a analyzu PDF priloh pred formulovanim zaverov.*
