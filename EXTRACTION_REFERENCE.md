# CRZ Contract PDF Extraction Reference

What to extract from Slovak government contract PDFs, based on analysis of
200 contracts from the Central Register of Contracts (March 2026).

## Data pipeline

```
CRZ XML daily export
  → parse structured metadata (load_crz.py)
  → download PDF attachments
  → pdftotext for native text (80% success rate)
  → OCR (Tesseract + Slovak) for scanned PDFs (20%)
  → LLM extraction per text file
  → enriched SQLite database
```

---

## Extraction fields, ranked by journalist impact

### Tier 1: Directly serves 360tka + Sme.sk briefs

#### 1. Service category classification (360tka priority)

**Problem**: 10%+ of contracts have generic titles ("Zmluva o dielo",
"Zmluva o poskytovaní služieb") that hide what's actually being bought.

**Proposed taxonomy** (validated against 200 contracts):

| Category | Slovak keywords | Prevalence |
|----------|----------------|------------|
| `construction_renovation` | stavebné práce, rekonštrukcia, zateplenie | ~5/20 generic |
| `software_it` | softvér, licencia, IT, počítačová sieť, WinPam | ~4/20 generic |
| `cultural_event_production` | porota, moderátor, vystúpenie, výstava | ~9/20 generic |
| `utilities` | dodávka tepla, voda, plyn, elektrina | common |
| `insurance` | poistná zmluva, poistenie | common |
| `professional_consulting` | poradenstvo, konzultácie, audit | 7+37/200 |
| `media_marketing` | reklama, propagácia, marketing, PR | 36/200 |
| `grant_subsidy` | dotácia, grant, NFP, príspevok | 30/200 |
| `property_lease` | nájom, prenájom, nebytový priestor | 77/200 |
| `cemetery` | hrobové miesto, pohrebisko | frequent |
| `asset_transfer` | kúpna zmluva, darovacia, prevod | common |
| `employment_social` | dohoda §59, §60, SZČO, sociálne | common |
| `legal_services` | advokát, právne služby | 3/200 |
| `cleaning_facility` | upratovanie, čistiace, hygienické | 13/200 |
| `digital_certification` | elektronický podpis, certifikát, pečať | rare |
| `hr_payroll_outsourcing` | mzdová agenda, personalistika | rare |
| `other` | | |

**Concrete mismatches found**:
- "Zmluva o dielo 2026/04" → actually jury work for AMFO photography competition (€180)
- "Zmluva o dielo a licenčná zmluva" → actually evaluation reports for doctoral programs (€400)
- "Zmluva o dielo" → actually moderating a dance event (€200)
- "Príkazná zmluva" → actually author talk in a library (€112)
- "Zmluva o poskytovaní služieb" → actually Lindström mat rental/laundry service
- "Rámcová zmluva o poskytovaní služieb" → actually NFC card system for Bratislava

**Extraction approach**: Read the `Predmet zmluvy` / `Článok I` section
(first ~1500 chars after the parties block) and classify.

#### 2. Hidden entities (Sme.sk priority)

**Problem**: XML exports only list 2 parties per contract. But PDFs contain
additional firms: consortium members, subcontractors, authorized
representatives, managing operators, predecessor entities.

**Findings across 200 texts**:
- `subdodávateľ`: 21/200 mention subcontracting
- `splnomocnenec` / delegation: 21/200
- `v zastúpení`: 45/200
- `konzorcium`: 1/200 (EDIH Cassovium digital innovation hub)
- Literal `člen konzorcia`: 0/200

**Concrete hidden entities found**:
- `JUDr. Ivana Hegera` (IČO 42002044) — authorized representative for
  cadastral proceedings, not a contracting party (6571550.txt)
- `Komunálne služby Mesta Ružomberok` (IČO 52113043) — acts as cemetery
  manager on behalf of Mesto Ružomberok (6580757.txt)
- `Technické služby Ružomberok a.s.` (IČO 36391301) — predecessor operator
  whose rights were transferred (6580757.txt)
- `ByPo spol. s r.o.` (IČO 31579175) — property management company acting
  under mandate for Mesto Ružomberok (6572807.txt)
- `Rodičovské združenie pri ZŠ s MŠ v Malženiciach` — signature mismatch
  with header parties (6576743.txt)
- `Košice IT Valley z.p.o.` (IČO 35578041) — EDIH Cassovium consortium
  member, actual service provider (6570857.txt)
- `Základná škola Janka Kráľa` (IČO 37864521) — co-user of heating
  service, affects cost allocation (6573010.txt)

**Extraction approach**:
1. Extract all IČO patterns + nearby org names from full text
2. Diff against known parties from XML metadata
3. Classify role: `authorized_representative`, `manager_operator`,
   `previous_operator`, `co_user`, `consortium_member`, `subcontractor`,
   `associated_entity`
4. Output: `firm_name, ICO, role, zmluva_id, crz_url, snippet`

#### 3. Penalty & termination asymmetry

**Problem**: Public contracts often have one-sided penalty structures where
only the supplier/recipient pays penalties, while the state retains
unilateral termination rights.

**Findings across 200 texts**:
- 74/200 mention sanctions/penalties
- 81/200 mention withdrawal (odstúpenie)
- 68/200 mention notice-based termination (výpoveď)
- Only 27 have actual payable bilateral or one-sided penalty clauses

**Most asymmetric contracts found**:

| Contract | Supplier penalty | Buyer penalty | Asymmetry |
|----------|-----------------|---------------|-----------|
| Bratislava NFC cards (6568810) | €5,000/breach + pass-through fines | None | Extreme |
| School energy retrofit (6570640) | €2,000 site, €1,000/day docs, 50% subcontracting | Late-payment interest only | Strong |
| Agrokomplex fair cooperation (6568639) | Pass-through public fines | None; only Agrokomplex can terminate | Strong |
| Construction works (6535700) | 1%/day delay | 0.02%/day late payment | 50:1 ratio |
| Telecom service (6575187) | None visible | Remaining term value on early exit | Inverted |
| Recovery Plan grants (6569336, 6575318, 6577477, 6578007) | €50/day for reporting breaches | None | Systematic |
| SLOVGRAM copyright (6568076) | N/A | 10% fee + lost discounts on late payment | One-sided |

**Balanced counterexample**: Cleaning contract (6557968) — buyer pays 0.01%/day
late-payment interest, supplier pays 0.05% for service failures, mutual
termination on 3 months' notice.

**Extraction approach**:
- Extract penalty clauses: `who_pays`, `trigger`, `amount_or_rate`
- Extract termination modes: `who_can_terminate`, `notice_period`, `cause_required`
- Compute asymmetry score

### Tier 2: Systemic investigation enablers

#### 4. Public procurement trail

- 37/200 reference ÚVO (procurement office)
- 12/200 mention verejné obstarávanie
- 23/200 mention tender/súťaž

**Extract**: procurement method, reference number, number of bidders,
whether direct award. Cross-reference with UVO portal.

#### 5. EU funds & state aid tracking

- 18/200 mention de minimis / state aid schemes
- 7/200 reference Plán obnovy (Recovery & Resilience Plan)
- 6/200 are Erasmus / EU grants
- 1/200 references EDIH (European Digital Innovation Hub)

**Extract**: funding source, aid scheme reference, total project value,
grant amount, co-financing ratio, clawback conditions.

**Interesting finds**:
- Multiple Recovery Plan contracts with identical penalty templates
  (€50/day for reporting failures)
- EDIH Cassovium consortium delivering digital transformation services
  through intermediary structure

#### 6. Intermediaries & commissions

- 24/200 mention sprostredkovateľ (intermediary/broker)
- 3/200 mention provízia (commission)

**Extract**: intermediary name, service brokered, commission rate/amount.

#### 7. Automatic renewal / zombie contracts

- 6/200 have automatic renewal clauses
- Many "na dobu neurčitú" (indefinite term) contracts

**Extract**: `auto_renewal: boolean`, `renewal_notice_period`,
`original_start_date`.

#### 8. Bank account network (IBAN graph)

- 128/200 contain IBAN numbers
- In our sample: no cross-org IBAN sharing detected (would need full
  11K-contract corpus for meaningful signal)

**Extract at scale**: Build IBAN→IČO mapping across all contracts. Flag
cases where different organizations share the same bank account.

### Tier 3: Niche but high-value

#### 9. Pharmaceutical / clinical trials

- Pfizer clinical trial agreement found (6578512.txt)
- Bilingual EN/SK, protocol number C5851005
- Per-patient payment structure, investigator + hospital as co-signatories

**Extract**: drug company, protocol number, payment per patient,
principal investigator, hospital/site.

#### 10. Conflict of interest declarations

- 8/200 contain conflict of interest language

**Extract**: `conflict_of_interest_clause: boolean`, declaration text.

#### 11. GDPR / personal data processing

- 78/200 mention GDPR or personal data processing

**Extract**: `gdpr_clause_present: boolean`, legal basis, data categories.

#### 12. Inflation indexation

- 9/200 mention inflation/indexation/valorization clauses

**Extract**: `price_indexation: boolean`, index reference, mechanism.

#### 13. Bezodplatné (gratuitous) transfers

- 22/200 involve free-of-charge transactions

**Extract**: what is given for free, to whom, estimated value if stated.

---

## Signatory network findings

No red flags in 200-contract sample (same person signing for different
IČOs, or signing both sides). Repeated institutional signers are normal.

Notable delegated-authority patterns worth flagging at scale:
- `na základe poverenia` (by authorization)
- `na základe plnomocenstva` (by power of attorney)
- `v zastúpení správcom` (represented by manager)

---

## OCR gap

50/250 PDFs (20%) failed `pdftotext` extraction — these are scanned
documents. For production, add Tesseract OCR with Slovak language pack:

```bash
tesseract input.pdf output -l slk --psm 1
```

---

## Recommended extraction schema (JSON)

```json
{
  "zmluva_id": 12054906,
  "service_category": "cultural_event_production",
  "service_category_confidence": 0.92,
  "actual_subject": "Členka poroty a vedenie rozborového seminára AMFO 2026",

  "hidden_entities": [
    {
      "name": "Komunálne služby Mesta Ružomberok",
      "ico": "52113043",
      "role": "manager_operator",
      "snippet": "V zastúpení správcom, príspevkovou organizáciou..."
    }
  ],

  "penalties": [
    {
      "payer": "supplier",
      "trigger": "delay in delivery",
      "amount": "1% of contract price per day",
      "source_line": 403
    }
  ],
  "penalty_asymmetry": "strong_buyer_advantage",

  "termination": {
    "buyer_can_terminate_without_cause": true,
    "supplier_can_terminate_without_cause": false,
    "notice_period": "1 month",
    "withdrawal_for_breach": "buyer only"
  },

  "procurement": {
    "method": "public_tender",
    "uvo_reference": "https://www.uvo.gov.sk/...",
    "num_bidders": null
  },

  "funding_source": {
    "type": "eu_recovery_plan",
    "scheme_reference": "Schéma DM - 08/2024",
    "grant_amount": 150000,
    "co_financing_ratio": 0.15
  },

  "signatories": [
    {
      "party": "buyer",
      "name": "Ing. Michal Fiala",
      "title": "generálny riaditeľ",
      "authority": "statutory"
    }
  ],

  "bank_accounts": [
    {
      "party": "supplier",
      "iban": "SK22 8180 0000 0070 0053 0134",
      "bank": "Štátna pokladnica"
    }
  ],

  "duration": {
    "type": "fixed_term",
    "start": "2026-01-01",
    "end": "2026-12-31",
    "auto_renewal": false
  },

  "gdpr_clause": true,
  "conflict_of_interest_clause": false,
  "price_indexation": false,
  "bezodplatne": false
}
```

---

## Pattern prevalence summary (200 contracts)

| Pattern | Count | % |
|---------|-------|---|
| Predmet zmluvy section | 160 | 80% |
| IČO numbers in text | 180 | 90% |
| IBAN numbers | 128 | 64% |
| Penalties / sanctions | 74 | 37% |
| Withdrawal clauses | 81 | 41% |
| Notice-based termination | 68 | 34% |
| GDPR / personal data | 78 | 39% |
| v zastúpení (delegation) | 45 | 23% |
| Audit mentions | 37 | 19% |
| ÚVO / procurement office | 37 | 19% |
| Marketing / advertising | 36 | 19% |
| Dotácia / grants | 30 | 15% |
| Duševné vlastníctvo / copyright | 29 | 15% |
| Sprostredkovateľ / intermediary | 24 | 12% |
| Bezodplatné / gratuitous | 22 | 11% |
| Subdodávateľ / subcontracting | 21 | 11% |
| Splnomocnenec / proxy | 21 | 11% |
| De minimis / state aid | 18 | 9% |
| Cestovné náhrady / travel | 17 | 9% |
| Konkurz / bankruptcy | 14 | 7% |
| Upratovanie / cleaning | 13 | 7% |
| Verejné obstarávanie | 12 | 6% |
| Zmluvná pokuta (explicit) | 12 | 6% |
| Zábezpeka / deposit | 12 | 6% |
| Inflácia / indexation | 9 | 5% |
| Splátky / installments | 9 | 5% |
| Konflikt záujmov | 8 | 4% |
| Environmentálne | 8 | 4% |
| Plán obnovy | 7 | 4% |
| Poradenstvo / consulting | 7 | 4% |
| Erasmus / EU grants | 6 | 3% |
| Pharma / clinical | 6 | 3% |
| Auto renewal | 6 | 3% |
| Cenová ponuka / price quote | 6 | 2% |
| Sponzoring | 4 | 2% |
| Exkluzivita / exclusivity | 4 | 2% |
| Advokát / legal services | 3 | 2% |
| Provízia / commission | 3 | 2% |
| Konzorcium | 1 | 0.5% |

---

---

## Deep dive findings

### A. EU Funds & State Aid (subagent analysis)

~50 contracts (25%) reference EU funding, state aid, grants, or subsidies.

**Funding programs found:**

| Program | Count | Largest grant |
|---------|-------|---------------|
| Recovery & Resilience Facility (Plán obnovy) | 4 direct + EDIH | €316,405 (Obec Bernolákovo) |
| Program Slovensko 2021-2027 / EFRR | 3 | **€773,114** (Obec Doľany — largest in corpus) |
| De minimis employment schemes | 6+ | €51,001 |
| Erasmus+ | 2 | €2,852 |
| ESF+ (European Social Fund Plus) | 2 | €162,867 |
| Audiovizuálny fond / GBER state aid | 2 | €15,000 |
| Visegrad Fund | 1 | €2,000 |
| APVV bilateral research | 1 | €4,800 |

**Key insight — EDIH Cassovium (6570857.txt)**: Most complex funding in corpus.
50% from European Commission direct grant + 50% from Slovak Recovery Plan.
Only the Recovery Plan portion counts as de minimis. Two EU-level sources in
one service delivery contract.

**All Recovery Plan energy contracts are 100% funded** — zero co-financing
from recipients. Unusual generosity reflecting the emergency nature of
RePower EU.

**Anti-fraud mechanisms**: ARACHNE anti-fraud tool integration in NFP
contracts, OLAF + European Prosecutor access rights, 100% financial
correction for proven conflicts of interest affecting procurement outcomes.

### B. Unusual & Investigatively Valuable Contracts (subagent analysis)

#### Pfizer clinical trial — the crown jewel

**File:** 6578512.txt (6,007 lines / 115 pages, bilingual EN/SK)

- **Drug:** PF-08046054/SGN-PDL1V (antibody-drug conjugate targeting PD-L1)
- **Study:** Phase 3, non-small-cell lung cancer (NSCLC)
- **Per-patient payment:** €4,860 (Arm A) to €7,800 (combined)
- **Investigator:** MUDr. Zuzana Švihelová Lišková, Nemocnica Ružinov
- **Institution:** Univerzitná nemocnica Bratislava
- CRZ declared amount (€7,800) = one patient; actual could be multiples
- Pfizer retains exclusive ownership of all study data and biological samples
- Contains anti-bribery provisions (Attachment D), EU data protection clauses

#### Political signatures

- **Rudolf Huliak** (Minister of Tourism/Sport) signed the €160,000
  Olympic funding contract (6580078.txt)
- **Martina Šimkovičová** (Minister of Culture) signed a lease
  termination (6569603.txt)

#### FinStat data access — state paying for its own data

Ministry of Foreign Affairs pays **FinStat** €4,120.50/year for access to
company financial data largely derived from public registers (6581120.txt).
Question: why does the state pay for repackaged access to its own data?

#### Vendor lock-in: DIVES software auto-renewal

DIVES (Ministry of Interior subsidiary) licenses to schools/social services
auto-renew annually unless explicitly cancelled (6575376.txt, 6580286.txt).
Classic vendor lock-in from a government-owned IT supplier.

#### SPP gas zombie clause

Fixed-term gas contracts automatically convert to indefinite unless customer
sends written objection 1-2 months before expiry (6568321.txt). Opt-out
mechanism benefiting the monopoly supplier.

#### Notable oddities

- **€40 for a TV appearance**: STVR pays €40 for one appearance on "Dámsky
  klub" — reveals economics of daytime TV (6576038.txt)
- **€1 symbolic barter**: Agrokomplex rents 9m² for €1 in exchange for
  moderation of "Poľovník a včelár 2026" opening (6568639.txt)
- **€114,000 fire truck donation**: Ministry of Interior donates surplus
  2020 IVECO 4x4 to Obec Polianka (6580877.txt)
- **Dragon exhibition**: Hrad Beckov pays Czech artist €5,744 for dragon
  sculptures — named dragons include Swan, Maja, Agatha (6579951.txt)
- **Gambling regulator + university MOU**: Non-binding memorandum on
  teaching gambling addiction prevention (6573548.txt)
- **Visegrad scholarship**: Fully English contract, UMB pays Georgian
  scholar €2,000 with zero financial reporting required (6581001.txt)

---

## Source files

- `load_crz.py` — XML parser with rezort mapping, incremental upsert
- `download_sample_pdfs.py` — PDF downloader from CRZ attachments
- `pdf_to_text.py` — pdftotext batch converter with manifest
- `data/texts/manifest.csv` — mapping of PDF→contract metadata
- `data/texts/*.txt` — 200 extracted contract texts
- `crz.db` — SQLite database with 10,884 contracts, 11,287 attachments,
  97 rezort mappings

## Journalist contacts

- **360tka** (Michal Kovačič, Barbora Šišoláková): auto-classify service
  types, search without opening PDFs
- **Sme.sk**: extract hidden firms (consortium members, subcontractors)
  with IČO, link to contract
