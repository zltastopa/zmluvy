# Investigativny scan CRZ: 1.--7. marca 2026

**Obdobie:** 2026-03-01 az 2026-03-07
**Pocet zmluv:** 10 251
**Celkova suma:** 658 898 159 EUR
**Unikatni dodavatelia:** 3 495 | **Unikatni objednavatelia:** 2 827

> Toto su zlte stopy, nie verdikty. Kazdy nález vyžaduje dalšie overenie.

---

## Faza 1: SQL analytika -- suhrn

### Distribúcia žltych stop (celkovo 25 860 flagov v obdobi)

| Závažnost | Typ stopy | Pocet |
|-----------|-----------|-------|
| danger | Danovy dlznik FS | 154 |
| danger | Pokuty zvyhodnuju dodavatela | 152 |
| danger | Danovo nespolahlivy dodavatel | 130 |
| danger | Zaporne vlastne imanie | 125 |
| danger | Dlznik VSZP | 106 |
| danger | Vymazany z DPH registra | 50 |
| danger | Dlznik Socialnej poistovne | 43 |
| danger | Danovo nespolahlivy subjekt v zmluve | 35 |
| danger | Zrusena firma | 27 |
| danger | Dovody na zrusenie DPH | 12 |
| warning | Skryta cena | 4 224 |
| warning | Zdielany podpisujuci | 3 802 |
| warning | Skryte entity | 1 001 |
| warning | Nesulad odvetvia (NACE) | 862 |
| warning | Bezodplatna zmluva | 482 |
| warning | Zmluvy v rychlom slede | 470 |
| warning | Skryta entita je dodavatel | 468 |
| warning | Chybajuca priloha | 220 |
| warning | Cerstve zalozena firma | 76 |
| warning | Delenie zakazky | 65 |
| warning | Mikro dodavatel, velka zmluva | 13 |
| warning | Neobvykle vysoka suma | 11 |
| warning | Tesne pod limitom EU sutaze | 5 |
| warning | Neziskovka s velkou zmluvou | 3 |

### Top 5 najvaznejsich nalezov

#### 1. TOPZONE S.R.O. (ICO: 36275000) -- 9 zlytch stop, zmluva #12048188

Zmluva o poskyto\xadvani sluzieb so sumou 0 EUR. Klucove stopy:
- **Vymazany z DPH registra** (rok porusenia 2020, vymazany 02.05.2021)
- **Zaporne vlastne imanie** (-95 442 EUR, obdobie 2018)
- **Pokuty zvyhodnuju dodavatela**
- **Nesulad odvetvia** -- NACE: Nespecializovany velkoobchod, zmluva: software/IT
- **Skryta entita je dodavatel** -- Termalne kupalisko Vincov les, s.r.o. (ICO: 36285226)
- **Zdielany podpisujuci** -- Viktor Janko podpisuje za 3 roznych dodavatelov

#### 2. LM1 invest s.r.o. (ICO: 46820591) -- 8 zltych stop, zmluva #12069043

Dohoda o skonceni najmu a uznani dlhu, suma 2 345,90 EUR. Klucove stopy:
- **Danovy dlznik FS** (dlh 941,43 EUR)
- **Dlznik Socialnej poistovne** (dlh 1 137,80 EUR)
- **Vymazany z DPH registra** (rok porusenia 2025, vymazany 03.03.2026)
- **Nesulad odvetvia** -- NACE: Poradenske cinnosti v podnikani, zmluva: prenajom
- **Zdielany podpisujuci** -- Mgr. Peter Kolek podpisuje za 8 roznych dodavatelov
- **Skryta entita je dodavatel** -- BYSPRAV, spol. s.r.o. Galanta (ICO: 36226599)

#### 3. Troy media s.r.o. (ICO: 36744824) -- sumovy outlier, zmluva #12070159

Zmluva o spolupraci pri vyrobe AVD, suma **1 108 632 EUR** -- 14,7x standardna odchylka pre kategoriu media/marketing (priemer 11 335 EUR). Dalsie stopy: skryte entity, zdielany podpisujuci (Mgr. Martina Flasikova za 51 dodavatelov).

#### 4. Gastrocenter s.r.o. (ICO: 53812930) -- 3 danger flags, zmluva #12058360

Zmluva o dielo, suma **53 254,54 EUR** pre Lienka DD, n.o. Klucove stopy:
- **Danovo nespolahlivy dodavatel**
- **Danovy dlznik FS** (dlh 17 053,49 EUR)
- **Dovody na zrusenie DPH** (rok porusenia 2023)

#### 5. SVS Nitra, s.r.o. (ICO: 35922737) -- zaporne imanie + mikro dodavatel, zmluva #12064598

Zmluva o dielo pre Mesto Trencianske Teplice, suma **287 558,49 EUR**. Klucove stopy:
- **Zaporne vlastne imanie** (-242 237 EUR)
- **Mikro dodavatel, velka zmluva** (0-1 zamestnancov)
- **Zrusena firma** podla RUZ

---

## Faza 2: Kriticka validacia

Kazdy nalez z Fazy 1 bol konfrontovany s nevinnym vysvetlenim. Uvadzam verdikt: **PREZILA** (stopa pretrvava), **CIASTOCNE** (oslabena, ale relevantnta), **NEPREZILA** (nevinne vysvetlenie je pravdepodobnejsie).

### Nalez 1: TOPZONE S.R.O. -- 9 zltych stop

| Stopa | Nevinne vysvetlenie | Verdikt |
|-------|---------------------|---------|
| Vymazany z DPH registra (2021) | Firma mohla ukoncit cinnost a teraz funguje bez DPH | **PREZILA** -- firma napriek tomu dostala statnu zmluvu na IT sluzby |
| Zaporne vlastne imanie (-95k) | Data su z roku 2018, firma mohla odvtedy zlepsit financie | **CIASTOCNE** -- stare data oslabuju signál, ale kombinacia s dalsimi stopami je vyznamna |
| Nesulad odvetvia (velkoobchod vs. IT) | Firma mohla rozsirit predmet podnikania | **PREZILA** -- velkoobchod a IT su velmi odlisne odvetvia, legitimne firmy si menia NACE |
| Pokuty zvyhodnuju dodavatela | V IT zmluvach byva asymetria benezna | **CIASTOCNE** -- caste, ale v kombinacii s ostatnymi stopami podozrive |
| Skryta entita (Vincov les) | Moze ist o subdodavatela alebo referenciu | **PREZILA** -- kupalisková firma ako skryta entita v IT zmluve je nelogicka |
| Zdielany podpisujuci (3 firmy) | Viktor Janko moze byt pravnik zastupujuci viacero firiem | **CIASTOCNE** -- 3 firmy su na hranici normalnosti |
| **Celkovy verdikt** | | **PREZILA** -- kumulacia 9 stop vcitane 3 danger je alarmujuca |

### Nalez 2: LM1 invest s.r.o. -- 8 zltych stop

| Stopa | Nevinne vysvetlenie | Verdikt |
|-------|---------------------|---------|
| Danovy dlznik + dlznik SP | Firma mohla mat docasne financne problemy | **PREZILA** -- dlhy su aktivne a zmluva je z marca 2026 |
| Vymazany z DPH (03.03.2026) | Administrativne konanie | **PREZILA** -- vymazanie nastalo presne v tyzdni zverejnenia zmluvy |
| Zdielany podpisujuci (8 firmiem) | Pravnik zastupujuci klientov | **PREZILA** -- 8 firmiem je vysoko nad normalom |
| BYSPRAV ako skryta entita | Spravca bytov referencovany v najomnej zmluve | **NEPREZILA** -- dohoda o ukonceni najmu logicky referencuje spravcu |
| **Celkovy verdikt** | | **CIASTOCNE** -- zmluva je na male ciastky (2 345 EUR) a ide o ukoncenie najmu; danger stopy su realne, ale riziko je nizke kvoli malej sume |

### Nalez 3: Troy media s.r.o. -- sumovy outlier 1 108 632 EUR

| Stopa | Nevinne vysvetlenie | Verdikt |
|-------|---------------------|---------|
| 14,7x stddev v media/marketing | Audiovizualne diela (AVD) su draha produkcia | **CIASTOCNE** -- produkcia filmov je objektívne draha, ale 1,1M EUR je mimo bezny rozsah |
| Zdielany podpisujuci (51 firmiem) | Mgr. Flasikova moze byt uradnicka na strane objednavatela podpisujuca za prijemcov | **NEPREZILA** -- 51 firiem naznacouje, ze ide o podpisovanie za statnu stranu, nie za dodavatelov |
| Skryte entity | Bezne v produkcnych zmluvach (koprodukcia) | **CIASTOCNE** -- normalny jav pre film/TV |
| **Celkovy verdikt** | | **CIASTOCNE** -- suma je vysoka, ale filmova/TV produkcia ma inherentne vysoke naklady; stojí za preverenie, ci bola sutaz |

### Nalez 4: Gastrocenter s.r.o. -- 3 danger flags, 53 254 EUR

| Stopa | Nevinne vysvetlenie | Verdikt |
|-------|---------------------|---------|
| Danovo nespolahlivy dodavatel | Mohlo ist o docasny stav | **PREZILA** -- status je aktivny v case uzavretia zmluvy |
| Danovy dlznik FS (17 053 EUR) | Splatkovy kalendar moze byt dohodnuty | **PREZILA** -- dlzoba je vyrazna a aktivna |
| Dovody na zrusenie DPH (2023) | Administrativne konanie ukoncene | **PREZILA** -- dovody su zverejnene, co znamena aktivny problem |
| **Celkovy verdikt** | | **PREZILA** -- trojnasobna danovo-financna stopa pri zmluve pre neziskovku (Lienka DD) je alarmujuca. Objednavatel je neziskova organizacia, co znizuje pravdepodobnost sofistikovanych due-diligence procesov. |

### Nalez 5: SVS Nitra, s.r.o. -- zaporne imanie + mikro + zrusena firma, 287 558 EUR

| Stopa | Nevinne vysvetlenie | Verdikt |
|-------|---------------------|---------|
| Zaporne vlastne imanie (-242k) | Data z 2018, firma mohla zlepsit financie | **CIASTOCNE** -- data su stare, ale suma je vysoka |
| Mikro dodavatel (0-1 zamestnancov) | Firma moze vyuzivat subdodavatelov | **PREZILA** -- 287k EUR zmluva o dielo pre firmu bez zamestnancov je podozriva |
| Zrusena firma | Firma uz neexistuje podla RUZ | **PREZILA** -- ak je firma zrusena, nemala by dostavat nove zmluvy |
| **Celkovy verdikt** | | **PREZILA** -- kombinacia zrusenej firmy s mikrovelikostou a velkym kontraktom je velmi podozriva. Trojita stopa preukazuje, ze mesto Trencianske Teplice uzavrelo zmluvu za takmer 288k EUR s firmou, ktora podla registra neexistuje a nema zamestnancov. |

---

## Dalsie vyznamne nalezy (overene)

### Delenie zakazky: DXC Technology (ICO: 35785306) + Ministerstvo obrany SR

- 19 objednavok z ramcovej dohody c. 2022/504 v roku 2026, celkovo **99 871 EUR**
- Vsetky objednavky su pod limitom priameho zadania
- **Verdikt: NEPREZILA** -- ide o objednavky z ramcovej dohody (RD), co je standardny mechanizmus verejneho obstaravania. Delenie je len opticky artefakt.

### Steeling, s.r.o. (ICO: 31720943) + Dopravny podnik Kosice

- 67 zmluv za 314 891 EUR v roku 2026 (januar--marec)
- **Verdikt: CIASTOCNE** -- vysoka frekvencia je neobvycajna, ale moze ist o ramcovu dohodu na pravidelne dodavky. Stoji za overenie, ci existuje suťaz.

### Sumove outlier: HOREZZA, a.s. (ICO: 36280127) -- 250 000 EUR

- Zmluva o vzajomnej spolupraci pri zabezpecovani podujati pre deti a mladez
- Kategória competition_olympiad: 15,9x stddev (priemer 2 108 EUR)
- Skryta entita je dodavatel (HOREZZA je aj v inych zmluvach)
- **Verdikt: PREZILA** -- 250k EUR na podujatia pre deti od Ministerstva obrany je sumovo neobvykle vysoka a kategoria nesedi. HOREZZA je hotelova spolocnost.

### Tesne pod EU limitom (threshold gaming)

| Dodavatel | Suma | Rozdiel od limitu |
|-----------|------|-------------------|
| CS, s.r.o. | 214 896,13 EUR | iba 104 EUR pod limitom |
| TERRATECHNIK spol. s r.o. | 213 122,54 EUR | 1 877 EUR pod limitom |
| TOPSTAV E&A s.r.o. | 210 177,58 EUR | 4 822 EUR pod limitom |
| MAHOLZ s.r.o. | 210 099,00 EUR | 4 901 EUR pod limitom |
| CSOB, a.s. | 210 000,00 EUR | 5 000 EUR pod limitom |

- **Verdikt: CIASTOCNE** -- CS, s.r.o. s rozdielom iba 104 EUR je vysoko podozrive a **PREZILA** validaciu. Ostatne su v sirsom pasme, kde moze ist o nahodu.

### Centrum zdielanych sluzieb BBSK, s.r.o. (ICO: 56931654) -- cerstve zalozena firma, 615 000 EUR

- Ramcova zmluva o poskyto\xadvani mandatnych sluzieb pre Banskobystricky samospravny kraj
- Firma zalozena 08.05.2025, 9 mesiacov pred zmluvou
- **Verdikt: NEPREZILA** -- ide o ucelovo zalozenu spolocnost samospravneho kraja na centralizaciu zdielanych sluzieb. Zalozenie VUC-kou je standardny postup.

### D3 Oscadnica--Cadca: 260,6 mil. EUR (zmluva #12068247)

- Najvacsia zmluva obdobia -- NFP pre Narodnu dialnicnu spolocnost
- 42x stddev pre kategoriu grant/subsidy
- **Verdikt: NEPREZILA** -- ide o standardny mechanizmus financovania dialnicneho projektu cez NFP. NDS je statna firma. Suma je vysoka, ale zodpoveda infrastrukturnemu projektu.

---

## Suhrn: Ktore nalezy prezili validaciu

| # | Dodavatel | ICO | Zmluva | Suma | Verdikt | Klucove stopy |
|---|-----------|-----|--------|------|---------|---------------|
| 1 | TOPZONE S.R.O. | 36275000 | #12048188 | 0 EUR | **PREZILA** | 9 stop: vymazana DPH, zaporne imanie, NACE nesulad, skryta entita kupalisko |
| 2 | Gastrocenter s.r.o. | 53812930 | #12058360 | 53 254 EUR | **PREZILA** | 3 danger: danovy dlznik (17k), nespolahlivy, dovody na zrusenie DPH |
| 3 | SVS Nitra, s.r.o. | 35922737 | #12064598 | 287 558 EUR | **PREZILA** | Zrusena firma, zaporne imanie (-242k), mikro dodavatel |
| 4 | HOREZZA, a.s. | 36280127 | #12061441 | 250 000 EUR | **PREZILA** | Hotelova firma, 250k na detske podujatia od MO SR, 15,9x outlier |
| 5 | CS, s.r.o. | -- | #12053309 | 214 896 EUR | **PREZILA** | Iba 104 EUR pod EU limitom sutaze |
| 6 | Troy media s.r.o. | 36744824 | #12070159 | 1 108 632 EUR | **CIASTOCNE** | 14,7x outlier v media/marketing, ale filmova produkcia je draha |
| 7 | LM1 invest s.r.o. | 46820591 | #12069043 | 2 345 EUR | **CIASTOCNE** | 8 stop, ale mala suma a ukoncenie najmu |
| 8 | Steeling, s.r.o. | 31720943 | -- | 314 891 EUR (67 zmluv) | **CIASTOCNE** | 67 zmluv za 3 mesiace s DPMK |

**Neprezili:** DXC Technology (ramcova dohoda), Centrum zdielanych sluzieb BBSK (VUC-ka), D3 dialnica (standardny NFP).

---

## Odporucania pre dalsie kroky

1. **SVS Nitra** -- najvyssie riziko: overit, ci firma realne existuje a ci ma kapacitu na dielo za 288k EUR
2. **TOPZONE** -- overit aktualny stav firmy na FinStat, ci funguje, a preco ju stat kontrahuje
3. **Gastrocenter** -- overit, ci neziskovka Lienka DD mala inu moznost (due diligence)
4. **HOREZZA + MO SR** -- overit ucel a ci prebehlo verejne obstaravanie (UVO)
5. **CS, s.r.o.** -- overit, ci suma nebola umyselne stanovena tesne pod limit na vyhnutie sa sutazi
