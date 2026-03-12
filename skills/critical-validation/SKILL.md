---
name: critical-validation
description: Validate and classify investigative findings from CRZ contract analysis. Challenge each finding against data artifacts and innocent explanations before reporting. The "Sulc Matej lesson" — always verify before you publish. Use after sql-analytics or any query that surfaces anomalies.
---

# Critical Validation of CRZ Findings

**Every finding MUST pass through this critic before being reported.**

The Sulc Matej lesson: a "1,676 contract splitting" finding turned out to be
910 different freelancers grouped together by a NULL ICO. Always challenge
your findings.

## Step 1: Check for data artifacts

For each finding, verify it's not a data quality issue:

**NULL/empty ICO grouping:**
If a finding involves suppliers without ICO, re-query with
`GROUP BY COALESCE(dodavatel_ico, dodavatel)` or `GROUP BY dodavatel`
to check if it's actually multiple distinct entities collapsed into one row.

**Duplicate contract entries:**
Check if the same contract appears twice (same `nazov_zmluvy`, `suma`,
`datum_podpisu` but different `id`) — CRZ often has both buyer and supplier uploads.

**Nonsensical dates:**
Filter out `datum_podpisu` before year 2000 (data entry errors like 0202-02-19).

## Step 2: Check for innocent explanations

Run a follow-up query for each flagged finding:

| Finding type | Validation query | Innocent if... |
|---|---|---|
| **Contract splitting** | `SELECT DISTINCT dodavatel FROM zmluvy WHERE objednavatel_ico = '{ico}' AND (dodavatel_ico IS NULL OR dodavatel_ico = '') LIMIT 50` | Many distinct names = freelancers/individuals, not splitting |
| **Weekend publishing** | Check if `datum_zverejnenia` is end-of-month | Published on last day of month in a batch with many others |
| **Late publication** | Check if it's an EU/Erasmus grant or addendum to old contract | Erasmus/EU grants, framework addenda, multi-year projects |
| **Round amounts** | Check `nazov_zmluvy` — grants, dotacie, uvery are naturally round | Grants, subsidies, loans, framework budget ceilings |
| **Threshold gaming** | Compare ratio to overall distribution in nearby bands | Similar density across 205-210K and 210-215K = no gaming |
| **No ICO, high value** | Check if supplier is foreign, individual, or consortium | Foreign entities, natural persons, state bodies lack Slovak ICO |
| **Supplier concentration** | Check if buyer distributes to subordinate orgs | State budget distribution (dotacie) to subordinate institutions |

## Step 3: Recognize common innocent patterns

These are NOT suspicious — recognize and dismiss them:

| Pattern | Why it's innocent |
|---|---|
| **Ministry → university dotacie** | Normal annual budget allocations, not procurement |
| **SFRB (housing fund) contracts** | Large housing development loans |
| **NDS highway contracts** | Multi-hundred-million infrastructure is expected |
| **Freelancer micro-contracts** | Broadcasters, research agencies pay many individuals |
| **VUB/Tatra banka/SLSP loans** | Banks providing municipal credit lines — round amounts normal |
| **Erasmus/EU program grants** | Long publication delays are standard for EU co-funded projects |

## Step 4: Classify each finding

Assign one of three classifications:

### CONFIRMED
The anomaly survives scrutiny. Include in report with explanation of **why
innocent explanations don't apply**. Be specific:
- "This is NOT a standard ministry-to-university dotacia because..."
- "Unlike typical freelancer micro-contracts, this pattern shows..."

### DISMISSED
Innocent explanation found. Exclude from report or mention briefly in an
"Investigated & Cleared" section. This builds trust and shows thoroughness.
Example: "Contract splitting at RTVS: appeared as 1,676 contracts to one
supplier, but validation revealed 910 distinct freelance contributors —
normal broadcaster operations."

### INCONCLUSIVE
Needs enrichment or manual review. Flag with:
- What we checked
- Why it remains unclear
- What additional data is needed (FinStat, RPVS, foaf.sk, PDF review)

## Output

A classified list of findings:
- Each finding labeled CONFIRMED / DISMISSED / INCONCLUSIVE
- For CONFIRMED: why innocent explanations don't apply
- For DISMISSED: which innocent pattern matched
- For INCONCLUSIVE: what next steps would resolve it
