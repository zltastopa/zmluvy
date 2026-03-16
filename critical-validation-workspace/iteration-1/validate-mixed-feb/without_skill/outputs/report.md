# Validacny report -- februar 2026 najdy

Datum validacie: 2026-03-16
Zdroj dat: Datasette (zmluvy.zltastopa.sk/data/crz)

Poznamka: Toto su stopy, nie verdikty.

---

## 1. WAY INDUSTRIES a.s. (ICO 44965257) -- 145M EUR od MO SR

**Verdikt: CONFIRMED**

### Overene fakty
- **1 zmluva** (ID 12012856): Ramcova zmluva, Ministerstvo obrany SR, 145 000 000 EUR, zverejnena 2026-02-19.
- **Dlznik VSZP**: 62 094,28 EUR (zamestnavatel, stav k 2026-02-28, CIN 44965257).
- **Dlznik Socialnej poistovne**: 179 116,09 EUR (stav k 2026-02-23).
- **Danovy dlznik FS**: 320 635,53 EUR -- dodatocne zisteny dlh.

### Zlte stopy v databaze (6)
| Severity | Stopa | Detail |
|----------|-------|--------|
| danger | Dlznik Socialnej poistovne | 179 116,09 EUR |
| danger | Dlznik VSZP | 62 094,28 EUR |
| danger | Danovy dlznik FS | 320 635,53 EUR |
| warning | Neobvykle vysoka suma | 145M EUR = 48x stddev pre procurement_purchase (priemer 163 598 EUR) |
| warning | Zdielany podpisujuci | Ing. Martin Catlos, Phd. podpisuje za 17 roznych dodavatelov |
| info | Neuvedena platnost | -- |

### Hodnotenie
Vsetky tri dlznicky registry (VSZP, SocPoist, FS) potvrdene. Firma s celkovymi dlhmi 562K+ EUR dostala ramcovu zmluvu za 145M EUR od MO SR. Tri danger-level flags. Najd je plne potvrdeny datami.

---

## 2. Angel Antonio Carbonell Barrachina -- 169 zmluv s Min. skolstva za 2.9M bez ICO

**Verdikt: DISMISSED**

### Overene fakty
- V databaze existuje **1 jedina zmluva** (ID 11976224): Prikazna zmluva, Ministerstvo skolstva, vyskumu, vyvoja a mladeze SR, **18 000 EUR**, bez ICO.
- Hladanie cez LIKE '%Carbonell%' a '%Barrachina%' na oboch stranach (dodavatel, objednavatel) vracia len tento 1 zaznam.

### Hodnotenie
Tvrdenie o 169 zmluvach za 2,9M EUR **sa nezhoduje s datami**. Realne ide o 1 zmluvu za 18 000 EUR -- rozsah je o 3 rady velkosti mensi. Jedna prikazna zmluva za 18K s ministerstvom nie je anomalna. Najd je neopodstatneny.

---

## 3. PERSET a.s. (ICO 48239089) + Asset Real a.s. (ICO 36745022) -- po 32.57M EUR pre Bratislavu

**Verdikt: CONFIRMED**

### Overene fakty
- **PERSET a.s.** (ID 12047388): Zmluva o zriadeni zalozneho prava, Hlavne mesto SR Bratislava, 32 569 732 EUR, zverejnena 2026-02-27 16:50:06.
- **Asset Real a.s.** (ID 12047390): Rovnaka zmluva, rovnaky objednavatel, **presne rovnaka suma** 32 569 732 EUR, zverejnena 2026-02-27 16:50:07 (1 sekunda rozdiel).
- Obe su typu "easement_encumbrance" (zalozne pravo).
- PERSET zmluva je explicitne bezodplatna.
- Spolocna skryta entita: **MTS SVK Development 08, s.r.o.** (ICO 54583110).
- Spolocni podpisujuci: **JUDr. Robert Kovacic** (predseda) a **JUDr. Ivor Kovacic** (clen) -- podpisuju za obe firmy.
- RUZ: PERSET (NACE 68200 -- prenajom nehnutelnosti), Asset Real (NACE 82990 -- ostatne pomocne cinnosti).

### Zlte stopy v databaze (na kazdu zmluvu)
| Severity | Stopa | Detail |
|----------|-------|--------|
| warning | Neobvykle vysoka suma | 32.57M EUR = 20.2x stddev pre easement_encumbrance |
| warning | Bezodplatna zmluva | PERSET |
| warning | Skryte entity | MTS SVK Development 08, s.r.o. |
| warning | Zdielany podpisujuci | JUDr. Robert Kovacic za 3 dodavatelov |
| info | Neuvedena platnost | -- |

### Hodnotenie
Dve rozne firmy s rovnakymi podpisujucimi (Kovacicovci) a rovnakou skrytou entitou dostali identicke zmluvy za identicku sumu od Bratislavy, zverejnene v rovnakej sekunde. Pattern naznacuje koordinovanu kolateralnu strukturu v ramci developerského projektu. Najd plne potvrdeny.

---

## 4. SFINGA s.r.o. (ICO 51671824) -- zmluva za 1.29M EUR zverejnena 489 dni po podpise

**Verdikt: CONFIRMED**

### Overene fakty
- Zmluva ID 11946081: "Zmluva o dielo c. 1/2024", dodavatel SFINGA s.r.o., objednavatel PE-ES, n.o.
- **Datum podpisu**: 2024-10-04
- **Datum zverejnenia**: 2026-02-05 09:17:47
- **Oneskorenie**: 489,4 dna (16+ mesiacov) -- potvrdene julianday vypoctom
- Suma: 1 291 200 EUR

### Zlte stopy v databaze
| Severity | Stopa | Detail |
|----------|-------|--------|
| warning | Zdielany podpisujuci | PhDr. Lubica Geczyova za 3 dodavatelov |
| info | Neuvedena platnost | -- |

### Hodnotenie
Oneskorenie 489 dni je **extremne** -- zakon 211/2000 Z.z. vyzaduje zverejnenie bezodkladne (v praxi do 30 dni). Objednavatel je neziskova organizacia (PE-ES, n.o.), zmluva za 1,29M EUR. Zmluva nadobuda ucinnost az zverejnenim na CRZ, takze 16 mesiacov mohla byt pravne neucinná. Najd potvrdeny. Poznamka: samotne oneskorenie zverejnenia nie je medzi nasimi 36 stopami -- potencialny kandidat na nove pravidlo.

---

## 5. Ministerstvo dopravy SR -> SFRB -- 490M EUR jedina zmluva

**Verdikt: INCONCLUSIVE**

### Overene fakty
- Zmluva ID 11990665: "Dodatok c.2 k Zmluve o financovani c. 850/CC00/2024 zo dna 20.05.2024"
- Dodavatel: Statny fond rozvoja byvania (SFRB)
- Objednavatel: Ministerstvo dopravy SR
- Suma: 490 058 824 EUR
- Datum podpisu: 2026-02-12, zverejnena: 2026-02-13 (1 den -- korektne)
- **Typ v databaze**: "zmluva" -- ale nazov hovori "Dodatok c.2" (data quality issue)
- V databaze je to **jediny zaznam** medzi Min. dopravy a SFRB (overene, count=1)

### Zlte stopy v databaze
| Severity | Stopa | Detail |
|----------|-------|--------|
| warning | Neobvykle vysoka suma | 490M EUR = 59.1x stddev pre grant_subsidy |
| warning | Zdielany podpisujuci | Ing. Milan Lipka za 164 dodavatelov |

### Hodnotenie
Suma 490M EUR je realna a potvrdena. Zmiernujuce faktory:
- SFRB je **statna institucia** -- prevod medzi statnym fondom a ministerstvom je bezny mechanizmus financovania bytovej vystavby.
- Nazov "Dodatok c.2" naznacuje navysenie existujucej zmluvy (povodna 850/CC00/2024 z 20.05.2024 nie je v datasete).
- Lipka podpisujuci za 164 dodavatelov -- typicke pre statneho urednika spravujuceho fondy.

INCONCLUSIVE preto, ze fakticke udaje (suma, jedina zmluva) sa potvrdili, ale prevod stat->stat nie je inherentne podozrivy. Chyba kontext povodnej zmluvy a dovod navysenia.

---

## 6. Jana KEPICOVA -- 13 382 zmluv za 85.6M EUR bez ICO

**Verdikt: DISMISSED**

### Overene fakty
- V databaze **neexistuje ziaden zaznam** pod menom "Kepicova" alebo "KEPICOVA" ani "kepic" -- ani ako dodavatel, ani ako objednavatel.
- Hladanie cez `LIKE '%kepic%'` a `LIKE '%Kepic%'` na oboch stranach vracia **nula vysledkov**.

### Hodnotenie
Tvrdenie o 13 382 zmluvach za 85,6M EUR je **uplne nepodlozene datami**. Ziadna osoba s menom Kepicova sa v CRZ databaze nenachadza. Povodny najd je zjavne chybny -- bud ide o data z ineho zdroja, alebo o halucináciu analytického modelu.

---

## Suhrn

| # | Subjekt | Tvrdenie | Verdikt | Dovod |
|---|---------|----------|---------|-------|
| 1 | WAY INDUSTRIES a.s. | 145M EUR + dlhy VSZP/SocPoist | **CONFIRMED** | Vsetky parametre potvrdene, 3 danger flags |
| 2 | Angel Antonio Carbonell Barrachina | 169 zmluv za 2.9M | **DISMISSED** | Realne 1 zmluva za 18K EUR |
| 3 | PERSET + Asset Real | po 32.57M EUR, rovnake sumy | **CONFIRMED** | Identicke zmluvy, spolocni podpisujuci, rovnaka skryta entita |
| 4 | SFINGA s.r.o. | 1.29M EUR, 489-dnovy delay | **CONFIRMED** | Vsetky parametre presne potvrdene |
| 5 | Min. dopravy -> SFRB | 490M EUR jedina zmluva | **INCONCLUSIVE** | Suma potvrdena, ale stat-stat prevod moze byt legitimny |
| 6 | Jana KEPICOVA | 13 382 zmluv za 85.6M | **DISMISSED** | Nula zaznamov v databaze |

**Skore: 3 CONFIRMED, 1 INCONCLUSIVE, 2 DISMISSED**

Najzavaznejsie nalezy su #1 (WAY INDUSTRIES -- 562K EUR dlhy + megazmluva 145M), #3 (PERSET/Asset Real -- koordinovana struktura s identickymi sumami), a #4 (SFINGA -- 489-dnove oneskorenie zverejnenia). Nalezy #2 a #6 su fakticky nespravne a mali by byt z dalsej analyzy vyradene.
