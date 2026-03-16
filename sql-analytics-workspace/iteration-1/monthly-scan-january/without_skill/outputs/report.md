# CRZ Mesacny Sken -- Januar 2026

**Datum analyzy:** 2026-03-16
**Obdobie:** 2026-01-01 az 2026-01-31
**Zdroj:** Centralny register zmluv (https://zmluvy.zltastopa.sk/data/crz)

---

## 1. Celkovy prehlad

| Metrika | Hodnota |
|---|---|
| Celkovy pocet zmluv | 49 953 |
| Zmluvy s uvedenou sumou | 26 905 (53.9%) |
| Zmluvy bez sumy (skryta cena) | 23 048 (46.1%) |
| Celkova hodnota | 3 113 348 618 EUR |
| Priemerna hodnota zmluvy | 115 716 EUR |
| Maximalna hodnota | 206 524 377 EUR |
| Pocet red flags | 127 043 |
| Typy zmluv | zmluva: 48 466, dodatok: 1 487 |

**Poznamka:** Takmer polovica zmluv (46.1%) nema uvedenu financnu hodnotu, co je samo o sebe varovnym signalom z hladiska transparentnosti.

---

## 2. Prehlad Red Flags

### 2.1 Sumar podla zavaznosti

| Zavaznost | Typ flagu | Pocet | Popis |
|---|---|---|---|
| DANGER | supplier_advantage | 2 564 | Pokuty zvyhodnuju dodavatela |
| DANGER | tax_unreliable | 915 | Danovo nespolahlivy dodavatel |
| DANGER | fs_tax_debtor | 667 | Danovy dlznik FS |
| DANGER | negative_equity | 654 | Zaporne vlastne imanie |
| DANGER | fresh_company | 468 | Cerstve zalozena firma |
| DANGER | vszp_debtor | 264 | Dlznik zdravotnej poistovne |
| DANGER | fs_vat_deregistered | 261 | Vymazany z DPH registra |
| DANGER | socpoist_debtor | 259 | Dlznik Socialnej poistovne |
| DANGER | tax_unreliable_entity | 161 | Danovo nespolahlivy subjekt v zmluve |
| DANGER | terminated_company | 104 | Zrusena firma |
| DANGER | fs_vat_dereg_risk | 79 | Dovody na zrusenie DPH |
| DANGER | fresh_micro_large | 1 | Nova mikro firma, velka zmluva |
| WARNING | hidden_price | 23 051 | Skryta cena |
| WARNING | signatory_overlap | 19 355 | Zdielany podpisujuci |
| WARNING | nace_mismatch | 4 284 | Nesulad odvetvia |
| WARNING | hidden_entities | 3 829 | Skryte entity v zmluve |
| WARNING | rapid_succession | 3 285 | Zmluvy v rychlom slede |
| WARNING | bezodplatne | 2 963 | Bezodplatna zmluva |
| WARNING | missing_attachment | 1 399 | Chybajuca priloha |
| WARNING | hidden_entity_is_supplier | 1 301 | Skryta entita je dodavatel |
| WARNING | contract_splitting | 294 | Delenie zakazky |
| WARNING | threshold_gaming | 13 | Tesne pod limitom EU sutaze |
| WARNING | dormant_then_active | 7 | Spaca firma |
| WARNING | micro_supplier_large_contract | 76 | Mikro dodavatel, velka zmluva |

**Celkom DANGER flagov: 6 397** na zmluvach v januari 2026.

---

## 3. Najvyssie rizikove zistenia

### 3.1 INVEST 9 - Westend Gate a.s. -- Najom za 42.3M EUR pre VsZP

| Pole | Hodnota |
|---|---|
| ID | 11847539 |
| Objednavatel | Vseobecna zdravotna poistovna a.s. |
| Dodavatel | INVEST 9 - Westend Gate a. s. (ICO: 36288411) |
| Predmet | Zmluva o najme nebytovych priestorov a parkovacich miest |
| Suma | 42 277 656 EUR |
| Datum podpisu | 2026-01-12 |
| URL | https://www.crz.gov.sk/zmluva/11847539/ |
| Red flags | micro_supplier_large_contract, supplier_advantage, amount_outlier |

**Preco je to podozrive:** Najom kancelarii za 42.3M EUR je extremny outlier -- 86.6x standardna odchylka pre kategoriu property_lease (priemer 8 228 EUR). Stoji za hlbsiu analyzu, ci je suma adekvtna dlzke najmu a rozsahu priestorov.

---

### 3.2 PM CEE VC j.s.a. -- Cerstve zalozena firma s 5.1M EUR zmluvou

| Pole | Hodnota |
|---|---|
| ID | 11912433 |
| Objednavatel | Venture to Future Fund, a.s. |
| Dodavatel | PM CEE VC j. s. a. (ICO: 57316813) |
| Predmet | ASSIGNMENT AGREEMENT concerning POWERFUL MEDICAL |
| Suma | 5 092 250 EUR |
| Datum podpisu | 2026-01-28 |
| URL | https://www.crz.gov.sk/zmluva/11912433/ |
| Red flags | fresh_company, threshold_gaming |
| Detail | Firma zalozena 18.11.2025 -- iba 2 mesiace pred zmluvou |

**Preco je to podozrive:** Spolocnost zalozena len 2 mesiace pred podpisom zmluvy za viac ako 5 milionov EUR. Ide o jediny "fresh_micro_large" flag v celom januari. Vysoko rizikovy profil -- mlada firma bez historie ziskava velku zakazku.

---

### 3.3 Duna-Hus s.r.o. -- Kumulacia 8 red flags

| Pole | Hodnota |
|---|---|
| ID | 11852407 |
| Objednavatel | ZS a Gymnazium s VJM, Dunajska 13, Bratislava |
| Dodavatel | Duna-Hus s.r.o. |
| Predmet | Ramcova zmluva na dodavku masa a masovych vyrobkov |
| Red flags | fs_tax_debtor, fs_vat_dereg_risk, fs_vat_deregistered, hidden_price, missing_expiry, socpoist_debtor, tax_unreliable, vszp_debtor |

**Preco je to podozrive:** Dodavatel je sucasne danovy dlznik FS, dlznik Socialnej poistovne, dlznik VsZP, bol vymazany z DPH registra a existuju dovody na jeho zrusenie. Skola napriek tomu uzavrela ramcovu zmluvu na dodavky potravin -- priamy rozpor so zakonom o verejnom obstaravani.

---

### 3.4 Delenie zakazky -- NDS a CSOB Leasing (40+ ciastkovych zmluv)

Narodna dialnicna spolocnost uzavrela v januari 2026 s CSOB Leasing, a.s. minimalne **40 ciastkovych zmluv** o operativnom leasingu sluzobnch vozidiel (kazda za cca 800-1400 EUR). Kazda z nich ma 8-9 red flags:

- `contract_splitting` -- delenie zakazky
- `rapid_succession` -- zmluvy v rychlom slede
- `supplier_monopoly` -- monopolny dodavatel
- `hidden_entities` + `hidden_entity_is_supplier`
- `nace_mismatch` -- nesulad odvetvia
- `signatory_overlap` -- zdielany podpisujuci

**Preco je to podozrive:** Systematicke delenie jednej velkej zakazky na desiatky malych zmluv moze byt sposobom, ako sa vyhnut prahovym hodnotam pre verejne obstaravanie. Celkova suma za 40 zmluv je cca 38 347 EUR -- stale relativne nizka, ale vzor je typicky pre contract splitting.

---

### 3.5 Lubomir Ludvik LUTEX -- Danovo nespolahlivy dodavatel s mnozstvom obecnych zmluv

Tento dodavatel (zbieranie pouziteho satstva) sa objavuje vo viacerych zmluvach s obcami, pricom kazda nesie 9 red flags:

- `fs_vat_deregistered` -- vymazany z DPH registra
- `tax_unreliable` + `tax_unreliable_entity`
- `fs_tax_debtor` -- danovy dlznik
- `hidden_entities` + `hidden_entity_is_supplier`
- `nace_mismatch`

Obce Sarisske Jastrabie, Spissky Hrusov, Vrbov, Orlov -- vsetky uzavreli zmluvy s touto firmou napriek jej zhorsene mu danovemu statusu.

---

### 3.6 Threshold Gaming -- Zmluvy tesne pod EU limitom (215 000 EUR)

Identifikovanych **13 zmluv** tesne pod EU limitom pre verejne obstaravanie:

| Zmluva | Objednavatel | Dodavatel | Suma | Rozdiel od limitu |
|---|---|---|---|---|
| 11904313 | Centrum spol. a psych. vied SAV | Go4insight + ACRC | 214 860 EUR | -140 EUR |
| 11659647 | SEPS a.s. | SecuriLas s.r.o. | 214 843 EUR | -157 EUR |
| 11880570 | BVS a.s. | TP Sante s.r.o. | 214 500 EUR | -500 EUR |
| 11830301 | UPJS Kosice | Anton Paar Slovakia | 213 405 EUR | -1 595 EUR |
| 11833331 | NUSCH Bratislava | INTEC PHARMA s.r.o. | 213 200 EUR | -1 800 EUR |
| 11882616 | Min. cest. ruchu a sportu | Slov. paralympijsky vybor | 213 100 EUR | -1 900 EUR |

**Preco je to podozrive:** Zmluvy s hodnotou iba 140-1900 EUR pod hranicou 215 000 EUR naznacuju umyselne nastavenie sumy tak, aby sa obisla povinnost medzinarodnej sutaze podla EU pravidiel.

---

### 3.7 Dodavatelia so zapornym vlastnym imanim na velkych zmluvach

| Dodavatel | ICO | Suma zmluvy | Vlastne imanie | Objednavatel |
|---|---|---|---|---|
| OSZZS SR | 36076643 | 30 773 241 EUR | -2 654 296 EUR | Min. zdravotnictva SR |
| Lavaton s.r.o. | 36244848 | 2 642 860 EUR | -519 031 EUR | FN Trnava |
| PERLA GASTRO s.r.o. | 36780979 | 1 988 628 EUR | -53 621 EUR | Mesto Banska Bystrica |
| MERTEL s.r.o. | 35967412 | 529 021 EUR | -22 179 EUR | Sekcia VO MO SR |

**Preco je to podozrive:** Firmy so zapornym vlastnym imanim su v technickom upadku. Uzatvarat s nimi zmluvy za miliony predstavuje vysoke riziko neplnenia a moznej straty verejnych prostriedkov.

---

### 3.8 Spiace (dormant) firmy -- nahlly navrat k aktivite

| Dodavatel | ICO | Suma | Obdobie neaktivity | Objednavatel |
|---|---|---|---|---|
| IOM (Medzinar. org. pre migraciu) | 31768679 | 2 178 902 EUR | 2.1 roka | Min. vnutra SR |
| Min. zivot. prostredia SR | 42181810 | 1 998 300 EUR | 3.5 roka | Podtatranska vodar. spol. |
| ENVIGEO a.s. | 31600891 | 91 610 EUR | **11.0 rokov** | Bratislavska vodarenska spol. |
| LABO-SK s.r.o. | 36365556 | 148 092 EUR | 3.8 roka | Biomedic. centrum SAV |

**Preco je to podozrive:** Firmy, ktore roky nemali ziadnu zmluvnu aktivitu, naraz ziskavaju velke zakazky. Najmarkantnejsi pripad je ENVIGEO a.s. -- 11 rokov bez zmluvy a naraz zakazka za 91 610 EUR.

---

## 4. Koncentracia zmluv -- Top objednavatelia

| Objednavatel | Pocet zmluv | Celkova hodnota |
|---|---|---|
| Min. skolstva, vyskumu, vyvoja a mladeze SR | 79 | 908 499 160 EUR |
| Min. cestovneho ruchu a sportu SR | 81 | 148 201 557 EUR |
| Narodna dialnicna spolocnost a.s. | 198 | 122 513 372 EUR |
| Statny fond rozvoja byvania | 309 | 121 113 675 EUR |
| Environmentalny fond | 8 | 77 375 899 EUR |
| Zeleznice SR | 297 | 76 702 598 EUR |
| Min. investicii, reg. rozvoja a informatizacie SR | 24 | 76 045 596 EUR |
| Min. kultury SR | 18 | 69 446 339 EUR |

---

## 5. Koncentracia zmluv -- Top dodavatelia

| Dodavatel | ICO | Pocet zmluv | Celkova hodnota |
|---|---|---|---|
| Univerzita Komenskeho v Bratislave | 00397865 | 12 | 206 632 466 EUR |
| Min. investicii, reg. rozvoja a informatizacie SR | 50349287 | 122 | 148 312 191 EUR |
| Slovenska technicka univerzita v Bratislave | 00397687 | 50 | 126 518 739 EUR |
| Technicka univerzita v Kosiciach | 00397610 | 27 | 94 387 369 EUR |
| Slovenska akademia vied | 00037869 | 51 | 79 540 460 EUR |
| UPJS Kosice | 00397768 | 6 | 65 978 598 EUR |
| Doprastav a.s. | 31333320 | 1 | 64 871 098 EUR |

---

## 6. Casove vzory

### Podozrive datumy zverejnenia
- **1. januar (94 zmluv):** Standardne nizky pocet -- sviatky
- **30. januar (3 542 zmluv):** Najvyssi pocet -- koncorocny tlak na uzatvaranie zmluv
- **31. januar (158 zmluv):** Prudky pokles -- sobota

### Oneskorene zverejnenie (podpis -> zverejnenie > 90 dni)
Najhorsi pripad: zmluva podpisana 23.1.2020, zverejnena 14.1.2026 -- **oneskorenie 2 183 dni (takmer 6 rokov)**. Viacero skol (napr. Gymnazium Malacky) hromadne zverejnilo stare zmluvy s oneskorenim 3-5 rokov.

---

## 7. Duplicitne zverejnenia

Viacero zmluv bolo zverejnenych dvakrat -- raz objednavatelom, raz dodavatelom:

| Zmluva | Strana 1 | Strana 2 | Suma |
|---|---|---|---|
| KONTRAKT NASES 2026 | MIRRI SR | NASES | 49 038 418 EUR |
| KONTRAKT MZ-OSZZS 2026 | MZ SR | OSZZS SR | 30 773 241 EUR |
| FPU Prispevok 2026 | MK SR | Fond na podporu umenia | 30 200 000 EUR |

Tieto duplicity su legitimne (obe strany zverejnuju), ale skresluji statisticke analyzy.

---

## 8. Odporucania na hlbsi vysetrovanie

### Vysoka priorita
1. **PM CEE VC j.s.a.** (ICO: 57316813) -- 2-mesacna firma s 5.1M EUR zmluvou. Overit vlastnicku strukturu, spojenie na Venture to Future Fund, a.s.
2. **INVEST 9 - Westend Gate a.s.** (ICO: 36288411) -- Najom za 42.3M EUR pre statnu poistovnu. Overit trhovu primeranost, vlastnikov.
3. **Duna-Hus s.r.o.** -- 8 red flags vratane dlhov na daniach, socialnom a zdravotnom poisteni. Skola by nemala nakupovat od takehoto dodavatela.

### Stredna priorita
4. **NDS + CSOB Leasing** -- Delenie zakazky na 40+ ciastkovych zmluv.
5. **Threshold gaming** -- 13 zmluv tesne pod EU limitom, obzvlast Go4insight/ACRC (iba 140 EUR pod limitom).
6. **Lubomir Ludvik LUTEX** -- Systematicky danovo nespolahlivy dodavatel, napriek tomu ziskava obecne zakazky.
7. **ENVIGEO a.s.** -- 11 rokov neaktivity, naraz zakazka od BVS.

### Systemove problemy
8. **46% zmluv bez uvedenej sumy** -- Masivny problem transparentnosti.
9. **Hromadne oneskorene zverejnovanie** -- Gymnazium Malacky a dalsie institucii zverejnili zmluvy s viacrocnym oneskorenim.
10. **654 zmluv s dodavatelmi so zapornym vlastnym imanim** -- Systemove riziko.

---

## 9. Metodologia

Analyza bola vykonana prostrednictvom SQL dotazov proti Datasette API nad databazou CRZ. Vyuzite boli tabulky:
- `zmluvy` -- zakladne udaje o zmluvach
- `red_flags` -- automatizovane varovne signaly
- `flag_rules` -- definicie varovnych signalov
- `extractions` -- LLM-extrahovane polia
- `ruz_equity` -- udaje o vlastnom imani z registra uctovnych zavierok

Dotazy pokryvali:
- Celkove statistiky za januar 2026
- Top objednavatelov a dodavatelov podla objemu
- Analyzu red flags podla typu a zavaznosti
- Zmluvy s najvyssim poctom varovnych signalov
- Oneskorene zverejnenia (podpis vs. publikacia)
- Threshold gaming (tesne pod EU limitom)
- Cerstve zalozene firmy s velkymi zakazkami
- Dodavatelov so zapornym vlastnym imanim
- Spiace firmy s nahlou aktivitou
- Delenie zakaziek (contract splitting)
- Dodavatelov -- danovych dlznikov
