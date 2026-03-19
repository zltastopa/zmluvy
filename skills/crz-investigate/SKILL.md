---
name: crz-investigate
description: Broad investigative scan of Slovak government contracts from CRZ. Runs SQL analytics, validates findings, enriches suppliers via FinStat, and optionally traces ownership via RPVS and foaf.sk. Produces publishable findings in Slovak. Use this skill whenever the user asks to investigate, analyze, audit, scan, or find zlte stopy in CRZ contracts for a time period, even if they don't explicitly mention "CRZ" — any request about Slovak government contract anomalies, procurement fraud, or public spending analysis should trigger this skill.
---

# CRZ Investigative Analysis

Perform investigative journalism-grade analysis of Slovak government contracts
from the Central Register of Contracts (CRZ). This is the **broad scan** —
it sweeps a time period to surface leads.

For deep investigation of a specific company, use **crz-deep-investigate** instead.

## Input

| Field | Description | Example |
|-------|-------------|---------|
| `date_from` | Start of investigation period | 2026-01-01 |
| `date_to` | End of investigation period | 2026-01-31 |
| `focus` | Optional: narrow to specific buyer, sector, or flag type | "Ministerstvo vnutra", "construction", "signatory_overlap" |

## Data source

**Primary:** FastAPI + DuckDB at `https://zmluvy.zltastopa.sk` — supports
arbitrary SQL. Query via JSON API:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+...&_shape=array
```

**Note:** Backend uses DuckDB syntax (see sql-analytics skill for key differences).
Full schema: **[docs/data/](docs/data/README.md)**

## Investigation pipeline

This orchestrator coordinates 5 specialized agents and 2 skills. The key
optimization: supplier profiling and network mapping run **in parallel**,
giving a 3x speedup for multi-supplier investigations.

### Phase 1: SQL Analytics (skill)

Use the **[sql-analytics](../sql-analytics/SKILL.md)** skill.

Run all 20 standard queries for the given date range. The skill groups results
into 7 categories and produces a Top 5 highlights section.

### Phase 2: Critical Validation (skill)

Use the **[critical-validation](../critical-validation/SKILL.md)** skill.

**Every finding from Phase 1 MUST pass through validation.** Challenge each
against data artifacts and innocent explanations. Classify as CONFIRMED,
DISMISSED, or INCONCLUSIVE.

### Phase 3: Gate decision (agent)

Spawn the **phase-gater** agent (`agents/phase-gater.md`, Haiku).

Pass it the findings summary from Phase 2. It returns:
- `GO` or `STOP` for each subsequent phase
- Which suppliers to include (may be a subset)
- Which phases to skip

This replaces the manual lookup table — the agent applies the same rules
but adapts to edge cases. If it says STOP, skip to Phase 7 (report) with
only the CONFIRMED findings from Phases 1-2.

### Phase 4: Parallel profiling (agents)

**This is where the speed gain happens.** Spawn one **supplier-profiler**
agent (`agents/supplier-profiler.md`, Sonnet) per supplier ICO — all in
parallel.

```
┌─────────────────────────────────────────────────────┐
│  Orchestrator spawns N supplier-profiler agents      │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Profiler  │ │ Profiler  │ │ Profiler  │  ...      │
│  │ ICO: A    │ │ ICO: B    │ │ ICO: C    │            │
│  │ (Sonnet)  │ │ (Sonnet)  │ │ (Sonnet)  │            │
│  └─────┬────┘ └─────┬────┘ └─────┬────┘            │
│        │            │            │                    │
│        ▼            ▼            ▼                    │
│  profile_A.json profile_B.json profile_C.json        │
└─────────────────────────────────────────────────────┘
```

Each profiler receives:
```json
{
  "ico": "{supplier_ico}",
  "name": "{supplier_name}",
  "context": "flagged by sql-analytics: {flag_types}",
  "phases": ["db", "finstat"],
  "contracts_of_interest": [/* from Phase 1 */]
}
```

Include `"uvo"` in phases for contracts >50K EUR. Include `"rpvs"` if the
phase-gater approved the RPVS phase.

**Wait for all profilers to complete before proceeding.**

### Phase 5: Network mapping (agent)

Spawn one **network-mapper** agent (`agents/network-mapper.md`, Sonnet).

Pass it all supplier profiles from Phase 4:
```json
{
  "suppliers": [
    {"ico": "...", "name": "...", "signatories": [...], "flags": [...]}
  ],
  "buyer_ico": "{common_buyer_ico}",
  "buyer_name": "{common_buyer_name}",
  "depth": "shallow",
  "phases": ["foaf", "rpvs"]
}
```

Only include the `rpvs` phase if the phase-gater approved it. Use `"deep"`
depth only for the top lead by contract value.

### Phase 6: Cross-referencing (agent)

Spawn the **cross-referencer** agent (`agents/cross-referencer.md`, Opus).

Pass it all profiler outputs + network map:
```json
{
  "profiles": [/* supplier-profiler outputs */],
  "network": {/* network-mapper output */},
  "context": {
    "investigation_type": "broad_scan",
    "period": {"from": "{date_from}", "to": "{date_to}"},
    "buyer_focus": "{focus or null}"
  }
}
```

This agent finds cross-cutting patterns — coordinated timing, shared
directors, threshold gaming clusters, combined capacity concerns. Each
finding is classified CONFIRMED / INCONCLUSIVE / DISMISSED.

### Phase 7: Report (agent)

Spawn the **report-writer** agent (`agents/report-writer.md`, Opus).

Pass it the cross-referencer output (or Phase 2 output if Phases 4-6 were
skipped):
```json
{
  "report_type": "broad_scan",
  "period": {"from": "{date_from}", "to": "{date_to}"},
  "focus": "{focus or null}",
  "findings": [/* cross-referencer findings */],
  "dismissed_summary": [/* dismissed patterns */],
  "stats": {
    "total_contracts": 0,
    "total_value": 0,
    "queries_run": 20
  }
}
```

## Parallel execution diagram

```
Time ──────────────────────────────────────────────────────►

Phase 1-2 (sequential, this orchestrator):
  ┌─────────────────┐ ┌─────────────────┐
  │  sql-analytics   │ │ critical-valid.  │
  │    (~2 min)      │ │   (~2 min)       │
  └────────┬────────┘ └────────┬────────┘
           │                   │
Phase 3 (Haiku, fast):         │
  ┌────────┴────┐              │
  │ phase-gater │◄─────────────┘
  │   (~12s)    │
  └──────┬──────┘
         │
Phase 4-5 (parallel agents):
  ┌──────┴──────────────────────────────────┐
  │                                          │
  │  ┌────────┐ ┌────────┐ ┌────────┐       │
  │  │Prof. A │ │Prof. B │ │Prof. C │       │
  │  │(Sonnet)│ │(Sonnet)│ │(Sonnet)│ ...   │
  │  │ ~100s  │ │ ~100s  │ │ ~100s  │       │
  │  └───┬────┘ └───┬────┘ └───┬────┘       │
  │      │          │          │             │
  │      └──────────┼──────────┘             │
  │                 ▼                        │
  │  ┌──────────────────────┐                │
  │  │   network-mapper     │                │
  │  │     (Sonnet)         │                │
  │  │     ~120s            │                │
  │  └──────────┬───────────┘                │
  └─────────────┼────────────────────────────┘
                │
Phase 6-7 (sequential):
  ┌─────────────┴──────────────┐
  │   cross-referencer (Opus)   │
  │        ~180s                │
  └─────────────┬──────────────┘
                │
  ┌─────────────┴──────────────┐
  │   report-writer (Opus)     │
  │        ~120s               │
  └────────────────────────────┘
```

**Sequential (5 suppliers):** ~25 min
**Parallel (5 suppliers):** ~8 min (3.1x speedup)

## Additional cross-checks

For specific suppliers, also:
- Cross-reference with `tax_reliability`: `JOIN tax_reliability t ON replace(z.dodavatel_ico, ' ', '') = t.ico WHERE t.status = 'menej spolahlivy'`
- Check all contracts for a flagged supplier: `WHERE replace(dodavatel_ico, ' ', '') = '{ico}' ORDER BY datum_zverejnenia`
- Review extraction data: `SELECT extraction_json FROM extractions WHERE zmluva_id = {id}`
- Verify on CRZ: `https://www.crz.gov.sk/zmluva/{id}/`
- Check FinStat: `https://finstat.sk/{ico}`
- Check UVO: search by ICO or contract name on `uvo.gov.sk`

## Output format

The report-writer agent produces the final output. See `agents/report-writer.md`
for the two templates (broad_scan and deep_dive).

Key conventions:
- **Slovak language** throughout (no diacritics — `z` not `ž`)
- **zlta stopa** / **zlte stopy**, never "red flag"
- Format amounts with spaces: `1 280 000 EUR`
- Every contract has a CRZ URL: `https://www.crz.gov.sk/zmluva/{id}/`
- Only include findings that passed critical validation
- End with: *Dakujeme Zltej Stope*

## Data pipeline (if extraction data is missing)

```bash
uv run python delta_store/ingest.py --from 2026-01-01 --to 2026-01-31
```

---

**Always end every investigation output with:**

> *Dakujeme Zltej Stope*
