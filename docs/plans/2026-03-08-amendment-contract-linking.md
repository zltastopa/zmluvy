# Amendment–Contract Linking Design

How to map dodatky (amendments) to their parent zmluvy (contracts) so that
all information about a contractual relationship is merged together.

## The problem

The CRZ database has 6,579 amendments (typ=dodatok) and 115,036 contracts
(typ=zmluva). There is **no native parent–child link** in the CRZ data:
the XML `<ref>` field is empty for 99.9% of amendments, and the CRZ
website itself shows no parent link on amendment detail pages.

Yet amendments are meaningless without their parent contract — a "Dodatok
č. 3 k Zmluve o dielo" only makes sense when you can see the original
scope, amount, parties, and previous amendments.

## Key insight: cislo_zmluvy is unique within an objednavatel

Each objednavatel (buyer/ordering org) assigns contract numbers from their
own internal scheme. Within one `objednavatel_ico`, a `cislo_zmluvy` value
uniquely identifies a contractual relationship.

This means: if we can extract the parent contract number from an amendment
text, we can match it by searching `cislo_zmluvy` within the same
`objednavatel_ico` — and expect a unique hit.

Both the amendment and the parent contract also share the same party pair
(`dodavatel_ico` + `objednavatel_ico`), which serves as an additional
confirmation signal.

## Linking strategies (in priority order)

### Strategy 1: Parse cislo_zmluvy patterns (no LLM needed)

Many amendments encode the parent contract number directly in their own
`cislo_zmluvy` field. Two dominant patterns:

**Pattern A — "Dodatok" keyword in cislo** (covers ~3,500 amendments)

The healthcare system (VšZP, Dôvera, Union ZP) uses cislo values like:

    62NVSU000422 Dodatok č. 15

The base contract number is everything before ` Dodatok`: `62NVSU000422`.

Linking rule:
```sql
parent_cislo = trim(substr(cislo_zmluvy, 1, instr(cislo_zmluvy, ' Dodatok') - 1))
```
Match within same `objednavatel_ico` (+ `dodavatel_ico` for confirmation).

**Pattern B — Slash suffix** (covers ~1,300 amendments)

Some organizations (notably SEPS) use a slash-suffix convention:

    2022-0178-1180530/03    -- Dodatok č. 3
    2022-0178-1180530       -- parent Zmluva o dielo

Linking rule:
```sql
parent_cislo = substr(cislo_zmluvy, 1, instr(cislo_zmluvy, '/') - 1)
```
Match within same `objednavatel_ico`. Require base length ≥ 6 characters
to avoid false positives from generic numbers like `2/2026`.

**Pattern C — Exact cislo reuse** (~36 amendments)

Some amendments carry the exact same `cislo_zmluvy` as their parent.

Linking rule:
```sql
WHERE z.cislo_zmluvy = a.cislo_zmluvy
  AND z.objednavatel_ico = a.objednavatel_ico
  AND z.id <> a.id
```

### Strategy 2: LLM extraction of parent contract number

For amendments whose `cislo_zmluvy` doesn't encode the parent reference,
the amendment *text* almost always names the parent explicitly:

    "Dodatok č. 1 k Zmluve o združenej dodávke elektrickej energie č. 20242555"
    "Dodatok č. 3 k Zmluve č. 2022-0178-1180530"

**Extraction prompt** asks the LLM to return:
- `parent_contract_number` — the referenced contract number
- `amendment_number` — which amendment this is (1, 2, 3…)
- `parent_title` — short title of the parent contract
- `confidence` — high / medium / low

**Matching**: search for `parent_contract_number` as `cislo_zmluvy` within
the same `objednavatel_ico`. Within one buyer this should give a unique
match.

**Experiment results** (72 amendments with text):
- LLM successfully extracted a parent reference in **68%** of cases
- 32% had no extractable parent ref (price lists, collective agreements,
  standalone documents that don't reference a parent)
- Main failure mode: parent contract not in our database (published
  before our 33-day data window), not extraction quality

### Strategy 3: Unique party pair fallback

When an amendment's party pair (`dodavatel_ico` + `objednavatel_ico`)
matches exactly one `zmluva` in the database, the link is unambiguous.

This currently matches ~90 amendments (those where the two organizations
have only ever had one contract between them in our data).

## Sibling grouping (even without the parent)

Even when the parent contract isn't in our database, we can still group
sibling amendments together. Amendments that share:

- same base `cislo_zmluvy` (after stripping suffixes), AND
- same `objednavatel_ico` (+ `dodavatel_ico`)

…belong to the same contractual relationship.

Experiment found **392 sibling groups** covering **1,244 amendments**
using just the cislo-stripping strategies.

## Current coverage bottleneck

With our current 33-day data window (Feb–Mar 2026), most parent contracts
aren't in the database — they were published months or years earlier.

| Strategy | Amendments matched | Notes |
|---|---|---|
| Cislo pattern parsing | ~700 | Mostly healthcare (siblings) |
| LLM extraction + DB match | ~3 | Parents predate our data |
| Unique party pair | ~90 | Unambiguous pair match |
| **Total** | **~800 / 6,579** | **~12%** |

**Loading more historical CRZ data would dramatically improve this.**
The CRZ publishes daily XML exports going back years. With 2–3 years of
historical data, the `objednavatel_ico + cislo_zmluvy` approach should
match the vast majority of amendments.

## Implementation plan

### Phase 1: Schema changes

Add a `contract_family_id` column to `zmluvy` (or a separate linking
table) to group amendments with their parent:

```sql
ALTER TABLE zmluvy ADD COLUMN contract_family_id TEXT;
-- Value: the canonical contract number (base cislo) for this family
-- e.g. "62NVSU000422" for all amendments of that healthcare contract

ALTER TABLE zmluvy ADD COLUMN parent_zmluva_id INTEGER REFERENCES zmluvy(id);
-- Direct link to the parent record (when found in DB)
```

### Phase 2: Batch linker script (`link_amendments.py`)

1. Run cislo-pattern strategies (A, B, C) across all amendments — pure SQL
2. For unmatched amendments with text: run LLM extraction of parent ref
3. Match extracted refs within same `objednavatel_ico`
4. Fall back to unique party pair for remaining
5. Store results in `contract_family_id` and `parent_zmluva_id`

### Phase 3: Extend extraction prompt

Add to the existing `extract_contracts.py` prompt:

```json
{
  "parent_contract_number": "contract number of the parent zmluva this amends, or null",
  "amendment_number": 3
}
```

This piggybacks on the existing extraction pipeline — no separate LLM
call needed.

### Phase 4: Merged contract view

Create a SQL view or API endpoint that shows a contract with all its
amendments merged:

```sql
CREATE VIEW contract_families AS
SELECT
    COALESCE(z.parent_zmluva_id, z.id) as family_root_id,
    z.id, z.typ, z.cislo_zmluvy, z.nazov_zmluvy,
    z.suma, z.datum_zverejnenia,
    e.actual_subject, e.service_category, e.penalty_asymmetry,
    z.contract_family_id
FROM zmluvy z
LEFT JOIN extractions e ON e.zmluva_id = z.id
ORDER BY contract_family_id, z.datum_zverejnenia;
```

This enables queries like:
- "Show me all amendments to contract X and the total cumulative value"
- "Which contracts had the most amendments?" (potential red flag)
- "Did penalties change between the original and amendment?"

## What won't link (and why)

- **Price lists / cenníky** (~5% of amendments): these are standalone
  documents with no parent contract reference
- **Collective agreements** (kolektívne zmluvy): standalone, not
  amendments to prior contracts
- **Objednávky** (purchase orders): may reference a rámcová zmluva but
  with a different cislo scheme
- **Parent outside CRZ**: some parent contracts are from organizations
  that don't publish to CRZ, or predate the CRZ system (2011+)

## Files

- `experiment_link_amendments.py` — LLM extraction experiment (72 docs)
- `data/amendment_linking_experiment.json` — detailed experiment results
