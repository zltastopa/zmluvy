---
name: crz-deep-investigate
description: Deep investigative dive into a specific Slovak company or corporate network. Maps all contracts, hidden entities, RPVS beneficial ownership, foaf.sk corporate connections, and timeline patterns. Produces a comprehensive Slovak report with network diagrams. Use this skill whenever the user asks to do a deep investigation, hlbsia investigativa, company analysis, ownership tracing, or corporate network mapping for a specific ICO, company name, or suspicious entity — even if they don't use the exact term "deep investigate". Any request to thoroughly examine a single company's CRZ footprint should trigger this skill.
---

# CRZ Deep Investigation

Perform a deep investigative dive into a specific company or corporate network
connected to Slovak government contracts. Takes a single target (company name
or ICO) and maps the full network.

For broad scanning across a time period, use **crz-investigate** instead.

## Input

| Field | Description | Example |
|-------|-------------|---------|
| `target` | Company ICO or name | 44424418, "PARA INVEST s.r.o." |
| `context` | Why this company is being investigated | "flagged by sql-analytics", "large sole-source contract" |
| `scope` | Which phases to run | "full" (default), "db-only" (Phases 1-2), "no-browser" (skip RPVS/foaf) |

## Data source

**Primary:** FastAPI + DuckDB at `https://zmluvy.zltastopa.sk` — supports
arbitrary SQL. Query via JSON API:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+...&_shape=array
```

**Note:** Backend uses DuckDB syntax (see sql-analytics skill for key differences).
Full schema: **[docs/data/](docs/data/README.md)**

## Investigation pipeline

This orchestrator coordinates agents for deep investigation. Unlike the broad
scan, it starts with direct SQL mapping (this orchestrator runs the queries),
then fans out to agents for enrichment and analysis.

### Phase 1: Target Contract Mapping (this orchestrator)

Map ALL contracts involving the target company:

```sql
-- All contracts for the target (as supplier or buyer)
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
       z.objednavatel, z.objednavatel_ico,
       printf('%.2f', z.suma) as suma, z.datum_zverejnenia, z.datum_podpisu
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '{ico}'
   OR replace(z.objednavatel_ico, ' ', '') = '{ico}'
ORDER BY z.suma DESC;

-- All zlte stopy for this company's contracts
SELECT rf.flag_type, fr.label, fr.severity, rf.detail,
       z.id, z.nazov_zmluvy, printf('%.2f', z.suma) as suma
FROM red_flags rf
JOIN flag_rules fr ON fr.id = rf.flag_type
JOIN zmluvy z ON rf.zmluva_id = z.id
WHERE replace(z.dodavatel_ico, ' ', '') = '{ico}';

-- Extraction data — hidden entities, signatories, penalty asymmetry
SELECT e.zmluva_id, z.nazov_zmluvy,
       e.extraction_json->>'$.hidden_entities' as hidden_entities,
       e.extraction_json->>'$.signatories' as signatories,
       e.extraction_json->>'$.actual_subject' as actual_subject,
       e.penalty_asymmetry, e.service_category, e.bezodplatne
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE replace(z.dodavatel_ico, ' ', '') = '{ico}';
```

Also identify the **contracting framework** — if contracts share a naming
pattern, query ALL contracts in that framework:

```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
       printf('%.2f', z.suma) as suma, z.datum_zverejnenia
FROM zmluvy z
WHERE z.nazov_zmluvy LIKE '%{framework_pattern}%'
ORDER BY z.suma DESC;
```

### Phase 2: Hidden Entity Expansion (this orchestrator)

Extract all hidden entities from the target's contracts:

```sql
SELECT DISTINCT
       json_extract_string(he, '$.ico') as entity_ico,
       json_extract_string(he, '$.name') as entity_name,
       json_extract_string(he, '$.role') as entity_role
FROM (
  SELECT unnest(from_json(
    json_extract(e.extraction_json, '$.hidden_entities'), '["JSON"]'
  )) as he
  FROM extractions e
  WHERE e.zmluva_id IN (
    SELECT id FROM zmluvy WHERE replace(dodavatel_ico, ' ', '') = '{ico}'
  )
) sub
WHERE he IS NOT NULL;
```

For each hidden entity ICO, check if it also has CRZ contracts:

```sql
SELECT any_value(z.dodavatel) as dodavatel, z.dodavatel_ico, count(*) as pocet,
       printf('%.2f', sum(z.suma)) as celkom
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '{hidden_ico}'
GROUP BY z.dodavatel_ico;
```

### Phase 3: Gate decision (agent)

Spawn the **phase-gater** agent (`agents/phase-gater.md`, Haiku).

Pass findings from Phases 1-2:
```json
{
  "current_phase": "target-mapping",
  "next_phase": "enrichment",
  "findings_summary": {
    "total_findings": 0,
    "severity_counts": {"danger": 0, "warning": 0, "info": 0},
    "top_findings": ["..."],
    "contract_count": 0,
    "total_value": 0,
    "hidden_entities_found": 0
  }
}
```

The user can override the gate with `scope: "full"` (always runs all phases).

| Phase 1-2 findings | Default action |
|---|---|
| Few contracts (<5), no flags, no hidden entities | Report clean profile. Skip Phases 4-6. |
| Moderate activity, some flags | Run Phase 4 (profiling) + Phase 5 (network). Skip UVO unless contracts >200K. |
| Many contracts, multiple flags, hidden entities | Full pipeline (all phases). |

### Phase 4: Parallel profiling (agents)

Spawn **supplier-profiler** agents (`agents/supplier-profiler.md`, Sonnet)
for the target AND all related companies found in Phase 2 — **in parallel**.

```
┌────────────────────────────────────────────────┐
│  Target: PARA INVEST (44424418)                 │
│  Hidden entities: Company B, Company C          │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Profiler  │ │ Profiler  │ │ Profiler  │       │
│  │ PARA INV  │ │ Company B │ │ Company C │       │
│  │ (Sonnet)  │ │ (Sonnet)  │ │ (Sonnet)  │       │
│  └─────┬────┘ └─────┬────┘ └─────┬────┘        │
│        └────────┬───┘────────────┘               │
│                 ▼                                 │
│         All profiles ready                       │
└────────────────────────────────────────────────┘
```

Each profiler gets `phases: ["db", "finstat", "uvo"]` by default. Add `"rpvs"`
if the phase-gater approved it.

### Phase 5: Network mapping (agent)

Spawn the **network-mapper** agent (`agents/network-mapper.md`, Sonnet).

For deep investigations, use `depth: "deep"` — follow all person chains,
not just 1 hop. Pass all companies from Phase 4:

```json
{
  "suppliers": [
    {"ico": "44424418", "name": "PARA INVEST s.r.o.", "signatories": [...], "flags": [...]},
    {"ico": "...", "name": "Company B", "signatories": [...], "flags": [...]}
  ],
  "buyer_ico": "{main_buyer_ico}",
  "buyer_name": "{main_buyer_name}",
  "depth": "deep",
  "phases": ["foaf", "rpvs"]
}
```

### Phase 6: Cross-referencing (agent)

Spawn the **cross-referencer** agent (`agents/cross-referencer.md`, Opus).

Pass all profiler outputs + network map:
```json
{
  "profiles": [/* all supplier-profiler outputs */],
  "network": {/* network-mapper output */},
  "context": {
    "investigation_type": "deep_dive",
    "period": null,
    "target": {"ico": "44424418", "name": "PARA INVEST s.r.o."},
    "buyer_focus": "{main_buyer_name}"
  }
}
```

The cross-referencer also performs **timeline & coordination analysis**:
- Compare foaf.sk board appointment dates against contract signing dates
- Flag appointments shortly before large contracts
- Same-day contract signing across related entities
- Same-minute CRZ publication times (batch upload)
- Identical contract values across different entities
- Hidden entities appearing as "previous_operator" (asset transfers)

### Phase 7: Report (agent)

Spawn the **report-writer** agent (`agents/report-writer.md`, Opus).

Pass the deep_dive template:
```json
{
  "report_type": "deep_dive",
  "target": {"name": "PARA INVEST s.r.o.", "ico": "44424418"},
  "findings": [/* cross-referencer findings */],
  "dismissed_summary": [/* dismissed patterns */],
  "stats": {"total_contracts": 0, "total_value": 0}
}
```

The report-writer produces the INVESTIGATIVNA SPRAVA format with mandatory
ASCII network diagram.

## Execution flow

```
Time ──────────────────────────────────────────────────────►

Phase 1-2 (this orchestrator, sequential):
  ┌──────────────────┐ ┌──────────────────────┐
  │ Target mapping    │ │ Hidden entity expand  │
  │   (SQL queries)   │ │   (SQL queries)       │
  └────────┬─────────┘ └──────────┬───────────┘
           │                      │
Phase 3:   └──────────┬───────────┘
  ┌───────────────────┴──────────────────┐
  │ phase-gater (Haiku, ~12s)            │
  │ → GO/STOP + which suppliers          │
  └───────────────────┬──────────────────┘
                      │
Phase 4-5 (parallel agents):
  ┌───────────────────┴──────────────────┐
  │ ┌──────────┐ ┌──────────┐            │
  │ │ Profiler │ │ Profiler │  ...       │
  │ │ target   │ │ entity B │            │
  │ │ (Sonnet) │ │ (Sonnet) │            │
  │ └────┬─────┘ └────┬─────┘            │
  │      └──────┬──────┘                  │
  │             ▼                         │
  │ ┌───────────────────────┐             │
  │ │ network-mapper (deep) │             │
  │ │      (Sonnet)         │             │
  │ └───────────┬───────────┘             │
  └─────────────┼─────────────────────────┘
                │
Phase 6-7 (sequential):
  ┌─────────────┴──────────────┐
  │  cross-referencer (Opus)    │
  │  + timeline analysis       │
  └─────────────┬──────────────┘
                │
  ┌─────────────┴──────────────┐
  │  report-writer (Opus)      │
  │  INVESTIGATIVNA SPRAVA     │
  └────────────────────────────┘
```

## Critical rules

1. **Check ALL companies in the network on RPVS** — not just the primary target.
2. **Build the board member matrix** — identical persons across entities is the strongest evidence.
3. **Include exact dates** — coordinated timing is strong evidence.
4. **CRZ URLs are mandatory** — every contract must have its link.
5. **ASCII network diagrams** — always include in the final report.
6. **Slovak language throughout** — headers, narrative in Slovak.
7. **Quantify everything** — totals, ratios, counts.
8. **Never report unverified claims** — classify as CONFIRMED, INCONCLUSIVE, or DISMISSED.
9. **End with "Dakujeme Zltej Stope"**.
