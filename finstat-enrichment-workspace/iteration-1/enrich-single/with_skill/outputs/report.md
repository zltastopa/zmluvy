# FinStat enrichment: SFINGA s.r.o. (ICO 51671824) -- zmluva za 1,29M EUR s PE-ES, n.o.

## Sumar
- Pocet dodavatelov: 1
- Financne zlte stopy: 1 DANGER, 1 WARNING
- Najkritickejsi dodavatel: SFINGA s.r.o. (zmluva 2,84x prevysuje rocne trzby, vysoka zadlzenost 77,58 %)

---

## Dodavatel 1: SFINGA s.r.o. (ICO 51671824)

**Zdroj:** [finstat.sk/51671824](https://finstat.sk/51671824) + lokalna DB (crz.db)

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | 454 385 EUR (2024) |
| Celkove vynosy | 454 464 EUR (2024) |
| Zisk (profit) | 5 079 EUR (2024) |
| Aktiva (assets) | 266 274 EUR (2024) |
| Vlastny kapital (equity) | 59 691 EUR (2024) |
| Zakladne imanie | 5 000 EUR |
| Celkova zadlzenost | 77,58 % |
| Hruba marza | 7,08 % |
| Datum vzniku | 25.05.2018 |
| Pravna forma | Spol. s r.o. |
| NACE | 41209 -- Vystavba obytnych a neobytnych budov i.n. |
| Velkost organizacie | nezisteny (podla RUZ) |
| Danova spolahlivost | spolahlivy |
| Dlhy VSZP | nezistene |
| Dlhy Socialna poistovna | nezistene |
| Dlhy Financna sprava | nezistene |
| Vymazany z DPH | nie |

### Historicky vyvoj zisku (FinStat, 2020-2024)

| Rok | Zisk |
|---|---|
| 2020 | 18 758 EUR |
| 2021 | 8 936 EUR |
| 2022 | 5 153 EUR |
| 2023 | 11 291 EUR |
| 2024 | 5 079 EUR |

Klesajuci trend zisku: pokles o 55 % medzi 2023 a 2024. Kumulovany zisk za 5 rokov je cca 49 217 EUR.

### Struktura pasiv (2024, podla FinStat)

| Polozka | Suma |
|---|---|
| Zakladne imanie | 5 000 EUR |
| Fondy zo zisku | 500 EUR |
| VH minulych rokov | 49 112 EUR |
| VH za uctovne obdobie | 5 079 EUR |
| **Vlastny kapital spolu** | **59 691 EUR** |
| Kratkodobe zavazky | 38 889 EUR |
| Kratkodobe financne vypomoci | 167 694 EUR |
| **Celkove aktiva** | **266 274 EUR** |

Poznamka: Kratkodobe financne vypomoci (167 694 EUR) tvoria 63 % celkovych aktiv -- firma je vyrazne zavisla na kratkodobom financovani.

### Zmluvy v CRZ

| ID | Suma | Nazov zmluvy | Objednavatel | Datum podpisu | Datum zverejnenia | Oneskorenie |
|---|---|---|---|---|---|---|
| 11946081 | 1 291 200 EUR | Zmluva o dielo c. 1/2024 | PE-ES, n.o. | 04.10.2024 | 05.02.2026 | **489 dni** |

**Predmet zmluvy:** Stavebne prace na diele "Zariadenie pre seniorov Diviacka Nova Ves" podla projektovej dokumentacie a vykazu poloziek. Termin ukoncenia: 01.04.2028.

**Existujuce zlte stopy v DB pre tento kontrakt:**
| Zlta stopa | Severity | Detail |
|---|---|---|
| Neuvedena platnost (missing_expiry) | info | -- |
| Zdielany podpisujuci (signatory_overlap) | warning | PhDr. Lubica Geczyova podpisuje za 3 roznych dodavatelov |

### Financne zlte stopy (vyhodnotenie podla skill pravidiel)

| Zlta stopa | Severity | Detail |
|---|---|---|
| `contract_exceeds_2x_revenue` | **DANGER** | Zmluva 1 291 200 EUR je **2,84x vacsia** nez rocne trzby firmy (454 385 EUR). Firma nema financnu kapacitu na realizaciu zakazky tohto rozsahu z vlastnych zdrojov. |
| `missing_rpvs` | **WARNING** | Zmluva presahuje 100 000 EUR s verejnym sektorom -- firma by mala byt registrovana v RPVS ako partner verejneho sektora. Potrebna manualna verifikacia v RPVS registri. |

**Dalsie pravidla -- vyhodnotenie:**
| Pravidlo | Vysledok |
|---|---|
| `negative_equity` | OK -- vlastny kapital 59 691 EUR je kladny |
| `severe_loss` | OK -- firma je ziskova (zisk 5 079 EUR) |
| `tax_unreliable` | OK -- danovo spolahlivy subjekt |
| `unusually_high_profit` | OK -- ziskova marza 1,1 % (5 079 / 454 385) je nizka |
| `young_company` | OK -- firma zalozena 25.05.2018, zmluva podpisana 04.10.2024 (6,4 roka) |

### Hodnotenie

SFINGA s.r.o. je mala stavebna firma s rocnymi trzbami 454 385 EUR, ktora podpisala zmluvu o dielo v hodnote 1 291 200 EUR -- teda **2,84-nasobok svojich rocnych trzb**. Vlastny kapital firmy (59 691 EUR) pokryva len 4,6 % hodnoty zmluvy, firma je zadlzena na 77,58 % a vyrazne zavisla na kratkodobych financnych vypomociach (167 694 EUR). Zisk firmy ma klesajucu tendenciu a v roku 2024 dosiahol len 5 079 EUR. Zmluva bola navyse zverejnena az 489 dni po podpise, co je extremne oneskorenie.

**Zaver:** Financne ukazovatele SFINGA s.r.o. vyvolavaju vazne pochybnosti o schopnosti firmy realizovat zakazku v hodnote 1,29M EUR. Firma je prilis mala, podkapitalizovana a zavisla na cudzich zdrojoch. Toto su vsak stopy, nie verdikty -- moze ist napr. o subdodavatelsky model alebo postupne financovanie. Odporuca sa dalsie overenie cez RPVS (beneficiarni vlastnici) a FOAF.sk (prepojene osoby a firmy).

---

**Enrichment ukonceny.** Najzavaznejsie zistenie: zmluva za 1 291 200 EUR vyrazne prevysuje financne moznosti firmy SFINGA s.r.o. (trzby 454 385 EUR, vlastny kapital 59 691 EUR). Kombinacia vysokej zadlzenosti (77,58 %), nizkej ziskovosti (1,1 %) a extremneho oneskorenia zverejnenia (489 dni) tvori viacero zlych stop, ktore si vyzaduju dalsie vysetrovanie.
