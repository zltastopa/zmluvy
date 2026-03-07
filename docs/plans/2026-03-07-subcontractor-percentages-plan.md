# Subcontractor Percentage Extraction — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend the LLM extraction prompt to capture per-subcontractor percentage shares and a contract-level `subcontracting_mentioned` flag, with corresponding flat DB columns.

**Architecture:** Extend the existing `hidden_entities` subcontractor entries with optional `percentage` and `subcontract_subject` fields. Add a top-level `subcontracting_mentioned` boolean. Derive three flat DB columns during upsert. Add `--force` flag for re-extraction.

**Tech Stack:** Python, sqlite-utils, OpenRouter API (Gemini 2.5 Flash Lite), httpx

---

### Task 1: Update the extraction JSON schema in the system prompt

**Files:**
- Modify: `extract_contracts.py:37` (hidden_entities schema line)
- Modify: `extract_contracts.py:48` (add subcontracting_mentioned after bezodplatne)
- Modify: `extract_contracts.py:83` (subcontractor role description)
- Modify: `extract_contracts.py:113-124` (rules section)

**Step 1: Update the JSON schema block**

In `extract_contracts.py`, in `SYSTEM_PROMPT`, change line 37 from:

```
  "hidden_entities": [{"name": "...", "ico": "...", "role": one of the roles listed below}],
```

to:

```
  "hidden_entities": [{"name": "...", "ico": "...", "role": one of the roles listed below, "percentage": number or null, "subcontract_subject": "..." or null}],
```

Add after the `"bezodplatne": bool` line (line 48):

```
  "subcontracting_mentioned": bool
```

**Step 2: Update the subcontractor role description**

In `extract_contracts.py`, change line 83 from:

```
- subcontractor — subdodávateľ: entity performing work under the main contract, geodetic companies in property transfers (e.g. GEPRAMS, GEOmark doing surveys)
```

to:

```
- subcontractor — subdodávateľ: entity performing work under the main contract, geodetic companies in property transfers (e.g. GEPRAMS, GEOmark doing surveys). For subcontractors, also extract "percentage" (their share of total contract value, 0-100, or null if not stated) and "subcontract_subject" (what they do, short phrase in Slovak, or null). Look for these in appendix tables ("Zoznam subdodávateľov"), inline text, or anywhere the percentage share is mentioned.
```

**Step 3: Add rules for subcontracting fields**

In `extract_contracts.py`, in the Rules section (after line 120, the IČO garbled text rule), add:

```
  - "percentage" and "subcontract_subject" fields ONLY apply to entities with role "subcontractor". Set both to null for all other roles.
  - For "percentage", extract the numeric share of total contract value (0-100). Ignore percentages that refer to DPH/VAT rates, zmluvná pokuta rates, discount rates, co-financing shares, or Russian sanctions thresholds (Article 5k, Regulation 833/2014).
- subcontracting_mentioned: set to true if the contract text discusses subcontracting in any way (subdodávateľ, subdodávka, zoznam subdodávateľov), even if no named subcontractor is found. Set to false otherwise.
```

**Step 4: Verify prompt compiles**

Run: `uv run python -c "from extract_contracts import SYSTEM_PROMPT; print(len(SYSTEM_PROMPT))"`

Expected: prints a number (no import error).

**Step 5: Commit**

```bash
git add extract_contracts.py
git commit -m "feat: extend prompt with subcontractor percentage fields

Add percentage and subcontract_subject to subcontractor hidden_entities.
Add subcontracting_mentioned top-level boolean. Add rules to ignore
DPH/VAT/penalty/sanctions percentages."
```

---

### Task 2: Add flat DB columns and --force flag

**Files:**
- Modify: `extract_contracts.py:265-283` (argparse section)
- Modify: `extract_contracts.py:293-298` (skip logic)
- Modify: `extract_contracts.py:380-394` (db_row construction)

**Step 1: Add --force argument**

In `extract_contracts.py`, after the `--workers` argument (line 282), add:

```python
    parser.add_argument("--force", action="store_true", help="Re-extract even if JSON already exists")
```

**Step 2: Update skip logic to respect --force**

In `extract_contracts.py`, change the skip logic (lines 293-298) from:

```python
    # Skip already-extracted files
    already_done = set(f.replace(".json", ".txt") for f in os.listdir(output_dir) if f.endswith(".json"))
    to_process = [f for f in files if f not in already_done]
```

to:

```python
    # Skip already-extracted files (unless --force)
    if args.force:
        already_done = set()
    else:
        already_done = set(f.replace(".json", ".txt") for f in os.listdir(output_dir) if f.endswith(".json"))
    to_process = [f for f in files if f not in already_done]
```

**Step 3: Add new flat columns to db_row**

In `extract_contracts.py`, in the db_row dict (after `iban_count` line), add these three lines:

```python
                        "subcontracting_mentioned": extraction.get("subcontracting_mentioned", False),
                        "subcontractor_count": len([e for e in extraction.get("hidden_entities", []) if e.get("role") == "subcontractor"]),
                        "subcontractor_max_percentage": max((e.get("percentage") or 0 for e in extraction.get("hidden_entities", []) if e.get("role") == "subcontractor"), default=None),
```

**Step 4: Fix the max() logic for None-safety**

The `max()` above returns 0 when all percentages are null. Use a helper instead. Before the `db_row` dict, add:

```python
                    subcontractors = [e for e in extraction.get("hidden_entities", []) if e.get("role") == "subcontractor"]
                    sub_pcts = [e["percentage"] for e in subcontractors if e.get("percentage") is not None]
```

Then in db_row use:

```python
                        "subcontracting_mentioned": extraction.get("subcontracting_mentioned", False),
                        "subcontractor_count": len(subcontractors),
                        "subcontractor_max_percentage": max(sub_pcts) if sub_pcts else None,
```

**Step 5: Verify it runs (dry-run)**

Run: `uv run python extract_contracts.py --dry-run --limit 5`

Expected: prints file count, no errors.

**Step 6: Commit**

```bash
git add extract_contracts.py
git commit -m "feat: add subcontractor DB columns and --force flag

Add subcontracting_mentioned, subcontractor_count, and
subcontractor_max_percentage flat columns to extractions table.
Add --force flag to re-extract existing files."
```

---

### Task 3: Run gold set evaluation (5 files)

**Files:**
- No code changes — this is a validation step.

**Step 1: Extract the 3 positive gold set files**

Run:

```bash
uv run python extract_contracts.py --force --file 6573916.txt
uv run python extract_contracts.py --force --file 6570430.txt
uv run python extract_contracts.py --force --file 6571913.txt
```

**Step 2: Inspect positive results**

Run:

```bash
for f in 6573916 6570430 6571913; do
    echo "=== $f ==="
    uv run python -c "
import json
ext = json.load(open('data/extractions/${f}.json'))
print('subcontracting_mentioned:', ext.get('subcontracting_mentioned'))
subs = [e for e in ext.get('hidden_entities', []) if e.get('role') == 'subcontractor']
print(f'subcontractors: {len(subs)}')
for s in subs:
    print(f'  {s.get(\"name\")} — {s.get(\"percentage\")}% — {s.get(\"subcontract_subject\")}')
"
done
```

Expected: `subcontracting_mentioned` is true for all three. Subcontractor entries may or may not have percentage values (depends on whether the LLM can parse the appendix tables).

**Step 3: Extract 2 negative control files**

Run:

```bash
uv run python extract_contracts.py --force --file 6574089.txt
uv run python extract_contracts.py --force --file 6576846.txt
```

**Step 4: Inspect negative results**

Run:

```bash
for f in 6574089 6576846; do
    echo "=== $f ==="
    uv run python -c "
import json
ext = json.load(open('data/extractions/${f}.json'))
print('subcontracting_mentioned:', ext.get('subcontracting_mentioned'))
subs = [e for e in ext.get('hidden_entities', []) if e.get('role') == 'subcontractor']
print(f'subcontractors: {len(subs)}')
for s in subs:
    print(f'  {s.get(\"name\")} — {s.get(\"percentage\")}% — {s.get(\"subcontract_subject\")}')
"
done
```

Expected: `subcontracting_mentioned` is false. No subcontractor entries. No DPH/penalty percentages leaking into subcontractor fields.

**Step 5: Check DB columns**

Run:

```bash
uv run python -c "
import sqlite_utils
db = sqlite_utils.Database('crz.db')
for zid in [6573916, 6570430, 6571913, 6574089, 6576846]:
    row = db.execute('select subcontracting_mentioned, subcontractor_count, subcontractor_max_percentage from extractions where zmluva_id = ?', [zid]).fetchone()
    print(f'  {zid}: mentioned={row[0]} count={row[1]} max_pct={row[2]}')
"
```

Expected: positive files show `mentioned=1`, negative files show `mentioned=0`.

**Step 6: Commit evaluation notes (if results look good)**

No code commit — this is a checkpoint. If results are bad, iterate on the prompt in Task 1 before proceeding.

---

### Task 4: Run targeted extraction on subdodávateľ-mentioning files

**Files:**
- No code changes — this is an extraction run.

**Step 1: Build the file list**

Run:

```bash
grep -rl -i 'subdod' data/texts/*.txt | sed 's|.*/||' | sort > /tmp/subdod_files.txt
wc -l /tmp/subdod_files.txt
```

Expected: ~882 files.

**Step 2: Re-extract those files with --force**

Run each file through the extractor. Since `--file` only accepts one file, use a loop or pass them as the file list. The simplest approach: temporarily move non-subdodávateľ JSONs aside, or just run with --force on the full set and accept it re-extracts all.

Better approach — run with a small script:

```bash
cat /tmp/subdod_files.txt | while read f; do
    uv run python extract_contracts.py --force --file "$f" --workers 1
done
```

Or, faster — modify the approach: just run the full extractor with --force. Since we only want ~882 files, this wastes some API calls. Instead, for the test, run with --force and --limit on just the subdodávateľ files.

Pragmatic approach:

```bash
uv run python -c "
import subprocess, os
files = open('/tmp/subdod_files.txt').read().strip().split('\n')
print(f'Re-extracting {len(files)} files with subcontractor language')
# Delete their existing JSONs so the normal extractor picks them up
for f in files:
    jf = f'data/extractions/{f.replace(\".txt\", \".json\")}'
    if os.path.exists(jf):
        os.remove(jf)
print('Cleared existing JSONs')
"
uv run python extract_contracts.py
```

This clears the JSONs for subdodávateľ-mentioning files and lets the normal parallel extractor re-process them.

**Step 3: Inspect aggregate results**

Run:

```bash
uv run python -c "
import sqlite_utils
db = sqlite_utils.Database('crz.db')
print('subcontracting_mentioned distribution:')
for row in db.execute('select subcontracting_mentioned, count(*) from extractions group by subcontracting_mentioned').fetchall():
    print(f'  {row[0]}: {row[1]}')
print()
print('subcontractor_count distribution:')
for row in db.execute('select subcontractor_count, count(*) from extractions where subcontractor_count > 0 group by subcontractor_count order by subcontractor_count').fetchall():
    print(f'  {row[0]} subcontractors: {row[1]} contracts')
print()
print('subcontractor_max_percentage distribution:')
for row in db.execute('select subcontractor_max_percentage, count(*) from extractions where subcontractor_max_percentage is not null group by subcontractor_max_percentage order by subcontractor_max_percentage').fetchall():
    print(f'  {row[0]}%: {row[1]} contracts')
"
```

**Step 4: Spot-check a few results with high percentages**

Run:

```bash
uv run python -c "
import sqlite_utils, json
db = sqlite_utils.Database('crz.db')
rows = db.execute('''
    select zmluva_id, subcontractor_max_percentage, extraction_json
    from extractions
    where subcontractor_max_percentage is not null
    order by subcontractor_max_percentage desc
    limit 5
''').fetchall()
for zid, pct, ej in rows:
    ext = json.loads(ej)
    subs = [e for e in ext.get('hidden_entities', []) if e.get('role') == 'subcontractor']
    print(f'{zid}: max_pct={pct}%')
    for s in subs:
        print(f'  {s.get(\"name\")} — {s.get(\"percentage\")}% — {s.get(\"subcontract_subject\")}')
    print()
"
```

Manually verify a few against the source text files to check for false positives.

**Step 5: Commit**

```bash
git add extract_contracts.py
git commit -m "chore: re-extract subdodávateľ files with new prompt

Targeted re-extraction of ~882 files mentioning subcontractors
to populate percentage and subcontract_subject fields."
```

---

### Task 5: Update docs

**Files:**
- Modify: `README.md`
- Modify: `docs/plans/2026-03-07-open-dataset-deployment.md` (if it references extraction schema)

**Step 1: Update README extraction field list**

In `README.md`, in the extraction pipeline section, update the extracted fields sentence to include subcontracting:

```
Extracted fields include: service category, actual subject, hidden
entities (with subcontractor percentages), penalties, penalty asymmetry,
signatories, duration, funding source, bank accounts, and more.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: mention subcontractor percentages in README"
```
