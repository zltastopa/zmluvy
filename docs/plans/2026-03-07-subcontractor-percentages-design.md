# Subcontractor percentage extraction — Design

## Goal

Capture per-subcontractor percentage shares at the contract level so we
can answer: "which subcontractor is getting what share of the contract
value?" This extends the existing `hidden_entities` extraction rather
than adding a separate structure.

## Context

- ~882 / 7,724 text files (~11%) mention "subdodávateľ"
- ~56 have a numeric percentage near subcontractor language
- Per-subcontractor breakdowns typically live in appendix tables
  ("Príloha — Zoznam subdodávateľov") which `pdftotext` garbles
  frequently — the LLM may recover some of these
- Common false positive: Russian sanctions 5%/10% thresholds
  (EU regulation 833/2014, Article 5k) — these are not contract shares

## Schema change

Extend the `subcontractor` role in `hidden_entities` with two optional
fields:

```json
"hidden_entities": [
  {
    "name": "ACME s.r.o.",
    "ico": "12345678",
    "role": "subcontractor",
    "percentage": 30,
    "subcontract_subject": "elektromontážne práce"
  }
]
```

- `percentage` — numeric share of total contract value (0–100), `null`
  if not stated
- `subcontract_subject` — what the subcontractor does, short phrase in
  Slovak, `null` if not stated
- These fields only apply when `role == "subcontractor"`

Add one new top-level boolean:

```json
"subcontracting_mentioned": true
```

This flags contracts that discuss subcontracting (subdodávateľ,
subdodávka) even when no named subcontractor or percentage is found.

## Prompt changes

1. Extend the `subcontractor` role description to ask for `percentage`
   and `subcontract_subject`. Instruct the model to look in appendix
   tables, inline text, and anywhere else.
2. Add explicit negative examples: ignore DPH/VAT, penalties, discount
   rates, co-financing, and Russian sanctions thresholds.
3. Add `subcontracting_mentioned` to the JSON schema with instructions
   to set it true when subcontracting language appears.

## Flat DB columns

Three new columns in the `extractions` table, derived during DB upsert:

| Column                       | Type       | Source                                     |
|------------------------------|------------|--------------------------------------------|
| `subcontracting_mentioned`   | bool       | `extraction["subcontracting_mentioned"]`   |
| `subcontractor_count`        | int        | count of hidden_entities with role=subcontractor |
| `subcontractor_max_percentage` | float/null | max percentage across subcontractor entries |

## Evaluation plan

1. **Scope test to ~882 files** that match `subdod` in their text,
   not the full corpus. Avoids wasting API calls on contracts that
   definitely lack subcontractor data.
2. Run extraction on 5 gold set files first (3 positive, 2 negative
   controls) and inspect JSON output.
3. If results look good, run on the full ~882 subdodávateľ-mentioning
   files.
4. Check false positive rate from DPH/penalty/sanctions percentages.
5. Only then backfill remaining contracts.

### Gold set — positive examples

- `6573916.txt` — appendix table with subdodávateľ % podiel columns
- `6570430.txt` — "predmet subdodávky a jej % podiel na celkovom plnení"
- `6571913.txt` — "podiel zákazky, ktorý má v úmysle zadať subdodávateľom"

### Negative controls

Pick 2 files with high penalty counts and DPH/VAT percentages but no
subcontractor language — verify `subcontracting_mentioned` is false
and no subcontractor percentages appear.

## Backfill

Add `--force` flag to `extract_contracts.py` that re-extracts even
when a JSON file already exists. Required for backfilling old
extractions that lack the new fields.

## Design decisions

- **Extend `hidden_entities` rather than new top-level object** — avoids
  duplication since the LLM already extracts subcontractors there.
- **`subcontracting_mentioned` as cheap signal** — catches the many
  contracts with subcontracting boilerplate but no named entities.
- **Test on subdodávateľ-matching files only** — dense evaluation,
  avoids wasting ~$30 on contracts that won't have the data.
