# CRZ Design Document v2 -- Review

**Reviewer**: Senior Code Reviewer
**Date**: 2026-03-06
**Document under review**: `2026-03-06-crz-smart-contracts-design-v2.md`
**Compared against**: `2026-03-06-crz-design-review.md` (19 issues from v1 review)

---

## Executive Summary

The v2 design document is a substantial improvement over v1. Of the 19 issues
identified in the v1 review, **14 are fully fixed, 4 are partially fixed, and
1 is not fixed**. The document is now honest about data quality, realistic
about costs, and disciplined about scope (Vestnik deferred, embeddings
removed, prerequisites gated).

The remaining gaps are concentrated in two areas: (a) details around the
ingestion strategy that still need empirical validation before building, and
(b) a few schema/operational issues that will bite during implementation if
not addressed now.

**Overall verdict**: The document is ready to move into implementation with
one prerequisite -- the open "partially fixed" items below should be resolved
during the P1-P3 prerequisite steps (which the document already plans), not
left for discovery during coding.

---

## Part A: Issue-by-Issue Verification

### CRITICAL Issues

**Issue 1: Cost estimates wrong by ~10x (Section 1 of review)**
**Status: FIXED**

v2 Section 1.3 now includes explicit token math: ~250 input tokens, ~60
output tokens, Haiku 4.5 at $0.25/$1.25 per MTok, yielding ~$0.000138 per
contract. The Batch API discount is correctly applied to the backfill
($379) while daily incremental uses the standard API ($12/month). The
distinction between "batching multiple contracts in one prompt" and "using
the Anthropic Batch API" is now clear -- v2 uses the Batch API (independent
requests at 50% discount), not multi-contract prompts.

No new problems introduced.

---

**Issue 2: Daily export semantics misunderstood (Section 2 of review)**
**Status: PARTIALLY FIXED**

v2 improves this in several places:

- The Access Methods table (Section "Data Landscape") now notes that daily
  exports "include re-processed old contracts, not just new" and "can be
  0 bytes on some days."
- Section 1.1 tracks contract-level and attachment-level `chan` timestamps
  independently and upserts only when contract `chan` is newer.
- The Key Data Quality Issues table notes "Re-exported old contracts in
  daily export ~3-5%."

**What is still missing**: The document still does not address the core
question from the review: *what happens when you miss a day?* If 2026-03-05
is 0 bytes, does 2026-03-06 contain the contracts that would have been in
2026-03-05? Or are they lost until they happen to be re-exported? The upsert
strategy ("update only if contract `chan` is newer") is correct for dedup but
does not answer whether the bootstrap process can tolerate gaps in the daily
export archive. This is precisely what prerequisite P2 (Historical Export
Analysis) should answer, but the document does not list this as a specific
question for P2 to resolve. P2 says to verify "same XML schema across years"
and "how many unique contract IDs appear across multiple daily exports" but
not "what happens around gap days."

Additionally, the review raised the possibility that a full/bulk export
endpoint might exist (which would make the 5,500-file bootstrap unnecessary).
v2 does not address this.

**Recommendation**: Add "Do daily exports catch up after a gap day?" and
"Does a full CRZ export exist?" as explicit questions in prerequisite P2.

---

### MAJOR Issues

**Issue 3: XML schema incomplete -- 10+ fields missing (Section 3 of review)**
**Status: FIXED**

v2 Section "Complete XML Schema" now documents all fields from the actual
data, including `poznamka`, `ref`, `zdroj`, `popis`, `popis_predmetu`,
`internapozn`, `text_ucinnost`, `poznamka_zmena`, `potvrdenie`,
`potv_ziadost`, `potv_datum`, `id` (lowercase), and `uvo`. Population
percentages are annotated. The dual `dokument`/`dokument1` fields are
explicitly documented with the "never both at once" constraint. The
database schema in Section 1.2 includes columns for all of these.

The attachment filename resolution code snippet in Section 1.1 correctly
checks both fields.

No new problems introduced.

---

**Issue 4: ICO data quality -- 26% empty, schema cannot handle it
(Section 4 of review)**
**Status: FIXED**

v2 redesigns the suppliers table with a surrogate `id SERIAL PRIMARY KEY`
instead of `ico TEXT PRIMARY KEY`. The `ico` column has a `UNIQUE`
constraint but allows NULL. The `is_natural_person BOOLEAN` column is added.
The contracts table documents `supplier_ico` as "NULL for 26% of records."

One minor note: the `CONSTRAINT unique_ico UNIQUE (ico)` in PostgreSQL
will actually allow multiple NULL values (because NULLs are not considered
equal for unique constraints in standard SQL and PostgreSQL follows this),
which is the correct behavior here. Good.

**Small gap**: The review also mentioned fuzzy name-based deduplication for
suppliers without ICO. v2 adds a GIN index on supplier names
(`idx_suppliers_name`) which is a good foundation, but does not describe
an actual dedup strategy. This is acceptable for Phase 1 -- name dedup is
hard and likely a Phase 2/3 concern -- but worth noting.

**GDPR**: The review asked for documentation of GDPR implications. v2 adds
`is_natural_person` and notes "Suppliers are natural persons ~20%" in the
data quality table with "GDPR implications for profiling." This is a flag,
not a strategy. The document should state what the system will and will not
do with natural person data (e.g., "natural person suppliers are stored but
excluded from supplier profile pages and aggregate reporting"). This does
not block implementation but should be resolved before the UI is built.

---

**Issue 5: Classification accuracy estimate untested (Section 5 of review)**
**Status: FIXED**

v2 adds prerequisite P1 (Classification Pilot) as an explicit gate: "Do not
build the classification pipeline until this is done." The pilot involves
200 contracts, journalist-labeled, with a >75% accuracy target. The
taxonomy is explicitly marked as "to be finalized after classification pilot
with journalists."

The review's sub-points are also addressed:
- 5a (poznamka not in prompt): v2 prompt includes `poznamka` and `popis`.
- 5b (taxonomy may not match journalist mental models): v2 says "Use their
  categories to refine the taxonomy (their mental model, not ours)."
- 5c (confidence calibration misleading): Not explicitly addressed, but the
  pilot will surface this empirically, so it is implicitly covered.
- 5d (escalate to Sonnet is wasteful): v2 says "For confidence < 0.5, mark
  as 'needs_pdf_content' (don't escalate to bigger model -- same input,
  same ambiguity)." Directly addresses this.

No new problems introduced.

---

**Issue 6: Agentic interface under-specified (Section 6 of review)**
**Status: FIXED**

v2 Section 1.7 now includes:
- Five tool schemas with input parameters (search_contracts,
  get_contract_detail, get_supplier_profile, get_statistics, get_anomalies).
- Explicit model choice (Sonnet 4.6) with cost estimate showing the math:
  ~5,000 input + ~2,000 output tokens per query, $3/$15 per MTok,
  $0.045/query, 200 queries/day assumption = ~$270/month.
- Language policy ("Agent responds in Slovak, tool calls use English keys
  with Slovak values").
- Ambiguity handling with a concrete example of how the agent communicates
  uncertainty.

This is now sufficiently specified for implementation.

One small observation: the cost estimate assumes 10 users x 20 queries/day.
This seems reasonable for an early deployment but could scale significantly
if the tool is opened to a broader audience. The document should note at
what user count the agent costs become a concern (e.g., at 1,000
queries/day, agent cost would be ~$1,350/month). Not a blocker.

---

**Issue 7: PDF download timeline calculation inconsistent (Section 7 of
review)**
**Status: FIXED**

v2 Section 1.5 now calculates using both daytime and nighttime downloading:
- Daytime: 1 req/3s = ~16,800/day
- Nighttime: 2 req/s (safe margin under 3/s) = ~72,000/night
- Total: ~88,800 PDFs/day
- Full backfill: ~62 days (~2 months)

The calculation is internally consistent. The choice of 2 req/s nighttime
(not 3) as a safe margin is reasonable.

**New observation**: The document says "full backfill of unique attachments"
takes ~62 days, but does not state the total number of unique attachments.
5.5M contracts x 97% with attachments = ~5.3M attachments, minus potential
dedup of shared attachment IDs. At 88,800/day, 5.3M / 88,800 = ~60 days.
The math checks out.

The review's sub-points:
- 7b (60-70% scan estimate based on 10 PDFs): v2 does not claim a specific
  scan percentage for the full corpus. Instead, it takes the pragmatic
  approach of running pdftotext first and marking failures as `needs_ocr`.
  This sidesteps the estimation problem entirely. Good.
- 7c (PDF storage concerns): Still not explicitly addressed. The document
  says extracted text is stored but does not say whether downloaded PDFs
  are kept or deleted after extraction. This matters: at an average of
  ~500KB per PDF (conservative), 5.3M PDFs = ~2.6TB of scratch storage.
  The document should specify: download, extract text, delete PDF (or
  keep only for Phase 2 OCR candidates).

**Recommendation**: Add a sentence about PDF storage lifecycle: which PDFs
are kept, which are deleted after text extraction.

---

**Issue 8: Vestnik integration aspirational (Section 8 of review)**
**Status: FIXED**

v2 scopes Vestnik down to Phase 2 and limits it to the ~2.8% of contracts
with explicit `uvo` field values: "Parse the UVO URLs/IDs and link to the
corresponding Vestnik records. Do not attempt fuzzy matching." This is a
tractable, well-scoped task. The review explicitly recommended this as
option (a).

No new problems introduced.

---

**Issue 9: Daily export behavior over time not understood (Section 9 of
review)**
**Status: PARTIALLY FIXED**

v2 adds prerequisite P2 (Historical Export Analysis): "Download 10 daily
exports from different years (2012, 2015, 2018, 2020, 2023, 2025) and
verify: Same XML schema across years? How many unique contract IDs appear
across multiple daily exports? Total volume estimate for full historical
bootstrap."

This is good and directly addresses the review's recommendation. However,
two questions from the review remain unanswered:

1. Whether a full/bulk export exists (as noted under Issue 2).
2. The review's estimate that raw processing volume across all 5,500 daily
   files may be ~15M records (not 5.5M), meaning 3x more XML parsing.
   This affects bootstrap time estimates. v2 does not address this, though
   P2 should surface it.

**Recommendation**: Add "estimate total raw records across all daily files
(may be much larger than 5.5M unique)" as an explicit P2 question.

---

**Issue 10: Database schema issues (Section 10 of review, 6 sub-items)**
**Status: FIXED (all 6 sub-items)**

- 10a (file_size INTEGER -> BIGINT): v2 uses `BIGINT` for
  `attachments.file_size`. Fixed.
- 10b (amount 0 vs NULL): v2 schema comments say "NULL = unknown, not
  free" and "0 -> NULL". Data quality table says "`suma_zmluva = 0` means
  unknown, not free -- must use NULL." Fixed.
- 10c (0000-00-00 date handling): v2 schema comment on `date_valid_until`
  says "0000-00-00 -> NULL." Fixed.
- 10d (missing poznamka and ref columns): v2 schema includes `notes`
  (poznamka), `parent_ref` (ref), and all other missing fields. Fixed.
- 10e (embedding vector(1024) unjustified): v2 removes the embedding
  column entirely and defers it: "Embeddings deferred until a concrete use
  case emerges" (Changes from v1, item 8). The ivfflat index is gone too.
  Fixed.
- 10f (raw_xml JSONB -> TEXT): v2 schema uses `raw_xml TEXT` with comment
  "Original XML (TEXT, not JSONB -- lossless)." Fixed.

No new problems introduced.

---

**Issue 11: Competitive landscape not researched (Section 11 of review)**
**Status: FIXED**

v2 adds prerequisite P3 (Competitive Landscape Research) that explicitly
lists otvorenezmluvy.sk, datanest.sk / ekosystem.slovensko.digital, and
Transparency International Slovakia. It also says "if they already provide
structured CRZ data, skip ingestion."

The review also mentioned ARES (Czech equivalent) as a learning opportunity.
v2 does not include this, which is fine -- it was a suggestion, not a
requirement.

No new problems introduced.

---

**Issue 12: No testing or validation strategy (Section 12 of review)**
**Status: FIXED**

v2 adds a "Testing Strategy" section covering:
- Classification evaluation: 500-contract golden set, accuracy metrics,
  regression testing, continuous monitoring (50 weekly spot-checks).
- Data pipeline testing: unit tests for edge cases, integration tests with
  sample ZIPs, monitoring alerts.
- API testing: pytest suite, load testing for <500ms on 5.5M rows.

This is sufficient for a design document. Implementation details (specific
test framework config, CI/CD pipeline) will come during development.

No new problems introduced.

---

### MINOR Issues

**Issue 13a: Rezort field semantics incorrect (Section 13a of review)**
**Status: FIXED**

v2 XML schema annotates `rezort` as "Publishing institution ID (NOT ministry
ID)" and the database schema comment says "rezort (institution ID, not
ministry)." The review also noted that a mapping from rezort ID to
human-readable name is needed. v2 does not include a `rezort` lookup table,
but the classification prompt uses `{rezort_name}`, implying the mapping
exists. This should be made explicit -- where does the rezort-to-name
mapping come from?

**Recommendation**: Add a note about how `rezort_name` is resolved (scraped
from CRZ web UI? Separate lookup table? Derived from contract data?).

---

**Issue 13b: Attachment download URL pattern may vary (Section 13b of
review)**
**Status: PARTIALLY FIXED**

v2 documents the dual `dokument`/`dokument1` fields thoroughly and includes
a `storage_system` column in the attachments table ('old' or 'new'). The
filename resolution code handles both fields.

However, the review's specific concern was that the **download URL pattern**
might differ between old-system and new-system attachments. v2 still shows
only one URL pattern in the Access Methods table:
`https://www.crz.gov.sk/data/att/{id}.pdf`. The document does not confirm
that this pattern works for both storage systems, or document what the
alternative URL pattern would be for old-system files.

**Recommendation**: During prerequisite P2 or early Phase 1 development,
test downloading attachments from both storage systems and document the URL
patterns.

---

**Issue 14: (This maps to Section 10 sub-items, already covered above)**

Note: The review's numbering in the summary (Section 15) lists issues 12-14
as minor. Issue 12 in the summary maps to Section 10 (database schema), 13
to Section 13a (rezort), and 14 to Section 13b (attachments). All are
addressed above.

---

### SUGGESTIONS

**Issue 15: Investigate `zdroj` field meaning (Section 13c of review)**
**Status: FIXED**

v2 includes `zdroj` in the XML schema with annotation "Source system: 1 or
3 (~50/50 split)" and adds `source_system SMALLINT` to the database schema.
Sufficient for now.

---

**Issue 16: Simplify task queue (Section 13d of review)**
**Status: FIXED**

v2 Technology Stack table says "Cron + Python scripts -- Simple. Graduate to
Celery only if needed." Celery + Redis are removed from Phase 1. Exactly
what the review suggested.

---

**Issue 17: Use HNSW instead of ivfflat (Section 13e of review)**
**Status: FIXED (by removal)**

v2 removes embeddings and vector search entirely, deferring them until a
concrete use case emerges. The ivfflat vs. HNSW question is moot. When
embeddings are added later, the HNSW recommendation should be revisited.

---

**Issue 18: Plan Slovak full-text search configuration (Section 13f of
review)**
**Status: FIXED**

v2 Technology Stack table says "PostgreSQL with `unaccent` + `simple` config
-- Slovak dictionary TBD (hunspell if available)." This acknowledges the
issue and provides a workable default (`simple` + `unaccent`) with a plan
to improve (hunspell). Sufficient for a design document.

---

**Issue 19: Re-prioritize -- pull forward pdftotext and ORSR, defer
embeddings (Section 14 of review)**
**Status: FIXED**

All three sub-recommendations are implemented:
- 14a (pdftotext in Phase 1): v2 Section 1.5 adds lightweight PDF
  extraction (pdftotext only, no OCR) to Phase 1.
- 14b (ORSR in Phase 1): v2 Section 1.4 adds ORSR business register
  enrichment to Phase 1.
- 14c (defer embeddings): v2 removes embeddings entirely from Phase 1.

No new problems introduced.

---

## Part B: New Problems Introduced by v2

### B1: The `suppliers.ico` UNIQUE constraint and name-only suppliers

**Severity: Minor**

The suppliers table has a `UNIQUE (ico)` constraint that allows NULLs. This
is correct for ICO-bearing entities. But for natural persons or entities
without ICO, there is no dedup mechanism. Two contracts with supplier
"Jan Novak" from different daily exports will create two separate supplier
rows with `ico = NULL`. Over 5.5M contracts with 26% missing ICOs, this
could create a large number of duplicate supplier entries.

This is not a schema error -- it is a design gap. The `idx_suppliers_name`
GIN index enables name-based lookup, but the document does not describe a
dedup process.

**Recommendation**: Acknowledge this as a known limitation in Phase 1. Add a
note that supplier dedup for non-ICO entities is a future improvement. For
Phase 1, the supplier table is primarily useful for ICO-bearing entities.

---

### B2: Missing `classification_runs` table

**Severity: Minor**

v1 had a `classification_runs` table tracking batch processing runs (date,
contracts processed, model used, cost, etc.). v2 drops this table entirely.
The testing strategy mentions "continuous monitoring" and "regression testing"
but without a runs table, there is no operational audit trail for
classification batches. When the prompt changes or the model is upgraded,
how do you know which contracts were classified with which version?

**Recommendation**: Either restore the `classification_runs` table or add
`classified_at TIMESTAMPTZ` and `classified_model TEXT` columns to the
contracts table so that classification provenance is tracked per-contract.
Per-contract tracking is arguably better since it survives partial runs.

---

### B3: The `amount` column transform (0 -> NULL) is lossy

**Severity: Minor**

v2 correctly identifies that `suma_zmluva = 0` means "unknown" and converts
it to NULL. But this is a one-way transform -- once converted, you cannot
distinguish between "the XML had 0" and "the XML field was missing." The
`raw_xml TEXT` column preserves the original, but querying it is expensive.

This matters less than it might seem (the original value is always in
`raw_xml`), but it is worth noting that any analysis that needs to
distinguish "explicitly zero" from "missing" will need to parse raw XML.

**Recommendation**: Consider storing the raw numeric value in a separate
column (e.g., `raw_amount NUMERIC`) alongside the cleaned `amount` column,
or simply document the transform clearly. The current design is acceptable
if the trade-off is understood.

---

### B4: Execution timeline is optimistic

**Severity: Observation (not a defect)**

The Recommended Execution Order estimates:
- Classification pilot: 1 week
- Historical export analysis: 2 days
- Competitive landscape research: 2 days
- Data ingestion pipeline: 1 week
- ORSR enrichment: 3 days
- Classification pipeline: 1 week
- API + basic search UI: 1 week
- Agentic interface: 1 week

Total: ~5 weeks of development time (excluding the 2-month PDF download).

This is plausible for a single experienced developer working full-time, but
tight. The prerequisites (P1-P3) depend on external parties (journalists for
classification, CRZ for historical data, research into existing tools) and
could easily block for weeks. The timeline does not account for iteration
cycles -- if the classification pilot fails the >75% target, the taxonomy
redesign and re-piloting could add 1-2 weeks.

This is not a document defect -- timelines are inherently uncertain -- but
worth noting for planning purposes.

---

## Part C: Summary of Remaining Gaps

These are the items that should be resolved before or during early
implementation:

| # | Gap | Where to resolve | Blocking? |
|---|-----|------------------|-----------|
| 1 | Daily export gap behavior (do exports catch up after 0-byte days?) | Prerequisite P2 | Yes, for bootstrap |
| 2 | Full/bulk CRZ export existence | Prerequisite P2 | No, but could simplify bootstrap |
| 3 | Raw record volume across all daily files (possibly 15M+, not 5.5M) | Prerequisite P2 | No, but affects time estimates |
| 4 | GDPR strategy for natural person suppliers | Before UI development | No (for pipeline) |
| 5 | Rezort-to-name mapping source | During ingestion development | No, but needed for classifier |
| 6 | Attachment download URL patterns for both storage systems | During PDF download development | No (for Phase 1 metadata) |
| 7 | PDF storage lifecycle (keep or delete after extraction?) | During Phase 1 PDF work | No (for pipeline) |
| 8 | Classification provenance tracking (runs table or per-contract) | During classifier development | No |

None of these are blocking in the sense that they prevent starting work.
They are all resolvable during the prerequisite steps or early development.

---

## Part D: Readiness Assessment

**Is v2 ready to become an implementation plan?**

**Yes, with the caveat that the three prerequisites (P1-P3) are genuine
gates, not formalities.** The document correctly identifies them as
prerequisites but does not emphasize strongly enough that the results of P2
and P3 could fundamentally change the implementation plan:

- If P3 reveals that otvorenezmluvy.sk already provides the structured data,
  the entire ingestion pipeline (Section 1.1) could be skipped.
- If P2 reveals that historical daily exports have a different schema or are
  missing years, the bootstrap strategy needs rethinking.
- If P1 (classification pilot) fails to reach 75% accuracy even after
  iteration, the core value proposition of the project needs reassessment.

The document should treat these prerequisites as decision points with
explicit go/no-go criteria and alternative paths, not just checkboxes.

**Bottom line**: The v2 document has addressed the critical and major issues
from the v1 review. The remaining gaps are minor and resolvable during
normal development. The design is solid enough to begin implementation,
starting with the three prerequisites.

---

## Summary Scorecard

| Severity | v1 Count | Fixed | Partially Fixed | Not Fixed |
|----------|----------|-------|-----------------|-----------|
| CRITICAL | 2 | 1 | 1 | 0 |
| MAJOR | 9 | 8 | 1 | 0 |
| MINOR | 3 | 2 | 1 | 0 |
| SUGGESTION | 5 | 5 | 0 | 0 |
| **Total** | **19** | **16** | **3** | **0** |

New issues introduced by v2: 4 (all Minor or Observation level).
