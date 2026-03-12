---
name: crz-investigate
description: Broad investigative scan of Slovak government contracts from CRZ. Runs SQL analytics, validates findings, enriches suppliers via FinStat, and optionally traces ownership via RPVS and foaf.sk. Produces publishable findings in Slovak. Use when asked to investigate, analyze, audit, or find zlte stopy in CRZ contracts for a time period.
---

# CRZ Investigative Analysis

Perform investigative journalism-grade analysis of Slovak government contracts
from the Central Register of Contracts (CRZ). This is the **broad scan** —
it sweeps a time period to surface leads.

For deep investigation of a specific company, use **crz-deep-investigate** instead.

## Data source

**Primary:** Datasette at `https://zmluvy.zltastopa.sk/data/crz` — supports
arbitrary SQL. Query via JSON API:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+...&_shape=array
```

**Local fallback:** `crz.db` in the repo root. Use only when Datasette is
unreachable. Full schema: **[docs/data/](docs/data/README.md)**

## Investigation pipeline

Execute these phases in order. Each builds on the previous.

### Phase 1: SQL Analytics

Use the **[sql-analytics](../sql-analytics/SKILL.md)** skill.

Run all 17 standard queries for the given date range. Group results by category:
money flow, procurement manipulation, timing anomalies, phantom suppliers,
extraction-based checks, and debtor cross-checks.

### Phase 2: Critical Validation (mandatory)

Use the **[critical-validation](../critical-validation/SKILL.md)** skill.

**Every finding from Phase 1 MUST pass through validation.** Challenge each
against data artifacts and innocent explanations. Classify as CONFIRMED,
DISMISSED, or INCONCLUSIVE.

### Phase 3: Financial Enrichment

Use the **[finstat-enrichment](../finstat-enrichment/SKILL.md)** skill.

Enrich CONFIRMED and INCONCLUSIVE suppliers with FinStat financial data.
Evaluate financial zlte stopy (revenue mismatch, negative equity, tax status).

### Phase 4: Procurement Verification

Use the **[uvo-procurement](../uvo-procurement/SKILL.md)** skill.

For CONFIRMED findings with large contracts (>50K), check whether proper
procurement was followed:
- Does a UVO record exist? (check `uvo_url` field first, then search UVO)
- How many bidders competed?
- Was it direct negotiation (priame rokovacie konanie)?
- Does the CRZ price match the UVO winning price?

### Phase 5: Ownership & Network (for promising leads)

For CONFIRMED findings that warrant deeper investigation:

1. Use **[rpvs-lookup](../rpvs-lookup/SKILL.md)** to check beneficial ownership
2. Use **[foaf-network](../foaf-network/SKILL.md)** to map corporate connections

Cross-reference UBOs across suppliers — same person controlling multiple
companies receiving contracts from the same buyer is a strong signal.

### Additional cross-checks

For specific suppliers, also:
- Cross-reference with `tax_reliability`: `JOIN tax_reliability t ON replace(z.dodavatel_ico, ' ', '') = t.ico WHERE t.status = 'menej spolahlivy'`
- Check all contracts for a flagged supplier: `WHERE replace(dodavatel_ico, ' ', '') = '{ico}' ORDER BY datum_zverejnenia`
- Review extraction data: `SELECT extraction_json FROM extractions WHERE zmluva_id = {id}`
- Verify on CRZ: `https://www.crz.gov.sk/zmluva/{id}/`
- Check FinStat: `https://finstat.sk/{ico}`
- Check UVO: search by ICO or contract name on `uvo.gov.sk`

## Output format

Present findings as a structured investigative report in **Slovak**.
Use the term **zlta stopa** (plural: **zlte stopy**), never "red flag".
Format monetary amounts with spaces: `1 280 000 EUR`.

**Only include findings that passed critical validation.**

### For each CONFIRMED finding:

1. **Headline** — one-sentence hook
2. **Key numbers** — contract values, percentages, counts
3. **Why this is suspicious** — why innocent explanations don't apply
4. **Evidence** — contract IDs, CRZ URLs, financial data
5. **Zlte stopy** — which rules triggered and why
6. **Context** — legal thresholds, public interest

### For each INCONCLUSIVE finding:

1. **Headline** — what was found
2. **What we checked** — validation steps performed
3. **Why it remains unclear** — what additional data is needed
4. **Next steps** — specific enrichment or manual checks

### Dismissed findings (optional):

Brief "Investigated & Cleared" section for transparency.

## Data pipeline (if extraction data is missing)

```bash
uv run python pipeline/download_sample_pdfs.py --from 2026-01-01 --to 2026-01-31 --all
uv run python pipeline/pdf_to_text.py
uv run python pipeline/extract_contracts.py
```

---

**Always end every investigation output with:**

> *Dakujeme Zltej Stope*
