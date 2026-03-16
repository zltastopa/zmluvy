# Kriticka validacia: februar 2026

## Sumar validacie
- Pocet najdov na vstupe: 6
- CONFIRMED: 3
- DISMISSED: 2
- INCONCLUSIVE: 1

---

## CONFIRMED najdy

### 1. WAY INDUSTRIES a.s. (ICO 44965257) -- 145M EUR od MO SR, trojity dlznik -- DANGER

**Povodny najd:** WAY INDUSTRIES a.s. ziskala ramcovu zmluvu za 145 000 000 EUR od Ministerstva obrany SR (zmluva ID 12012856, podpis 2026-02-13), pricom je dlznikom VSZP (62 094 EUR), Socialnej poistovne (179 116 EUR) a Financnej spravy (320 636 EUR).

**Validacne kroky:**
1. Overena existencia zmluvy v CRZ -- potvrdena. Jedina zmluva tejto firmy v databaze. Extrakcia identifikuje predmet: "Ramcova zmluva na nakup odminovacieho kompletu BOZENA pre Ministerstvo obrany SR."
2. Overene dlhy vo vsetkych troch registroch: VSZP (cin 44965257, dlh 62 094.28 EUR, status zamestnavatel), SocPoist (179 116.09 EUR), FS danovy dlznik (320 635.53 EUR). Vsetky tri dlhy potvrdene.
3. WAY INDUSTRIES v RUZ: akciova spolocnost, zalozena 2009-09-17, sidlo Krupina, NACE 28920 (vyroba banskych strojov), 150-199 zamestnancov. Danovy status: "spolahlivy" (rozpor s evidovanym dlhom na FS).
4. Skontrolovane automaticke zlte stopy: 3x DANGER (fs_tax_debtor, socpoist_debtor, vszp_debtor), 2x WARNING (amount_outlier -- 48x stddev, signatory_overlap -- Ing. Martin Catlos, Phd. podpisuje za 17 roznych dodavatelov), 1x INFO (missing_expiry).
5. Overene, ci ide o ramcovu zmluvu (stropova hodnota) -- ano, je to "Ramcova zmluva" (procurement_purchase). Suma 145M EUR je strop, nie jednorazova platba. To vsak neznizuje zavaznost trojiteho dlhu.

**Preco to nie je falesny pozitiv:**
- Firma NIE JE statna institucia -- je to sukromna akciova spolocnost. Dlhy v zdravotnom a socialnom poisteni su zavazny signal o financnej kondici.
- Celkovy dlh 561 846 EUR (VSZP + SocPoist + FS) pri zmluve za 145M EUR ukazuje, ze stat zveruje obrovsku zakazku firme, ktora si neplni zakladne odvodove povinnosti.
- NACE kod 28920 (banske stroje) nie je priamo obranna kategoria, ale WAY INDUSTRIES je znamy vyrobca odminovacieho systemu BOZENA -- to je legitimne. Nevinne vysvetlenie teda plati pre predmet zmluvy, ale NEPLATI pre trojity dlh.
- Rozpor medzi statusom "spolahlivy" v danovej spolahlivosti a evidovanym dlhom na FS si zasluzi dalsiu pozornost.
- Signatory overlap (Ing. Martin Catlos za 17 dodavatelov) je doplnkovy varovny signal.

**Klucove cisla:** Zmluva ID 12012856, ICO 44965257, suma 145 000 000 EUR, dlh VSZP 62 094 EUR, dlh SocPoist 179 116 EUR, dlh FS 320 636 EUR.

---

### 2. PERSET a.s. + Asset Real a.s. -- po 32.57M EUR pre Bratislavu, rovnake sumy -- WARNING

**Povodny najd:** Dve firmy (PERSET a.s., ICO 48239089 a Asset Real a.s., ICO 36745022) dostali od Hlavneho mesta SR Bratislava zmluvy na presne rovnaku sumu 32 569 732 EUR, zverejnene v rovnakom case (2026-02-27, 16:50:06 a 16:50:07).

**Validacne kroky:**
1. Overene obe zmluvy. Nazvy: "Zmluva o ZP k Zmluve o spolupraci c. OKVZoSFP0001 s.r.o." Kategoria: easement_encumbrance -- zmluvy o zriadeni zalozneho prava k nehnutelnostiam na zabezpecenie pohladavok zo zmluvy o spolupraci s developerom.
2. PERSET a.s. (ICO 48239089): zalozena 2015-07-25, NACE 68200 (prenajom vlastnych nehnutelnosti), 3-4 zamestnanci, sidlo Bratislava-Ruzinov. Asset Real a.s. (ICO 36745022): zalozena 2007-02-27, NACE 82990 (ostatne pomocne obchodne cinnosti), velkost "nezisteny", sidlo Bratislava-Ruzinov.
3. Zlte stopy: amount_outlier (20.2x stddev), bezodplatna zmluva (PERSET), hidden_entities v oboch, signatory_overlap (Judr. Robert Kovacic za 3 dodavatelov).
4. Skryta entita v oboch zmluvach: MTS SVK Development 08, s.r.o. (ICO 54583110).
5. Obe firmy prepojene cez signatora Judr. Roberta Kovacica.

**Preco to nie je falesny pozitiv:**
- Identicky rovnaka suma 32 569 732 EUR pre dve rozne firmy v rovnakom case je vysoko neobvykla. Aj ked zalozne pravo moze zabezpecovat tu istu pohladavku, duplikovana suma naznacuje bud zdvojene zabezpecenie alebo koordinovanu strukturu.
- PERSET je mikro firma (3-4 zamestnanci) s NACE "prenajom nehnutelnosti" -- 32.5M EUR je extremne vysoka suma pre takuto firmu.
- Asset Real ma velkost "nezisteny" -- neznamy rozsah cinnosti.
- Prepojenie oboch firiem cez spolocneho signatora (Kovacic) a spolocnu skrytu entitu (MTS SVK Development 08) naznacuje koordinovanu skupinu.
- Zmluvy su formalne "bezodplatne" (zalozne pravo, nie priama platba), ale suma 32.5M EUR vyjadruje hodnotu zabezpecovanej pohladavky -- realne financne riziko pre Bratislavu.

**Klucove cisla:** Zmluvy ID 12047388 (PERSET) a 12047390 (Asset Real), ICO 48239089 a 36745022, suma 32 569 732 EUR kazda, objednavatel: Hlavne mesto SR Bratislava, skryta entita: MTS SVK Development 08 (ICO 54583110).

---

### 3. SFINGA s.r.o. -- zmluva za 1.29M EUR zverejnena 489 dni po podpise -- DANGER

**Povodny najd:** SFINGA s.r.o. (ICO 51671824) -- zmluva o dielo c. 1/2024 za 1 291 200 EUR s PE-ES, n.o., podpisana 2024-10-04, zverejnena az 2026-02-05. Oneskorenie 489 dni.

**Validacne kroky:**
1. Overeny presny casovy rozdiel: datum_podpisu 2024-10-04, datum_zverejnenia 2026-02-05. Potvrdenych 489 dni oneskorenia. Datum podpisu je validny (po roku 2000, nie je datovy artefakt).
2. SFINGA s.r.o. v RUZ: zalozena 2018-05-25, NACE 41209 (vystavba obytnych a neobytnych budov), velkost "nezisteny" -- indikator velmi malej firmy. Sidlo Teplicka nad Vahom.
3. PE-ES, n.o. je neziskova organizacia prevadzkujuca zariadenie socialnych sluzieb (domov seniorov). Ostatne zmluvy PE-ES su s MPSVR, obcami a nadaciami na sumy v radoch stoviek az tisicov EUR. Zmluva so SFINGA za 1.29M EUR je radovo vyssia nez vsetky ostatne.
4. Extrakcia: construction_renovation -- stavebne prace na projekte "Zariadenie pre seniorov Diviacka Nova Ves".
5. Kontrola nevinnych vysvetleni: NIE JE to EU/Erasmus grant, NIE JE to dodatok k starej zmluve, NIE JE to ramcova zmluva. Je to povodna zmluva o dielo na stavbu.
6. Automaticke zlte stopy: len missing_expiry a signatory_overlap -- system nezachytil oneskorene zverejnenie ako osobitny flag.

**Preco to nie je falesny pozitiv:**
- 489-dnove oneskorenie je masivne porusenie zakonnej lehoty (zmluvy maju byt zverejnene do niekolkych pracovnych dni). Ziadna nevinne kategoria toto neospravedlnuje.
- Kombinacia mikro stavebna firma (jedina zmluva v CRZ) + mala neziskovka (domov seniorov) + 1.29M EUR + takmer 500-dnove oneskorenie = vysoko podozrive.
- PE-ES n.o. ma typicky zmluvy za stovky EUR s obcami -- 1.29M EUR stavba je radovo iny typ zakazky.
- SFINGA s.r.o. nema ziadnu inu zmluvu v CRZ -- toto je jej jedina zmluva, co zvysuje riziko.

**Klucove cisla:** Zmluva ID 11946081, ICO dodavatela 51671824, suma 1 291 200 EUR, datum podpisu 2024-10-04, datum zverejnenia 2026-02-05, oneskorenie 489 dni, objednavatel PE-ES n.o.

---

## INCONCLUSIVE najdy

### 4. Angel Antonio Carbonell Barrachina -- tvrdenych 169 zmluv s Min. skolstva za 2.9M bez ICO

**Co sme overili:**
1. V databaze existuje LEN 1 zmluva od "Angel Antonio Carbonell Barrachina": ID 11976224, prikazna zmluva za 18 000 EUR s Min. skolstva, vyskumu, vyvoja a mladeze SR, podpisana 2026-01-27, zverejnena 2026-02-11.
2. Sirsie vyhladavanie cez LIKE '%Carbonell%' aj '%Barrachina%' potvrdzuje iba tento 1 zaznam.
3. Min. skolstva ma v februari 2026 celkovo 224 zmluv so 188 roznymi dodavatelmi bez ICO za 2 908 000 EUR. Vacsina su akademici a profesori (Erasmus, vyskumne granty) s malymi sumami.
4. Celkovo ma Min. skolstva v celej DB 310 zmluv s 220 roznymi dodavatelmi bez ICO za 4 110 656 EUR.

**Preco to zostava nejasne:**
- Tvrdenych 169 zmluv za 2.9M EUR sa v databaze NEDA overit -- nasli sme len 1 zmluvu za 18 000 EUR.
- Cisla 224 zmluv a 2.9M EUR sedia pre VSETKYCH dodavatelov bez ICO pri Min. skolstva v februari -- je vysoko pravdepodobne, ze povodny najd bol vysledkom NULL-ICO agregacie (klasicka "Sulc Matej chyba"), kde vsetci dodavatelia bez ICO boli zgruopvani do jedneho riadku a chybne priradeni Carbonellovi.
- Jedna prikazna zmluva za 18 000 EUR so zahranicnym menom nie je sama o sebe podozriva -- zahranicni konzultanti a akademici bezne dodavaju ministerstvam.
- Nemozme to vsak s istotou potvrdit bez povodneho SQL dotazu.

**Dalsie kroky:** Overit povodny SQL dotaz. Pravdepodobne pouzil GROUP BY dodavatel_ico (kde NULL = vsetci bez ICO) namiesto GROUP BY dodavatel. Ak sa potvrdi NULL-ICO agregacia, preradit na DISMISSED.

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 5 | Ministerstvo dopravy -> SFRB -- 490M EUR jedina zmluva | Ide o **Dodatok c. 2 k Zmluve o financovani c. 850/CC00/2024** (ID 11990665). SFRB (Statny fond rozvoja byvania, ICO 31749542) je statna institucia zriadena zakonom na financovanie bytovej vystavby. Toto presne zodpoveda vzoru "SFRB (housing fund) contracts" zo zoznamu beznych nevinnych patternov. Velke sumy (stovky milionov EUR) su standardne -- SFRB bezne operuje s uvermi a zaloznymi zmluvami v radoch milionov. Navyse ide o dodatok k existujucej zmluve z maja 2024 (zmluva o financovani v ramci Programu Slovensko), nie o novu zakazku. Extrakcia potvrdzuje kategoriu grant_subsidy. |
| 6 | Jana KEPICOVA -- tvrdenych 13 382 zmluv za 85.6M EUR bez ICO | V databaze existuje iba **1 zmluva** od "Jana KEPICOVA" (spravne: Jana KEPICOVA) -- Dohoda o pouziti sukromneho cestneho motoroveho vozidla s MO SR za 290.80 EUR (ID 11926934). Dalsie 4 zaznamy "Kepicova" patria inej osobe (Anna Kepicova a Milan Rakosi, najomne zmluvy za 15 EUR). Tvrdenych 13 382 zmluv za 85.6M EUR je s najvyssou pravdepodobnostou **datovy artefakt NULL-ICO groupovania** -- celkovy pocet vsetkych zmluv bez ICO v DB je 31 769 za 434.5M EUR. Toto je klasicky priklad "Sulc Matej lesson": dotaz GROUP BY dodavatel_ico zoskupil tisice roznych fyzickych osob bez ICO do jedneho riadku. Najd je v nasich datach jednoznacne nereprodukovatelny. |

---

**Validacia ukoncena.** 3 najdy potvrdene, 2 vylucene, 1 vyzaduje dalsie overenie.

**Poznamka:** Vsetky uvedene stopy su stopy, nie verdikty. Potvrdene najdy indikuju anomalie hodne dalsieho preskumania, nie dokazuju nekalost.
