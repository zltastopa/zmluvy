# Kriticka validacia: Q4 2025

## Sumar validacie
- Pocet najdov na vstupe: 5
- CONFIRMED: 0
- DISMISSED: 5
- INCONCLUSIVE: 0

---

## CONFIRMED najdy

(ziadne)

---

## INCONCLUSIVE najdy

(ziadne)

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | TATRA DEFENCE SYSTEMS -- 1.03 mld EUR od MO SR (ramcova zmluva) | Ramcova zmluva c. SEMOD-179/2025-7 za 1 032 689 734 EUR je legitima obranno-priemyselna zakazka. TATRA DEFENCE SYSTEMS s.r.o. (ICO 08993289) je znamy vyrobca obrnencov (8x8 Tatra). Jedina zlta stopa na zmluve je "nie je v RUZ" (info), co je bezne pre obrannych dodavatelov s osobitnym rezimom. Nie je dlznikom v ziadnom registri. Ramcove zmluvy v obrane bezne dosahuju miliardove sumy -- ide o maximalny strop na viacrocne dodavky, nie jednorazovu platbu. Ziadne debt/tax/VAT varovania. |
| 2 | Environmentalny fond -- 30M EUR okruhla suma pre Vodohospodarsku vystavbu | Vzorovy priklad nevinneho patternu. Zmluva c. 11849535: "ZMLUVA O POSKYTNUTI PODPORY Z ENVIRONMENTALNEHO FONDU FORMOU DOTACIE Z PROSTRIEDKOV MODERNIZACNEHO FONDU" -- presne zodpoveda patternu "Environmentalny fond / Modernizacny fond dotacie". Prijemca VODOHOSPODARSKA VYSTAVBA, STATNY PODNIK (ICO 00156752) je statny podnik zalozeny 1989, 250-499 zamestnancov, statne vlastnictvo. Okruhla suma 30 000 000 EUR je standardna pre dotacne zmluvy z EU fondov. Fond zaroven poskytuje aj dalsie dotacie (napr. MH Teplarensky holding za 27.2M a 4.7M EUR). Plne zodpoveda statutarnym prerozdelovanim EU prostriedkov. |
| 3 | Fond na podporu vzdelavania -> Tomas Hengerics -- 457 zmluv za 4.2M EUR | Falesny pozitiv -- zmiesnanie urovni. Tomas Hengerics ma v CRZ len 1 zmluvu o pozicke (id 11641718) za 11 571 EUR, kde je OBJEDNAVATELOM (dlznikom), nie dodavatelom. Fond na podporu vzdelavania (ICO 47245531) je dodavatelom -- je to studentsky pozickovy fond. Celkovo ma fond 596 zmluv za ~10.5M EUR, vsetky su individualne pozicky studentom. Cislo "457 zmluv za 4.2M" bolo zrejme vytiahnute z agregacie samotneho fondu a nespravne priradene Hengericsovi. Fond na podporu vzdelavania je explicitne uvedeny v zozname nevinnych patternov -- "studentsky pozickovy fond, mnozstvo malych zmluv s fyzickymi osobami je normalne". |
| 4 | Hruzova Zuzana, Bc. -- 506 zmluv za 13.6M EUR bez ICO | Klasicky NULL ICO artifact (Sulc Matej lekcia). Realne data: Hruzova Zuzana, Bc. ma v CRZ presne 10 zmluv, vsetky s Obcou Varin, kazda za 15 EUR (celkom 150 EUR). Vsetky su "prenajom kinosaly" a "cvicenie". Tvrdenie o 506 zmluvach za 13.6M EUR je nemozne -- vzniklo pravdepodobne agreganim vsetkych dodavatelov bez ICO (dodavatel_ico IS NULL OR dodavatel_ico = '') do jednej skupiny. V databaze su stovky roznych dodavatelov bez ICO: "Neuvedene" (204), prazdne meno (201), "Fyzicka osoba" (183), atd. Toto je presne ten isty mechanizmus ako pri Sulc Matej, kde 1 676 zmluv patrilo 910 roznym freelancerom. |
| 5 | Eduardo Carmona -- 49 zmluv pre APVV po 700 EUR | Falesny pozitiv. Eduardo Carmona ma v CRZ presne 1 zmluvu za 700 EUR (nie 49). Tvrdenie o 49 zmluvach je neoveritelne a pravdepodobne vzniklo rovnakym NULL ICO agreganim alebo zmiesnenim s inou agregaciou. APVV (Agentura na podporu vyskumu a vyvoja) bezne uzatvara mikro-zmluvy s vyskumnikmi a recenzentmi -- pattern "Freelancer micro-contracts" pre vyskumne agentury. Aj keby mal 49 zmluv po 700 EUR (34 300 EUR celkom), islo by o standardne recenzentske/konzultacne odmeny v akademickom prostredi. |

---

**Validacia ukoncena.** 0 najdov potvrdene, 5 vylucene, 0 vyzaduje dalsie overenie.

### Metodologicka poznamka

Vsetky najdy boli vylucene. Tri z piatich (Hengerics, Hruzova, Carmona) obsahovali fakticky nespravne cisla, ktore nezodpovedaju realnym udajom v CRZ. Ide bud o NULL ICO agreganciu (Sulc Matej lekcia), alebo o nespravne priradenie agregacnych cisel konkretnej osobe. Zvysne dve (TATRA DEFENCE, Environmentalny fond) su legitimne statne mechanizmy -- obranno-priemyselna ramcova zmluva a dotacie z Modernizacneho fondu statnym podnikom.

Tieto najdy su stopy, nie verdikty.
