# INVESTIGATIVNA SPRAVA: DREVEX s.r.o. (ICO 36835463)

## Zhrnutie

DREVEX s.r.o. uzatvoril zmluvu s obcou Liptovske Sliace na 212 784 EUR — presne 2 216 EUR pod EU limitom 215 000 EUR. O 17 dni neskor dodatok zvysil sumu na 541 260 EUR, vysoko nad limit. Vsetky 4 zmluvy spolocnosti su od rovnakej obce a tvoria 82,9% celkoveho objemu 912 875 EUR.

---

## CONFIRMED: Zmluva za 212 784 EUR — presne 2 216 EUR pod EU limitom 215 000 EUR (912 875 EUR) — HIGH

### Co sme nasli

| ID Zmluvy | Nazov | Objednatel | Suma (EUR) | Datum podpisu | CRZ URL |
|---|---|---|---|---|---|
| 11353827 | Zmluva o dielo | Obec Liptovske Sliace | 212 783.85 | 2025-06-15 | https://www.crz.gov.sk/zmluva/11353827/ |
| 11387669 | Dodatok c. 1 | Obec Liptovske Sliace | 541 259.81 | 2025-07-02 | https://www.crz.gov.sk/zmluva/11387669/ |
| 11696268 | Zmluva o dielo (Multifunkcne ihrisko) | Obec Liptovske Sliace | 84 040.80 | 2025-10-14 | https://www.crz.gov.sk/zmluva/11696268/ |
| 11938512 | Zmluva o dielo (Revitalizacia centra) | Obec Liptovske Sliace | 74 791.02 | 2025-12-18 | https://www.crz.gov.sk/zmluva/11938512/ |

**Celkovy objem:** 912 875.48 EUR
**Pocet zmlup:** 4
**Objednatel:** Obec Liptovske Sliace (ICO 00315427)

### Preco je to podozrive

**1. Strategicke podhodnotenie pod EU limitom**

Povodna zmluva (ID 11353827) bola podpisana 15. juna 2025 na sumu **212 783.85 EUR** — presne **2 216 EUR pod EU prahom 215 000 EUR**. Pod tymto limitom sa nevyzaduje euroopske publikovanie zakazky.

**Timeline:**
```
2025-06-15: Zmluva o dielo          212 783.85 EUR  (2 216 EUR pod limitom)
2025-07-02: Dodatok c. 1            541 259.81 EUR  (navysenie o 154%)
            ----------------------------------------
            CELKOM po dodatku:      754 043.66 EUR  (vysoko nad limitom)
```

O **17 dni** po podpisani povodnej zmluvy bol podpisany dodatok, ktory navysil sumu na **541 259.81 EUR** — co je navysenie o **154%** a celkovo presahuje povodnu sumu o **328 475.96 EUR**. Vysledna hodnota 754 043.66 EUR je vysoko nad EU limitom, ktory sa mal pouzit pri povodnom obstaravani.

**2. Absolutna zavislost na jednom objednatelovi**

Vsetky 4 zmluvy DREVEX s.r.o. su od **Obce Liptovske Sliace**:
- Podiel na celkovom objeme: **82.9%** (zmluvy 11353827 a 11387669)
- Zostávajuce 2 zmluvy (84 040.80 EUR + 74 791.02 EUR) su tiez od rovnakej obce
- **100% obchodnej aktivity** spolocnosti v CRZ pochádza z jedneho verejneho obstaravatela

Takato koncentracia zvysuje riziko netransparentnych vztahov a korupcie.

### Zlte stopy

| Stopa | Severity | Detail |
|---|---|---|
| threshold_gaming | DANGER | Povodna zmluva 212 784 EUR je 2 216 EUR pod EU limitom. Dodatok nasledne zvysil na 541 260 EUR. |
| buyer_concentration | WARNING | Vsetky 4 zmluvy od rovnakej obce |

### Dokazy

| Zmluva | CRZ URL | PDF |
|---|---|---|
| 11353827 — Zmluva o dielo | https://www.crz.gov.sk/zmluva/11353827/ | https://www.crz.gov.sk/zmluva/11353827/dokument/ |
| 11387669 — Dodatok c. 1 | https://www.crz.gov.sk/zmluva/11387669/ | https://www.crz.gov.sk/zmluva/11387669/dokument/ |
| 11696268 — Multifunkcne ihrisko | https://www.crz.gov.sk/zmluva/11696268/ | https://www.crz.gov.sk/zmluva/11696268/dokument/ |
| 11938512 — Revitalizacia centra | https://www.crz.gov.sk/zmluva/11938512/ | https://www.crz.gov.sk/zmluva/11938512/dokument/ |

---

## Schema: Ako to funguje

```
    Obec Liptovske Sliace
    (ICO 00315427)
            |
            |
      100% zmlup
            |
            v
      DREVEX s.r.o.
      (ICO 36835463)
            |
     912 875 EUR celkom
     (4 zmluvy 2025-2026)
```

---

## Klucove otazky pre dalsie vysetrovanie

1. **Existuju osobne prepojenia** medzi vedenim DREVEX s.r.o. a clenmi obecneho zastupitelstva alebo starostom obce Liptovske Sliace? (RPVS lookup, foaf.sk)

2. **Ako prebehlo verejne obstaravanie** pre zmluvu 11353827? Bol to priamy sut, alebo sutaz s jednou ponukou? (UVO lookup)

3. **Ake boli financne parametre DREVEX s.r.o.** v case podpisu zmluvy? Mal firma dostatocne trzby a kapacitu na realizaciu zakazky za 212K EUR a neskor 541K EUR? (FinStat enrichment)

4. **Existuju dalsie firmy** s podobnymi vzorcami (pod-limitne zmluvy + navysovacie dodatky) u tej istej obce? (SQL analytics na ICO 00315427)

5. **Co obsahuje dodatok c. 1?** Ake boli dovody pre navysenie o 154%? Je tam jasne odovodnenie zmeny rozsahu prac? (Manualna analyza PDF)

---

> *Dakujeme Zltej Stope*
