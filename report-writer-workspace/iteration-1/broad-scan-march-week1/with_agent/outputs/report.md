# CRZ Investigativna analyza: 2026-03-01 -- 2026-03-07

## Zhrnutie

Analyzovali sme 10 332 zmluv za tyzden 1.-7. marca 2026 s celkovou hodnotou 658 911 763 EUR. Identifikovali sme 2 POTVRDENE pripady sukromnych firem so zapornym vlastnym imanim, ktore ziskali stavebne zakazky v objeme 395 552 EUR. Dalsie 3 pripady su NEJASNE a vyzaduju dalsie overenie. Vylucili sme 8 falesne pozitivnych nalejov (NULL ICO grupiny, datove artefakty, standardne bankove produkty).

---

## CONFIRMED: SVS Nitra s.r.o. -- sukromna stavebna firma so zapornym vlastnym imanim ziskala zakazku za 287 558 EUR — HIGH

### Co sme nasli

| Zmluva ID | Nazov | Dodavatel | Objednatel | Suma | Datum podpisu | Datum zverejnenia |
|-----------|-------|-----------|------------|------|---------------|-------------------|
| 12064598 | Zmluva o dielo | SVS Nitra, s.r.o. (35922737) | Mesto Trencianske Teplice | 287 558,49 EUR | 2026-03-04 | 2026-03-05 |

**Financna situacia dodavatela:**
- Vlastne imanie: **-242 237 EUR**
- NACE: Vystavba obytnych a neobytnych budov
- Zalozena: 2005-02-24 (21 rokov v prevadzke)

### Preco je to podozrive

**1. Zaporne vlastne imanie**

SVS Nitra s.r.o. ma zaporne vlastne imanie -242 237 EUR, co znamena, ze firma dlhuje viac, ako co vlastni. Napriek tomu ziskala stavebnu zakazku za 287 558 EUR — co je o 45 321 EUR viac, ako je absolutna hodnota jej zadlzenia.

Stavebne zakazky si zvycajne vyzaduju financnu stabilitu, pretoze dodavatel musi predfinancovat material a mzdy. Firma so zapornym vlastnym imanim nema kapacitu na toto predfinancovanie.

**Pomer: hodnota zakazky je 1,19x absolutna hodnota zaporneho imania**

**2. Chybajuca evidencia v statnych registroch**

Firma nie je evidovana v registroch VSZP (Vseobecna zdravotna poistovna) ani Socialnej poistovne. To je neobvykle pre stavebnу firmu, ktora by mala mat zamestnancov.

Sukromne stavebne firmy (nie rozpoctove organizacie) so zapornym imanim predstavuju vysoke riziko:
- Nemaju financne zdroje na realizaciu
- Mozu byt schrankami pre presun verejnych penazi
- Chybajuce registracie naznacuju minimalne personalne kapacity

### Zlte stopy

| Stopa | Severity | Detail |
|-------|----------|--------|
| negative_equity | danger | Vlastne imanie -242 237 EUR |

### Dokazy

| Zmluva | CRZ URL | FinStat |
|--------|---------|---------|
| 12064598 | https://www.crz.gov.sk/zmluva/12064598/ | https://finstat.sk/35922737 |

---

## CONFIRMED: HDH development s.r.o. -- sukromna firma so zapornym imanim -89 462 EUR ziskala zakazku za 107 994 EUR — HIGH

### Co sme nasli

| Zmluva ID | Nazov | Dodavatel | Objednatel | Suma | Datum podpisu | Datum zverejnenia |
|-----------|-------|-----------|------------|------|---------------|-------------------|
| 12063040 | Zmluva o poskytovani sluzieb | HDH development, s.r.o. (35912804) | Sprava NP Muranska planina | 107 994,00 EUR | 2026-03-03 | 2026-03-04 |

**Financna situacia dodavatela:**
- Vlastne imanie: **-89 462 EUR**
- NACE: Ostatne inzinierske cinnosti
- Zalozena: 2004-12-17 (21 rokov v prevadzke)

### Preco je to podozrive

**1. Zaporne vlastne imanie presiahnute hodnotou zakazky**

HDH development s.r.o. ma zaporne vlastne imanie -89 462 EUR. Zakazka za 107 994 EUR presahuje absolutnu hodnotu zaporneho imania o 18 532 EUR — firma dlhuje menej, nez kolko dostane z jednej zakazky.

**Pomer: hodnota zakazky je 1,21x absolutna hodnota zaporneho imania**

**2. Inzinierske sluzby pre statnu spravu prirody**

Objednatel je Sprava NP Muranska planina — statna organizacia spravujuca narodny park. Inzinierske cinnosti pre narodne parky zvycajne zahrnaju projektovu dokumentaciu, technicke posudky, stavebny dozor.

Firma so zapornym vlastnym imanim nema financnu stabilitu potrebnu na poskytovanie sluzieb statnym organizaciam. Toto NIE je ramcova zmluva ani dotacia — je to zmluva o poskytovani sluzieb na konkretne prace.

### Zlte stopy

| Stopa | Severity | Detail |
|-------|----------|--------|
| negative_equity | danger | Vlastne imanie -89 462 EUR |

### Dokazy

| Zmluva | CRZ URL | FinStat |
|--------|---------|---------|
| 12063040 | https://www.crz.gov.sk/zmluva/12063040/ | https://finstat.sk/35912804 |

---

## CONFIRMED: Prahovanie pod EU sutaznym limitom -- 4 stavebne zakazky tesne pod 215 000 EUR — MEDIUM

### Co sme nasli

| Zmluva ID | Nazov | Dodavatel | Objednatel | Suma | Datum podpisu |
|-----------|-------|-----------|------------|------|---------------|
| 12053309 | Zmluva o dielo | CS, s.r.o. (ICO chyba) | SUC TTSK | 214 896,13 EUR | 2026-03-01 |
| 12054420 | Zmluva o dielo | TERRATECHNIK | Podtatranska vodarenska | 213 122,54 EUR | 2026-03-02 |
| 12058250 | Dodatok k ZoD | TOPSTAV | Mesto Hurbanovo | 210 177,58 EUR | 2026-03-03 |
| 12053796 | Kupna zmluva | MAHOLZ s.r.o. | BBSK | 210 099,00 EUR | 2026-03-01 |

**EU prah pre stavebne zakazky: 215 000 EUR**

### Preco je to podozrive

**1. Systematicke vyhybanie sa EU sutaziam**

EU prah 215 000 EUR aktivuje prisne sutazne postupy podla smernic EK. Nad tymto prahom je povinne:
- Zverejnenie v TED (Tenders Electronic Daily)
- Dlhsie lehoty pre podavanie ponuk
- Prisnejsie kriteria hodnotenia

Analyzovali sme vsetky zmluvy v pasmach:
- **210-215K EUR (tesne pod prahom): 12 zmluv**
- **215-220K EUR (tesne nad prahom): 3 zmluvy**

**Pomer 4:1** naznacuje, ze objednavatelia cielene drzali ceny pod 215K, aby sa vyhli EU sutaziam.

**2. Po vyluceni nevinnych typov**

Vylucili sme:
- Dotacie a granty (nie su verejne obstaravanie)
- Bankove uvery (fixne sumy)
- Zmluvy SFRB (statny fond s vlastnymi pravidlami)

Po vyluceni ostavaju **4 stavebne zakazky** (zmluvy o dielo, dodatok k ZoD, kupna zmluva pre BBSK).

Toto NIE su ramcove zmluvy — su to konkretne stavebne prace a nakupy. Kazda je o 118 EUR az 4 901 EUR pod EU prahom.

### Zlte stopy

| Stopa | Severity | Detail |
|-------|----------|--------|
| threshold_gaming | warning | 12 zmluv tesne pod (210-215K) vs 3 tesne nad (215-220K), pomer 4:1 |

### Dokazy

| Zmluva | CRZ URL | Dodavatel |
|--------|---------|-----------|
| 12053309 | https://www.crz.gov.sk/zmluva/12053309/ | CS, s.r.o. (ICO chyba) |
| 12054420 | https://www.crz.gov.sk/zmluva/12054420/ | TERRATECHNIK |
| 12058250 | https://www.crz.gov.sk/zmluva/12058250/ | TOPSTAV |
| 12053796 | https://www.crz.gov.sk/zmluva/12053796/ | MAHOLZ s.r.o. |

---

## INCONCLUSIVE: CS, s.r.o. -- bez ICO, stavebna zakazka 214 896 EUR tesne pod EU prahom

### Co nevieme

CS, s.r.o. nema ICO v systeme CRZ pri zmluve 12053309. Suma zakazky je 214 896,13 EUR — len **118 EUR pod EU prahom 215 000 EUR**.

Bez ICO nemozeme:
- Overit financnu stabilitu na FinStat
- Skontrolovat vlastnicku strukturu v ORSR
- Mapovat sietove prepojenia s objednatelom SUC TTSK

### Dalsie kroky

1. **Manualne vyhladanie na FinStat/ORSR** — vyhliadat firmu podla nazvu "CS, s.r.o." (moze existovat viac firiem s tymto nazvom)
2. **PDF zmluvy z CRZ** — skontrolovat original zmluvy 12053309, hladat ICO v tele dokumentu
3. **Overenie u objednatela SUC TTSK** — ziada o doplnenie ICO dodavatela

---

## INCONCLUSIVE: OptiStav s.r.o. -- zmluva za 370 394 EUR s 5 skrytymi entitami

### Co nevieme

Zmluva 12059258 (Zmluva o dielo c. Z26) obsahuje **5 skrytych entit** v texte zmluvy — neobvykle vysok pocet. Typicka zmluva o dielo ma 0-2 skryte entity (subdodavatelia, zarucitelia).

Bez dalsich dat nevieme:
- Kto su tieto skryte entity (nazvy, ICO)
- Aku rolu maju v zmluve (subdodavatelia, konsorcialni partneri, zarucitelia)
- Ci su prepojene s OptiStav s.r.o. alebo objednatelom

### Dalsie kroky

1. **Prezriet extraction_json** — extrahovat nazvy a ICO skrytych entit z textu zmluvy
2. **FinStat overenie** — skontrolovat financne profily vsetkych 5 entit
3. **foaf.sk sietove mapovanie** — overit vzajomne prepojenia medzi OptiStav a 5 entitami (spolocni majitelia, spolocni konatelia, preklady adries)

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | NULL ICO zgrupovania (2 275 freelancerov) | Datovy artefakt -- rozne mena zgrupenych pod NULL ICO |
| 2 | Vikendove zverejnenie 1.3.2026 (35 zmluv) | Automatizovany upload, nizky pocet zmluv |
| 3 | Neskor zverejnena zmluva (666K dni) | Datovy artefakt -- chybny datum podpisu 0202-02-19 |
| 4 | Okruhle sumy (nasobky 100K) | Bankove uvery, dotacie, ramcove zmluvy |
| 5 | Supplier advantage penalties | Uvery a NFP zmluvy -- standardny pokutovy rezim |
| 6 | Bezodplatne zmluvy | Kolektivne zmluvy, energie, NFP zmluvy |
| 7 | ZS Eliasa Laniho zaporne imanie | Rozpoctova organizacia -- bezne pre skolske zariadenia |
| 8 | Dvojiti dlznici | Zmluvy su 'Uznanie dlhu' -- nie verejne zakazky |

---

## Odporucania na dalsie preverenie

1. **SVS Nitra s.r.o. (35922737)** — overit ORSR zaznam (konatelia, majitelia, platnost registracie), skontrolovat UVO zakazkove postupy, mapovat foaf.sk siet (ci su prepojenia s Mestom Trencianske Teplice)

2. **HDH development s.r.o. (35912804)** — overit RPVS skutocnych majitelov, skontrolovat historiu zakaziek pre Spravu NP Muranska planina, analyzovat, ci su ine firmy so zapornym imanim v portfolio Spravy NP

3. **CS, s.r.o. (bez ICO)** — ziada o doplnenie ICO od SUC TTSK, stiahnut PDF zmluvy 12053309, overit, ci existuju dalsie zmluvy bez ICO v marci 2026

4. **Threshold gaming (215K EUR)** — analyzovat historicke trendy (2025 vs 2026), identifikovat objednatelov s opakovanym vzorcom, skontrolovat, ci su dodaci rozdeleni na viacere mensie zmluvy (splitting)

5. **OptiStav s.r.o. (12059258)** — extrahovat skryte entity, mapovat sietove prepojenia, overit, ci je to konzorcium alebo ret'az subdodavatelov

---

> *Tieto najdy su stopy, nie verdikty. Kazdy nalez si vyzaduje dalsie overenie.*

> *Dakujeme Zltej Stope*
