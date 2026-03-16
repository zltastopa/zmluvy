# Kriticka validacia: Q4 2025

## Sumar validacie
- Pocet najdov na vstupe: 5
- CONFIRMED: 0
- DISMISSED: 4
- INCONCLUSIVE: 1

---

## CONFIRMED najdy

(Ziadne najdy neboli potvrdene ako skutocne podozrive.)

---

## INCONCLUSIVE najdy

### 1. TATRA DEFENCE SYSTEMS -- 1.03 mld EUR od Ministerstva obrany (ramcova zmluva)

**Co sme overili:**

1. **Datovy artefakt (Step 1):** Zmluva ID 11760561, "RAMCOVA ZMLUVA c. SEMOD-179/2025-7", podpisana a zverejnena 2025-12-17, suma 1 032 689 734 EUR. Existuje v databaze prave raz -- nejde o duplikat. Dodavatel ICO 08993289.

2. **Nevine vysvetlenie (Step 2):**
   - **Ramcova zmluva** urcuje maximalny financny strop na viacere roky, nie jednorazovu platbu. Skutocne cerpanie byva vyrazne nizsie. Je to standardny instrument pre dlhodobe obranecke programy.
   - **Obranecke nakupy** v miliardovom rozsahu su legitimne v kontexte modernizacie armady SR (analogia: NDS dialnicne kontrakty za stovky milionov).
   - TATRA DEFENCE SYSTEMS (ICO 08993289) je sucastou skupiny Tatra Defence Group / Czechoslovak Group (CSG), najvacsieho stredoeuropskeho obranneho koncernu.

3. **Registre:** Firma nema negativne zaznamy -- nie je danovy dlznik, nie je dlznik VSZP, nema dovody na zrusenie DPH. Jedina zlta stopa: "Dodavatel nie je v RUZ" (info uroven) -- firma nema uctovnu zavierku v registri.

4. **Vzorce (Step 3):** Analogia s "NDS highway contracts -- multi-hundred-million infrastructure is expected". Obranecke ramcove zmluvy su porovnatelne.

**Preco to zostava nejasne:**
- Suma 1.03 mld EUR je extremne vysoka -- cca 0.8 % HDP Slovenska. Aj pre ramcovu zmluvu je to na hornej hranici.
- ICO 08993289 naznacuje zalozenie okolo roku 2019 -- relativne nova firma na miliardovy kontrakt.
- Firma nie je v RUZ -- nevieme overit financne zdravie, velkost firmy, pocet zamestnancov.
- Je to jedina zmluva tejto firmy v CRZ -- ziadna historia dodavatelskeho vztahu.
- Nevieme overit, ci prebehlo riadne obstaravanie cez UVO (obranecke zakazky mozu mat vynimku, ale aj tak musia splnit podmienky transparentnosti).
- Nevieme overit beneficnych vlastnikov cez RPVS.

**Dalsie kroky:**
- FinStat enrichment pre ICO 08993289 -- overit trzby, zamestnancov, vlastnicku strukturu
- RPVS lookup -- overit konecnych uzivatelov vyhod
- foaf.sk -- mapovat korporatnu siet a personalne prepojenia (CSG vazby)
- UVO vestnik -- vyhladat ci existuje verejne obstaravacie oznamenie
- CRZ detail: https://www.crz.gov.sk/zmluva/11760561/ -- overit prilohy a podmienky ramcovej zmluvy (trvanie, milniky, penale)

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | **Environmentalny fond -- 30M EUR okruhla suma pre Vodohospodarsku vystavbu** | **Datovy artefakt + nevinny vzor.** (a) Zmluva existuje v dvoch kopiach: ID 11773739 (zverejnena Vodohospodarskou vystavbou 2025-12-18) a ID 11849535 (zverejnena Environmentalnym fondom 2026-01-14) -- oba subjekty zverejnili tu istu zmluvu, datum podpisu je zhodny (2025-12-18). Standardny postup na CRZ, nie duplicitne cerpanie. (b) Nazov zmluvy explicitne uvadza "DOTACIA Z PROSTRIEDKOV MODERNIZACNEHO FONDU" -- dotacie maju prirodzene okruhle sumy, su to rozpoctove alokacie, nie trhove ceny. (c) Environmentalny fond je statny fond, Vodohospodarska vystavba (ICO 00156752) je statny podnik -- ide o standardny statny transfer. (d) V tej istej davke Env. fond distribuoval aj dalsie dotacie: 12.1M EUR pre tu istu Vodohospodarsku vystavbu, 22.1M/13.2M/5.6M pre MH Teplarensky holding. Vzor zodpoveda kategorii "Ministry/fond -> statny podnik dotacie". Zlte stopy: iba "Neuvedena platnost" (info) a "Neobvykle vysoka suma" (warning, ale ocakavane pre dotacie z Modernizacneho fondu). |
| 2 | **Fond na podporu vzdelavania -> Tomas Hengerics -- 457 zmluv za 4.2M EUR** | **FALESNY NAJD -- data nepotvrduju tvrdenie.** Meno "Tomas Hengerics" v databaze CRZ vobec neexistuje (0 zaznamov). Jediny Hengerics je "Mgr. Alexandra Hengerics Szabo, PhD." s 1 zmluvou za 1 025 EUR pre Univerzitu J. Selyeho. Fond na podporu vzdelavania ma v databaze celkovo iba 4 zmluvy za 342 092 EUR s 3 dodavatelmi. Cisla "457 zmluv" a "4.2M EUR" neodpovedaju ziadnym realnym datam v CRZ. Navyse, aj keby sa najd potvrdil, Fond na podporu vzdelavania je studentsky pozickovy fond -- velke mnozstvo malych zmluv s jednotlivcami by bolo standardne (pozicky studentom) a zodpovedalo by vzorcu "Fond na podporu vzdelavania -- student loan fund, many small contracts to individuals is normal." |
| 3 | **Hruzova Zuzana, Bc. -- 506 zmluv za 13.6M EUR bez ICO** | **FALESNY NAJD -- data nepotvrduju tvrdenie.** Meno "Hruzova" (v akejkolvek forme) v databaze CRZ vobec neexistuje -- ani ako dodavatel, ani ako objednavatel (0 zaznamov). V celej databaze neexistuje ziaden individualny dodavatel bez ICO s 400+ zmluvami. Najvyssi pocet zmluv pre jedneho dodavatela bez ICO je 204 ("Neuvedene" pre Matersku skolu Zeleznicna). Cisla "506 zmluv" a "13.6M EUR" su neoveritelne a neodpovedaju ziadnym realnym datam. |
| 4 | **Eduardo Carmona -- 49 zmluv pre APVV po 700 EUR** | **FALESNY NAJD / SKRESLOVANIE + nevinny vzor.** (a) Eduardo Carmona ma v CRZ presne 1 zmluvu (nie 49): "Autorska zmluva o dielo" (ID 11490797), 700 EUR, podpisana 2025-10-22, pre Agenturu na podporu vyskumu a vyvoja (APVV). Zlte stopy: iba "Neuvedena platnost" (info) a "Dodavatel bez ICO" (info). (b) APVV standardne uzatvara autorske zmluvy a prikazne zmluvy s individualnymi vedcami/recenzentmi: v databaze je 195 takychto zmluv so 190 roznymi fyzickymi osobami bez ICO, typicke sumy 100-1 980 EUR. Eduardo Carmona je pravdepodobne zahranicny recenzent/expert -- standardna prax pre hodnotenie vedeckych projektov. Vzor zodpoveda kategorii "Freelancer micro-contracts -- research agencies (APVV) pay many individuals." |

---

**Validacia ukoncena.** 0 najdov potvrdene, 4 vylucene, 1 vyzaduje dalsie overenie.

---

## Metodologicka poznamka

Stiri z piatich najdov boli vylucene:
- **Tri najdy (Hengerics, Hruzova, Carmona)** obsahovali udaje, ktore neodpovedaju realnym datam v CRZ. Tomas Hengerics a Hruzova Zuzana v databaze vobec neexistuju, Carmona ma 1 zmluvu (nie 49). Toto je klasicky pripad, preco je kriticka validacia nevyhnutna -- bez overenia oproti skutocnym datam by tieto falesne najdy mohli byt prezentovane ako investigativne zistenia.
- **Environmentalny fond** je standardna statna dotacia z Modernizacneho fondu pre statny podnik, s duplikatnym zaznamom na CRZ (obe strany zverejnuju).

Jediny najd, ktory prezil validaciu ako INCONCLUSIVE, je **TATRA DEFENCE SYSTEMS** -- zmluva existuje, suma je extremne vysoka, a chyba dostatok dat na posudenie (firma nie je v RUZ, ziadna historia v CRZ, neoverene obstaravanie). Dalsie overenie cez FinStat, RPVS, foaf.sk a UVO vestnik je potrebne.

**Toto su stopy, nie verdikty.**
