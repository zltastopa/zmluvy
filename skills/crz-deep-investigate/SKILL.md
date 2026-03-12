---
name: crz-deep-investigate
description: Deep investigative dive into a specific Slovak company or corporate network. Maps all contracts, hidden entities, RPVS beneficial ownership, foaf.sk corporate connections, and timeline patterns. Produces a comprehensive Slovak report with network diagrams. Use when asked to do a deep investigation, hlbsia investigativa, company analysis, or ownership tracing for a specific ICO or company name.
---

# CRZ Deep Investigation

Perform a deep investigative dive into a specific company or corporate network
connected to Slovak government contracts. Takes a single target (company name
or ICO) and maps the full network.

For broad scanning across a time period, use **crz-investigate** instead.

## Data source

**Primary:** Datasette at `https://zmluvy.zltastopa.sk/data/crz` — supports
arbitrary SQL. Query via JSON API:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+...&_shape=array
```

**Local fallback:** `crz.db` in the repo root. Full schema: **[docs/data/](docs/data/README.md)**

## Input

A **company name**, **ICO**, or **reference to a previously identified
suspicious entity**. If unclear, ask for the ICO.

## Investigation pipeline

Execute these phases sequentially. Each builds on previous data.

### Phase 1: Target Contract Mapping

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
       json_extract(e.extraction_json, '$.hidden_entities') as hidden_entities,
       json_extract(e.extraction_json, '$.signatories') as signatories,
       json_extract(e.extraction_json, '$.actual_subject') as actual_subject,
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

### Phase 2: Hidden Entity Expansion

Extract all hidden entities from the target's contracts:

```sql
SELECT DISTINCT json_extract(value, '$.ico') as entity_ico,
       json_extract(value, '$.name') as entity_name,
       json_extract(value, '$.role') as entity_role
FROM extractions e, json_each(json_extract(e.extraction_json, '$.hidden_entities'))
WHERE e.zmluva_id IN (
  SELECT id FROM zmluvy WHERE replace(dodavatel_ico, ' ', '') = '{ico}'
);
```

For each hidden entity ICO, check if it also has CRZ contracts:

```sql
SELECT z.dodavatel, z.dodavatel_ico, count(*) as pocet,
       printf('%.2f', sum(z.suma)) as celkom
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '{hidden_ico}'
GROUP BY z.dodavatel_ico;
```

### Phase 3: RPVS Beneficial Ownership

Use the **[rpvs-lookup](../rpvs-lookup/SKILL.md)** skill.

Check the target AND all related companies found in Phases 1-2.
**Not just the primary target** — if you discovered 3 related companies, check all 3.

Key things to look for:
- Missing RPVS registration (legally required for >100K contracts)
- UBOs that are public officials
- Same UBO across multiple supplier companies
- Recent ownership changes before large contracts

### Phase 4: Corporate Network Mapping

Use the **[foaf-network](../foaf-network/SKILL.md)** skill.

This is the core of the deep investigation. For the target and all related
companies, build the full person-to-company matrix. Trace ownership chains.
Detect identical boards, family clusters, and coordinated appointments.

### Phase 5: Procurement Verification

Use the **[uvo-procurement](../uvo-procurement/SKILL.md)** skill.

For the target's contracts, verify the procurement process:

1. Check `uvo_url` field in CRZ data — follow links to UVO/Josephine/EVO
2. If no link exists, search UVO by buyer ICO + contract name
3. Extract: procurement type, bid count, winning price, competitor ranking
4. Compare CRZ contract value with UVO winning price

Key questions:
- Did this contract go through open competition?
- How many bidders participated?
- Was it priame rokovacie konanie (direct negotiation) — and if so, why?
- Does the same supplier repeatedly win with no competition?

### Phase 6: Timeline & Coordination Analysis

Cross-reference all collected data into a timeline:

- Compare foaf.sk board appointment dates against contract signing dates
- Flag appointments shortly before large contracts

Check for coordinated patterns:
- Same-day contract signing across multiple related entities
- Same-minute CRZ publication times (batch upload of coordinated contracts)
- Identical contract values across different entities
- Hidden entities appearing as "previous_operator" (asset transfers)

## Output format

The final report MUST follow this structure, written in **Slovak**.
Use **zlta stopa / zlte stopy**, never "red flag".
Format amounts with spaces: `1 280 000 EUR`.

```markdown
# INVESTIGATIVNA SPRAVA: [Target] a [network name]

## Zhrnutie
[2-3 sentence executive summary]

---

## CONFIRMED: [Finding headline] ([total value])

### Co sme nasli
[Facts + contract table]

### Preco je to podozrive
**1. [Zlta stopa category]**
[Evidence with tables — board member matrix, financial comparison]

### Verejne obstaravanie (UVO)
| Zmluva | Typ postupu | Pocet ponuk | Vitazna cena | UVO link |
|---|---|---|---|---|

### Dokazy
| Zmluva | CRZ URL | UVO URL | PDF |
|---|---|---|---|

### Zlte stopy
| Stopa | Severity | Detail |
|---|---|---|

---

## INCONCLUSIVE: [Finding] ([value])
### Co nevieme
### Dalsie kroky

---

## Schema: Ako to funguje

[ASCII network diagram — MANDATORY]:
    [Buyer]
        |
    +---+---+
    |       |
 Company A  Company B
    |       |
    +---+---+
        |
    [Shared persons]

---

## Klucove otazky pre dalsie vysetrovanie
1. ...
2. ...

---

> *Dakujeme Zltej Stope*
```

## Critical rules

1. **Check ALL companies in the network on RPVS** — not just the primary target.
2. **Build the board member matrix** — identical persons across entities is the strongest evidence.
3. **Include exact dates** — coordinated timing is strong evidence.
4. **CRZ URLs are mandatory** — every contract must have its link.
5. **ASCII network diagrams** — always include a visual representation.
6. **Slovak language throughout** — headers, narrative in Slovak.
7. **Quantify everything** — totals, ratios, counts.
8. **Never report unverified claims** — classify as CONFIRMED, INCONCLUSIVE, or DISMISSED.
9. **End with "Dakujeme Zltej Stope"**.
