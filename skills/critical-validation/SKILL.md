---
name: critical-validation
description: Validate and classify investigative findings from CRZ contract analysis before they are reported. Challenges each finding against data artifacts, innocent explanations, and common false-positive patterns. The "Sulc Matej lesson" — always verify before you publish. Use this skill after sql-analytics or any query that surfaces anomalies, whenever findings need validation before reporting, when the user asks to verify or double-check suspicious contracts, or when the crz-investigate orchestrator enters Phase 2. If you have raw findings from CRZ queries, run them through this skill before presenting conclusions.
---

# Critical Validation of CRZ Findings

**Every finding MUST pass through this critic before being reported.**

The Sulc Matej lesson: a "1,676 contract splitting" finding turned out to be
910 different freelancers grouped together by a NULL ICO. Always challenge
your findings.

## Input

A list of findings from sql-analytics or other CRZ queries. Each finding
should have: finding_name, category, severity, key_data (ICOs, amounts,
contract IDs, dates), and raw_query_result or summary.

If the input is a sql-analytics report, use the Zhrnutie najdov table.

## Data source

**Primary:** FastAPI + DuckDB at `https://zmluvy.zltastopa.sk` — use for
follow-up validation queries:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+...&_shape=array
```

**Note:** Backend uses DuckDB syntax (see sql-analytics skill for key differences).

## Execution strategy: Two-pass validation

Speed matters — validate all findings efficiently using two passes. The key
insight is that many findings can be dismissed without any database queries
at all. Query only what survives triage.

### Pass 1 — TRIAGE (no queries needed)

Scan ALL findings against the known innocent patterns below. Any finding that
clearly matches a pattern gets immediately DISMISSED without wasting a query.
This typically eliminates 30-50% of findings upfront.

**Instant-dismiss patterns** — recognize and dismiss on sight:

| Pattern | Why it's innocent |
|---|---|
| **Ministry → university dotacie** | Normal annual budget allocations, not procurement |
| **SFRB (housing fund) contracts** | Large housing development loans, standard state mechanism |
| **NDS highway contracts** | Multi-hundred-million infrastructure is expected |
| **Freelancer micro-contracts** | Broadcasters (STVR), research agencies (APVV) pay many individuals |
| **VUB/Tatra banka/SLSP loans** | Banks providing municipal credit lines — round amounts normal |
| **Erasmus/EU program grants** | Long publication delays are standard for EU co-funded projects |
| **State org negative equity** | Hospitals, rescue services, prispevkove organizacie often have negative equity by design |
| **January/December volume spikes** | Budget cycle: allocations in January, year-end spending in December |
| **Fond na podporu vzdelavania** | Student loan fund — many small contracts to individuals is normal |
| **NASES ↔ MIRRI symmetric transfers** | IT infrastructure budget transfers between related state bodies |
| **Environmentalny fond / Modernizacny fond dotacie** | EU fund distributions to state enterprises — round amounts standard |
| **State fund annual allocations** (Fond na podporu sportu, etc.) | Statutory budget transfers with naturally round amounts |

For each triage dismissal, note which pattern matched. These go directly into
the DISMISSED table in the output — no further validation needed.

Also during triage, flag findings that smell like **data artifacts**:
- Supplier with no ICO + suspiciously high contract count → likely NULL ICO grouping
- Late publication with days_late > 100,000 → bad date (before year 2000)
- Identical amounts from multiple suppliers to same buyer → check for duplicates

### Pass 2 — VALIDATE (queries, run in parallel)

For findings that survive triage, run validation queries. The goal is to
minimize round-trips by batching and parallelizing.

**Step A: Batch register lookup (one query for all surviving ICOs)**

Collect all ICOs from surviving findings and check all registers at once:

```sql
-- Run as ONE query — checks all registers for all ICOs in one shot
SELECT 'vszp' as register, ico, dlh as value
FROM vszp_debtors WHERE ico IN ('{ico1}','{ico2}','{ico3}')
UNION ALL
SELECT 'socpoist', ico, dlh FROM socpoist_debtors WHERE ico IN ('{ico1}','{ico2}','{ico3}')
UNION ALL
SELECT 'fs', ico, dlh FROM fs_tax_debtors WHERE ico IN ('{ico1}','{ico2}','{ico3}')
UNION ALL
SELECT 'ruz', ico, CAST(vlastne_imanie AS TEXT) FROM ruz_equity WHERE ico IN ('{ico1}','{ico2}','{ico3}')
```

**Step B: Finding-specific queries (run in parallel)**

Launch all finding-specific validation queries in the same turn — don't wait
for one to finish before starting the next. Each finding type needs:

| Finding type | Validation query | Innocent if... |
|---|---|---|
| **Contract splitting / NULL ICO** | `SELECT DISTINCT dodavatel FROM zmluvy WHERE objednavatel_ico='{ico}' AND (dodavatel_ico IS NULL OR dodavatel_ico='') LIMIT 50` | Many distinct names = freelancers, not splitting |
| **Weekend publishing** | Count contracts on that date + check if end-of-month batch | Published with many others on last day of month |
| **Late publication** | Check nazov_zmluvy for EU/Erasmus/addendum keywords | Erasmus/EU grants, framework addenda |
| **Round amounts** | Check nazov_zmluvy for dotacia/grant/uver/prispevok | Grants, subsidies, loans have naturally round amounts |
| **No ICO, high value** | Check if dodavatel name suggests foreign entity or s.r.o./a.s. | Foreign entities lack Slovak ICO; Slovak s.r.o. without ICO is suspicious |
| **Negative equity** | Check ruz_entities for legal_form (prispevkova org = state) | State institutions can operate with negative equity |
| **Dormant firm** | `SELECT max(datum_zverejnenia) FROM zmluvy WHERE dodavatel_ico='{ico}' AND datum_zverejnenia < '{date_from}'` | Seasonal activity or name/ICO change |
| **Duplicate amounts** | Check if same contract uploaded by both parties | CRZ often has buyer + supplier uploads |

**Step C: Classify each surviving finding**

With register data and query results in hand, classify:

#### CONFIRMED
The anomaly survives scrutiny. Explain **why innocent explanations don't
apply**:
- "This is NOT a standard dotacia because the recipient is a private company"
- "The negative equity is for a PRIVATE firm, not a state institution"
- "Despite being a defense contract, the triple debtor status is a red flag"

#### INCONCLUSIVE
Needs external enrichment. Flag with what was checked, why it's unclear,
and what's needed next (FinStat, RPVS, foaf.sk, UVO, PDF review).

## Output template

```markdown
# Kriticka validacia: {date_range}

## Sumar validacie
- Pocet najdov na vstupe: {N}
- CONFIRMED: {X}
- DISMISSED: {Y}
- INCONCLUSIVE: {Z}

---

## CONFIRMED najdy

### 1. {finding_headline} — {severity}

**Povodny najd:** {brief description from sql-analytics}

**Validacne kroky:**
1. {what query/check was run}
2. {what the result showed}

**Preco to nie je falesny pozitiv:**
- {specific reason innocent explanation doesn't apply}
- {evidence from validation query}

**Klucove cisla:** {contract IDs, amounts, ICOs}

---

[...repeat for each CONFIRMED finding...]

---

## INCONCLUSIVE najdy

### {N}. {finding_headline}

**Co sme overili:** {validation steps taken}
**Preco to zostava nejasne:** {what we don't know}
**Dalsie kroky:** {specific next steps — FinStat, RPVS, foaf.sk, PDF review}

---

## Preverene a vylucene (DISMISSED)

| # | Najd | Dovod vylucenia |
|---|------|-----------------|
| 1 | {finding} | {innocent pattern or validation result} |
| 2 | ... | ... |

---

**Validacia ukoncena.** {X} najdov potvrdene, {Y} vylucene, {Z} vyzaduje
dalsie overenie.
```

## Example

**Input finding:** "Sulc Matej — 659 zmluv so STVR za 747K EUR, potencialne
delenie zakazky"

**Pass 1 triage:** Flagged as potential data artifact (high count + NULL ICO
pattern). Also matches "Freelancer micro-contracts for broadcasters" but
the count is extreme — send to Pass 2 for verification.

**Pass 2 validation:**
```sql
SELECT count(DISTINCT dodavatel) as distinct_suppliers
FROM zmluvy WHERE objednavatel LIKE '%STVR%'
  AND (dodavatel_ico IS NULL OR dodavatel_ico = '')
```
Result: 967 distinct freelancers. Sulc Matej has only 1 contract for 24K EUR.

**Classification:** DISMISSED — "Sulc Matej's 659 contracts was a NULL ICO
grouping artifact. STVR has 967 distinct freelancers without ICO. Actual
data: 1 contract, 24,000 EUR — consistent with broadcaster freelance work."
