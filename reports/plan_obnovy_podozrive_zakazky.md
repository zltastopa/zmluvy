# Plán obnovy: 10 podozrivých zákaziek

**Dátum analýzy:** 2026-03-08
**Zdroj:** CRZ databáza (crz.db), Finančná správa SR, VŠZP zoznam dlžníkov
**Rozsah:** 424 zmlúv v celkovej hodnote ~395 mil. EUR súvisiacich s Plánom obnovy a odolnosti SR

---

## 1. SWAN, a.s. — 8 mil. EUR dotácia pre daňovo nespoľahlivý subjekt

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | SWAN, a. s. (IČO: 35680202) |
| **Suma** | 7 981 200,00 EUR |
| **Objednávateľ** | Úrad podpredsedu vlády SR pre Plán obnovy |
| **Dátum podpisu** | 18.12.2025 |
| **CRZ** | https://www.crz.gov.sk/zmluva/11775134/ |

**Prečo je to podozrivé:** SWAN a.s. je podľa Finančnej správy SR vedený ako **„menej spoľahlivý"** daňový subjekt. Napriek tomu získal z Plánu obnovy dotáciu takmer 8 mil. EUR. Je to jediný príjemca dotácie z Plánu obnovy s negatívnym hodnotením daňovej spoľahlivosti. Red flag `tax_unreliable` bol potvrdený v databáze.

**Red flags:** `tax_unreliable` (danger)

---

## 2. Duplicitné zmluvy za 60,4 mil. EUR — Ministerstvo spravodlivosti

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | Ministerstvo spravodlivosti SR (IČO: 00166073) |
| **Suma** | 60 408 004,00 EUR × 2 |
| **Objednávatelia** | Mestský súd Bratislava IV (ID 11960256) a Mestský súd Bratislava III (ID 11960259) |
| **Dátum podpisu** | 02.02.2026 |
| **CRZ** | https://www.crz.gov.sk/zmluva/11960256/ / https://www.crz.gov.sk/zmluva/11960259/ |

**Prečo je to podozrivé:** Identický Dodatok č. 3 k tej istej zmluve (MS/139/2024-186) bol zverejnený v rovnaký deň na rovnakú sumu 60,4 mil. EUR, ale pre dva rôzne súdy. Buď ide o legitímne rozdelenie tej istej zákazky (a suma je uvádzaná celková pre oba záznamy), alebo ide o **duplicitné účtovanie**. Rovnaký vzor sa opakuje aj pri ďalších zmluvách Min. spravodlivosti — Dodatok č. 2 pre OS Banská Bystrica (503 760 EUR × 2) a Dodatok č. 1 pre KS Košice (312 902,80 EUR × 2). Celkovo Min. spravodlivosti vykazuje **133,6 mil. EUR** v Pláne obnovy (vrátane IČO variantu 166073 za ďalších 7,6 mil.).

**Red flags:** Systematické duplicity, nekonzistentné IČO (00166073 vs 166073)

---

## 3. DOMOV SENIOROV Tatranská Štrba — 507-dňové oneskorenie zverejnenia

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | DOMOV SENIOROV Tatranská Štrba, n.o. (IČO: 51776359) |
| **Suma** | 2 663 013,60 EUR |
| **Objednávateľ** | Ministerstvo zdravotníctva SR |
| **Dátum podpisu** | 23.07.2024 |
| **Dátum zverejnenia** | 12.12.2025 |
| **Oneskorenie** | **507 dní** |
| **CRZ** | https://www.crz.gov.sk/zmluva/11736642/ |

**Prečo je to podozrivé:** Zmluva bola podpísaná v júli 2024, ale zverejnená až v decembri 2025 — teda takmer rok a pol po podpise. Podľa zákona o CRZ musia byť zmluvy zverejnené do 10 dní. Nezisková organizácia založená v 2018 (NACE: Starostlivosť o staršie osoby) dostala 2,66 mil. EUR na obnovu — ale prečo bola zmluva tak dlho utajovaná?

**Red flags:** Extrémne oneskorenie zverejnenia (507 dní), nezisková organizácia

---

## 4. HS Development, s.r.o. — mladá firma s 1,33 mil. EUR zákazkou

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | HS Development, s.r.o. (IČO: 55496008) |
| **Suma** | 1 334 312,00 EUR |
| **Objednávateľ** | Ministerstvo hospodárstva SR |
| **Dátum podpisu** | 12.02.2026 |
| **Založenie firmy** | 06.06.2023 |
| **Vek firmy pri podpise** | **982 dní (~2,7 roka)** |
| **CRZ** | https://www.crz.gov.sk/zmluva/11989466/ |

**Prečo je to podozrivé:** Firma z Hriňovej s predmetom podnikania **„Nešpecializovaný veľkoobchod"** (NACE 46900) získala 1,33 mil. EUR z Plánu obnovy od MH SR. Ide o jej **jedinú zmluvu** v CRZ. Firma bola založená len v roku 2023 a nemá žiadnu preukázateľnú históriu štátnych zákaziek. Veľkoobchodná firma čerpajúca z plánu obnovy vyvoláva otázku, čo presne „obnovuje".

**Red flags:** Mladá firma, jediná zmluva, nesúlad NACE s účelom dotácie

---

## 5. Cosmopo s.r.o. — turistické ubytovanie za 1,65 mil. EUR

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | Cosmopo s.r.o. (IČO: 54326940) |
| **Suma** | 1 653 000,00 EUR |
| **Objednávateľ** | Ministerstvo hospodárstva SR |
| **Dátum podpisu** | 12.01.2026 |
| **Založenie firmy** | 28.01.2022 |
| **Sídlo** | Bratislava - Jarovce |
| **CRZ** | https://www.crz.gov.sk/zmluva/11860337/ |

**Prečo je to podozrivé:** Firma s predmetom podnikania **„Turistické ubytovanie"** (NACE 55200) so sídlom v Jarovciach získala 1,65 mil. EUR z Plánu obnovy. Suma je **okrúhla** (presne 1 653 000). Firma má len 4 roky a toto je jej jediná zmluva v CRZ. Otázka: prečo turistické ubytovanie z Jaroviec čerpá z plánu obnovy priemyslu?

**Red flags:** Mladá firma, nesúlad NACE, okrúhla suma, jediná zmluva v CRZ

---

## 6. ejoin operator s.r.o. — 3,23 mil. EUR na nabíjacie stanice

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | ejoin operator s.r.o. (IČO: 53012470) |
| **Suma** | 3 230 000,00 EUR (+ 333 000 EUR koncesia) |
| **Objednávateľ** | Ministerstvo hospodárstva SR |
| **Dátum podpisu** | 23.02.2026 |
| **Založenie firmy** | 12.06.2020 |
| **Sídlo** | Dubnica nad Váhom |
| **CRZ** | https://www.crz.gov.sk/zmluva/12030117/ |

**Prečo je to podozrivé:** IT firma (NACE 62090 — „Ostatné služby týkajúce sa IT") z Dubnice získala 3,23 mil. EUR na zákazku z Plánu obnovy a ďalších 333 000 EUR na koncesiu nabíjacích staníc cez MH Invest. Okrúhla suma. Firma má len 5,7 roka a predtým mala len zmluvy s mestom Liptovský Mikuláš (dodatky za 0 EUR). Skok z nulových zmlúv na 3,5 mil. EUR je výrazný.

**Red flags:** Okrúhla suma, dramatický nárast hodnoty zákaziek, IT firma buduje nabíjacie stanice

---

## 7. Juraj Gutai — MASTER WOOD: duplicitná zmluva 393 236 EUR

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | Juraj Gutai - MASTER WOOD (IČO: 32329351) |
| **Suma** | 393 236,56 EUR × 2 |
| **Objednávateľ** | Ministerstvo hospodárstva SR |
| **Dátum podpisu** | 21.01.2026 (oba) |
| **CRZ** | https://www.crz.gov.sk/zmluva/11886330/ + https://www.crz.gov.sk/zmluva/11984230/ |

**Prečo je to podozrivé:** Identická zmluva pre toho istého živnostníka, na rovnakú sumu, s rovnakým dátumom podpisu — zverejnená dvakrát (22.1. a 12.2.2026). Buď ide o technický duplikát v CRZ, alebo o pokus o **dvojité čerpanie** z Plánu obnovy. Rovnaký živnostník má aj ďalšiu zmluvu (mandátna zmluva za 73 284 EUR s obcou Pribeta na nábytok pre denný stacionár).

**Red flags:** Duplicitná zmluva, živnostník s 786K EUR celkovo z Plánu obnovy

---

## 8. DARK DOG Slovakia — 370-dňové oneskorenie, 103K EUR

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | DARK DOG Slovakia, s.r.o. (IČO: 46257411) |
| **Suma** | 102 700,00 EUR |
| **Objednávateľ** | Ministerstvo hospodárstva SR |
| **Dátum podpisu** | 22.01.2025 |
| **Dátum zverejnenia** | 27.01.2026 |
| **Oneskorenie** | **370 dní** |
| **CRZ** | https://www.crz.gov.sk/zmluva/11904122/ |

**Prečo je to podozrivé:** Firma s predmetom podnikania **„Veľkoobchod s nápojmi"** (NACE) z obce Vlčany čerpá z Plánu obnovy 102 700 EUR. Zmluva bola zverejnená s oneskorením vyše roka. Aký má veľkoobchod s nápojmi vzťah k obnove a odolnosti? Okrúhla suma. Jediná zmluva v CRZ.

**Red flags:** 370-dňové oneskorenie, nesúlad podnikateľskej činnosti, okrúhla suma

---

## 9. Solaray, s.r.o. — 618K EUR, mladá firma z Galanty

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | Solaray, s.r.o. (IČO: 54913489) |
| **Suma** | 618 000,00 EUR |
| **Objednávateľ** | Ministerstvo hospodárstva SR |
| **Dátum podpisu** | 17.02.2026 |
| **Založenie firmy** | 04.10.2022 |
| **Vek firmy pri podpise** | ~3,4 roka |
| **CRZ** | https://www.crz.gov.sk/zmluva/12006954/ |

**Prečo je to podozrivé:** Firma s NACE „Výroba ostatných všeobecných strojov" založená v októbri 2022 získala 618 000 EUR z Plánu obnovy. Okrúhla suma. Jediná zmluva v CRZ. Firma s 3,4-ročnou históriou a bez predchádzajúcich štátnych zákaziek.

**Red flags:** Mladá firma, okrúhla suma, jediná zmluva, žiadna CRZ história

---

## 10. RÜCKSCHLOSS s.r.o. — 3,88 mil. EUR dotácia pre obrábačskú firmu z Banskej Štiavnice

| Parameter | Hodnota |
|---|---|
| **Dodávateľ** | RÜCKSCHLOSS s.r.o. (IČO: 53162731) |
| **Suma** | 3 882 029,00 EUR |
| **Objednávateľ** | Úrad podpredsedu vlády SR pre Plán obnovy |
| **Dátum podpisu** | 18.12.2025 |
| **Založenie firmy** | 16.07.2020 |
| **Vek firmy pri podpise** | ~5,4 roka |
| **CRZ** | https://www.crz.gov.sk/zmluva/11775131/ |

**Prečo je to podozrivé:** Firma s NACE kódom **„Obrábanie"** (25620) z Banskej Štiavnice, založená v roku 2020, získala takmer 4 mil. EUR ako **dotáciu** priamo od Úradu podpredsedu vlády pre Plán obnovy. Je to jej **jediná zmluva** v celom CRZ. Firma s 5-ročnou históriou a obrábacím zameraním dostala jednu z najväčších individuálnych dotácií z Plánu obnovy — prečo?

**Red flags:** Mladá firma, jediná zmluva v CRZ, vysoká suma dotácie, úzko špecializovaný NACE

---

## Súhrnná tabuľka

| # | Dodávateľ | Suma (EUR) | Hlavný red flag |
|---|---|---|---|
| 1 | SWAN, a.s. | 7 981 200 | Daňovo nespoľahlivý subjekt |
| 2 | Min. spravodlivosti SR | 60 408 004 × 2 | Duplicitné zmluvy |
| 3 | DOMOV SENIOROV Tatranská Štrba | 2 663 014 | 507-dňové oneskorenie |
| 4 | HS Development, s.r.o. | 1 334 312 | Mladá veľkoobchodná firma, jediná zmluva |
| 5 | Cosmopo s.r.o. | 1 653 000 | Turistické ubytovanie, nesúlad NACE |
| 6 | ejoin operator s.r.o. | 3 230 000 | IT firma buduje nabíjačky, okrúhla suma |
| 7 | Juraj Gutai — MASTER WOOD | 393 237 × 2 | Duplicitná zmluva |
| 8 | DARK DOG Slovakia, s.r.o. | 102 700 | 370-dňové oneskorenie, veľkoobchod s nápojmi |
| 9 | Solaray, s.r.o. | 618 000 | Mladá firma, okrúhla suma, bez histórie |
| 10 | RÜCKSCHLOSS s.r.o. | 3 882 029 | Obrábačská firma, 4M dotácia, bez histórie |

---

## Odporúčania na ďalšie preverenie

1. **RPVS kontrola** — overiť konečných užívateľov výhod pre: Cosmopo, HS Development, Solaray, ejoin operator, RÜCKSCHLOSS. Hľadať prepojenia na politicky exponované osoby.
2. **FinStat obohatenie** — stiahnuť finančné výkazy (tržby, zisk, aktíva) pre všetky podozrivé firmy a overiť, či hodnota zmluvy nepresahuje 2× ročné tržby.
3. **Foaf.sk sieťová analýza** — overiť, či majitelia/konatelia podozrivých firiem nesedia v iných firmách, ktoré tiež čerpajú z Plánu obnovy.
4. **Duplicity Min. spravodlivosti** — vyžiadať vysvetlenie, prečo sú identické zmluvy za 60,4 mil. EUR zverejnené pre dva rôzne súdy.
5. **Oneskorené zverejnenie** — podať podnet na Úrad pre verejné obstarávanie ohľadom 507- a 370-dňových oneskorení.

---

*Ďakujeme Žltej Stope*
