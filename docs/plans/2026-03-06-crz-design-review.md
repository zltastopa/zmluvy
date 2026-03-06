# CRZ Smart Contracts -- Design Review

**Reviewer**: Senior Code Reviewer (automated)
**Date**: 2026-03-06
**Document under review**: `2026-03-06-crz-smart-contracts-design.md`
**Data examined**: `2026-03-04.xml` (2,794 records), CRZ web screenshots, sample PDFs

---

## Executive Summary

The design document presents a well-structured, phased approach to a real
problem. The problem statement is accurate, the phasing is sensible, and the
target audience (investigative journalists) is clearly defined. However, the
document contains **several factual errors in its cost and throughput
calculations**, **misses critical fields from the actual XML schema**, and
**under-specifies the hardest parts** (the agentic interface, the daily export
semantics, and the Vestnik integration) while over-specifying the easy parts
(the REST API, the database schema).

The most significant risk is not technical -- it is that **metadata-only
classification may not deliver enough value for journalists** before Phase 2
(PDF processing) is complete, and Phase 2 has a multi-month timeline that could
kill momentum.

---

## 1. Cost Estimates Are Wrong by an Order of Magnitude

**Severity: CRITICAL**

The design claims classification will cost ~$0.001 per contract and ~$5,500 for
the full 5.5M backfill. This is off by roughly 10x.

Actual Haiku 4.5 pricing (as of early 2026): $0.25/MTok input, $1.25/MTok
output. For the prompt described in the document (~200 tokens input, ~50 tokens
output per contract), the cost is approximately **$0.0001 per contract**, not
$0.001. That means:

| Item | Design estimate | Actual estimate |
|------|----------------|-----------------|
| Backfill (5.5M, unbatched) | ~$5,500 | ~$620 |
| Backfill (5.5M, batched 100/call) | ~$5,500 | ~$390 |
| Daily (2,800 contracts) | ~$2.80 | ~$0.31 |
| Monthly | ~$84 | ~$9.50 |

This is good news for the budget, but bad news for the document's credibility.
If the cost estimates are wrong by 10x in the favorable direction, what else is
wrong? The document should show its arithmetic: token counts, pricing per
million tokens, batch amortization.

**Additionally**, the document says "Process in batches of 100 contracts per API
call (using batch API)" but conflates two different things: (a) putting multiple
contracts in a single prompt, and (b) using the Anthropic Batch API (which
submits many independent requests at 50% cost). These have very different
implications for latency, error handling, and prompt design. Clarify which is
meant, or both.

**Recommendation**: Redo all cost estimates with explicit token math. Consider
that the Batch API gives 50% discount but has 24-hour turnaround, which is fine
for backfill but not for daily incremental processing.

---

## 2. The Daily Export Is Not What the Document Thinks It Is

**Severity: CRITICAL**

The document states: "Each daily ZIP contains a single XML file with all changes
from that day." Analysis of the actual 2026-03-04 export reveals this is
**incomplete and misleading**:

- Of 2,794 records, **99 contracts have old contract `chan` dates but
  2026-03-04 attachment `chan` dates**. These are contracts from 2016-2022
  whose PDFs were re-processed or re-uploaded on March 4, 2026, but whose
  contract metadata did not change.

- The export includes contracts where **only the attachment changed**, not the
  contract itself. The deduplication strategy ("use contract `ID` as primary
  key, keep the most recent version") will overwrite perfectly good contract
  data with identical data, but more importantly, will not correctly track
  **what changed and when**.

- **The 2026-03-05.zip is a 0-byte file.** Daily exports can be empty or
  missing. The pipeline must handle this gracefully. This is not mentioned in
  the error handling section.

- The document does not discuss what the `chan` field on attachments means
  versus the `chan` field on contracts. These are independent timestamps.
  The export trigger appears to be: "any `chan` timestamp (contract-level or
  attachment-level) falls on this date."

**Recommendation**: The ingestion logic needs to be smarter than simple upsert.
It should:
1. Track both contract-level and attachment-level change timestamps separately
2. Handle empty/missing daily exports without alerting as errors
3. Understand that a contract appearing in a daily export may mean only its
   attachment metadata changed (e.g., PDF re-signed or migrated to new storage)

---

## 3. The XML Schema Is Incomplete in the Design Document

**Severity: MAJOR**

The design document lists a subset of fields in its example XML. The actual XML
contains **10 additional fields** not mentioned anywhere:

| Field | Present in data | In design doc | Notes |
|-------|----------------|---------------|-------|
| `id` (lowercase) | Yes, always 0 or internal ID | No | Different from `ID` (uppercase). Always differs from `ID`. Often 0. Unclear purpose. |
| `poznamka` | Yes, 177/2794 non-empty | No | Free-text notes, often contain additional service descriptions ("auditorske sluzby", "mesacny najom"). **High classification signal.** |
| `potv_ziadost` | Yes, values 1 or 5 | No | Confirmation request status. Unclear meaning. |
| `potv_datum` | Yes | No | Confirmation date |
| `zdroj` | Yes, values 0/1/2/3 | No | Source system. ~50/50 split between 1 and 3. Could indicate whether contract came from central CRZ or decentralized system. |
| `potvrdenie` | Yes, 279/2794 | No | Confirmation PDF filename (e.g., `{id}_potvrdenie.pdf`) |
| `text_ucinnost` | Yes, 37/2794 | No | Textual description of when contract becomes effective |
| `popis` | Yes, 24/2794 | No | Description field |
| `popis_predmetu` | Yes, always empty in this export | No | Subject description -- potentially valuable if populated in other exports |
| `internapozn` | Yes, 29/2794 | No | Internal notes |
| `poznamka_zmena` | Yes, always empty | No | Change notes |
| `ref` | Yes, 63/2794 | No | Reference to parent contract or external system. Contains URLs, internal IDs, or contract numbers. **Critical for linking amendments to parent contracts.** |
| `datum` (signing date) | Yes | Mentioned in schema as `date_signed` | Good, but worth noting it is distinct from `datum_zverejnene` and `datum_ucinnost` |

The `poznamka` field is particularly important. It contains free-text notes like
"auditorske sluzby" (audit services), "mesacny najom" (monthly rent), "servisne
sluzby" (service services). This is **additional classification signal** that
the LLM prompt should use.

The `ref` field is critical for Phase 3's "Amendment inflation" anomaly
detection. Without it, you cannot link amendments to their parent contracts.
Some `ref` values are URLs, some are contract numbers, some are internal IDs --
this needs a parsing strategy.

**The attachment schema is also wrong.** The document shows only `dokument1` and
`velkost1`, but there are actually two parallel fields:

- `dokument` + `velkost`: Used by ~1,361 attachments (49%)
- `dokument1` + `velkost1`: Used by ~1,533 attachments (51%)
- **Never both at once.** Exactly one pair is populated per attachment.

The ingestion code must check both field pairs, or it will miss half the
attachments. The design document's schema only references `dokument1`.

**Recommendation**: Update the schema to include all fields. At minimum, add
`poznamka`, `ref`, `zdroj`, `potvrdenie`, `popis` to the database schema. Add
`poznamka` and `popis` to the classification prompt. Handle both `dokument`/
`dokument1` in attachment processing.

---

## 4. ICO Data Quality Is Worse Than Assumed

**Severity: MAJOR**

The design relies heavily on supplier ICO for cross-referencing (ORSR lookup,
NACE codes, anomaly detection). But the data reveals:

- **26.4% of contracts (738/2794) have empty supplier ICO.** These are
  contracts with individuals (natural persons), foreign entities, or simply
  missing data.
- **4 contracts have garbage in the ICO field** (e.g., "086 42 B", "42 001 3",
  "90050 Kr"). These appear to be zip code fragments pasted into the wrong
  field.
- Many suppliers are **natural persons** (e.g., "Sevcik Jan", "Comendant
  Marcel") who do not have ICOs and will not appear in the business register.

This means the suppliers table's `ico TEXT PRIMARY KEY` design is broken for a
quarter of all contracts. You need a strategy for:
1. Contracts with no supplier ICO (use a synthetic key?)
2. Contracts where the supplier is a natural person (different privacy rules
   apply under GDPR -- you cannot build profiles of individuals the same way
   you can for companies)
3. Fuzzy matching of supplier names when ICO is missing but the same entity
   appears under slightly different name spellings

The "500K unique ICOs estimated" figure should be verified. If 26% of contracts
lack an ICO, the actual number of unique ICOs is lower, but the number of
unique *suppliers* is higher (because you need name-based dedup for non-ICO
entities).

**Recommendation**: The suppliers table needs a composite or surrogate key, not
just ICO. Consider a `supplier_id SERIAL` PK with a unique constraint on ICO
where non-null, plus a separate name-based dedup strategy for individuals.
Document the GDPR implications of profiling natural persons.

---

## 5. Metadata-Only Classification: The 70-85% Estimate Is Untested

**Severity: MAJOR**

The document claims 70-85% classification accuracy from metadata alone. This
number appears to be a guess, not an empirical measurement. The document
correctly identifies this in the risks section ("Pilot on 1000 contracts
first") but then proceeds to build the entire Phase 1 architecture around the
assumption that it works.

Specific concerns:

**a) The "poznamka" field is not used in the classification prompt but contains
strong signal.** The current prompt uses: predmet, zs2, zs1, suma_zmluva,
rezort_name. Adding `poznamka` (notes) and `popis` (description) would
meaningfully improve accuracy for the subset that has them.

**b) The taxonomy may not match journalist mental models.** The 14-category
taxonomy looks reasonable from an engineering perspective, but have the
journalists at 360ka been asked how *they* would categorize contracts? The
difference between "how a developer categorizes" and "how a journalist searches"
is often significant. For example:
- Journalists might care about "osobne automobily" (personal vehicles) as a
  category -- this cuts across "transport" and "facilities"
- "Zmluva o dielo" is not a useful category but it is a distinct contract *type*
  under Slovak civil law. The taxonomy conflates service category with legal
  form.
- Cemetery plot rentals are 215/2794 (7.7%) of contracts. Lumping them under
  "other" loses resolution. Are they really "other" to a journalist
  investigating municipal spending?

**c) The confidence calibration example is misleading.** The document says
"Zmluva o dielo" + supplier "STRABAG" = construction (medium confidence). But
STRABAG is a well-known construction company. The real problem is "Zmluva o
dielo" + supplier "INPRO Slovakia s.r.o." -- a name that could be anything.
For these truly ambiguous cases, metadata-only classification may be closer to
coin-flip accuracy than 50%.

**d) The "escalate to Sonnet" strategy for low-confidence results is wasteful.**
If metadata is insufficient for Haiku, it is also insufficient for Sonnet.
Both models see the same input. Sonnet may produce a more articulate
*explanation* of why it is uncertain, but it will not magically produce a correct
category from the same ambiguous metadata. The escalation should go to
"needs PDF content," not to a bigger model.

**Recommendation**: Before building Phase 1, run a classification pilot:
1. Take 200 contracts, manually classify them (get the journalists to do this)
2. Run the LLM classifier on the same 200
3. Measure actual accuracy
4. Iterate on taxonomy and prompt until accuracy is acceptable
5. Only then build the pipeline

---

## 6. The Agentic Interface Is Under-Specified

**Severity: MAJOR**

Section 1.4 describes the agent in four bullet points and one sentence about
implementation ("standard tool-use pattern with Claude"). This is the
highest-value feature for journalists and gets the least design attention.

Missing specifications:

- **What tools does the agent have access to?** Just the REST API endpoints?
  Can it write SQL directly? Can it generate charts? Can it compare across time
  periods? The tool design determines what the agent can actually do.
- **How does it handle ambiguity in user queries?** "Marketing contracts" could
  mean category=marketing or predmet contains "marketing". These give very
  different results.
- **What is the conversation history strategy?** Does it maintain session
  state? Can a journalist say "now filter that to 2024 only"?
- **How does it handle data gaps?** When 25% of contracts lack supplier ICO,
  or when classification confidence is low, does the agent communicate this
  uncertainty?
- **What LLM model is the agent?** The technology stack says "Sonnet 4.6
  (agent)" but the cost estimates do not include agent usage costs. Agent
  conversations are expensive -- each query could easily be 5K-10K tokens with
  tool use. If 10 journalists make 50 queries/day, that is 500 queries/day at
  ~$0.10-0.20 each = $50-100/day = $1,500-3,000/month. This is not in the
  budget.
- **What language does the agent speak?** Slovak? English? Both? The examples
  are in Slovak, but the REST API is in English. Language mixing in tool calls
  is a known failure mode.

**Recommendation**: Design the agent tools explicitly. Write out the tool
schemas. Estimate agent conversation costs. Decide on language policy. Consider
whether a structured search UI (with filters) might serve 80% of journalist
needs without the complexity and cost of an LLM agent.

---

## 7. PDF Processing Timeline and Strategy

**Severity: MAJOR**

### 7a. The 5-month download timeline is probably unacceptable

The document calculates 153 nights for the full backfill at 1 req/s average
(nighttime only). But this ignores several things:

- **Why nighttime only?** The rate limit is 1 req/2s during the day. At a safe
  margin of 1 req/3s during daytime (14h) plus 3 req/s at night (10h), you get
  ~124,800 PDFs/day, completing in **44 days (~1.5 months)** instead of 5
  months. The document's own numbers show 3 req/s nighttime = 108,000/night,
  not 36,000.

- **The 36,000/night figure uses 1 req/s, not 3 req/s.** The document states
  the nighttime limit is 3 req/s, then calculates at 1 req/s "average." This
  inconsistency needs explanation.

- **Not all 5.5M contracts have unique attachments.** The document says "97%
  have exactly 1 attachment" but does not account for the 3% with zero or
  multiple attachments, or the possibility that some attachment IDs may be
  shared across contracts (reused PDFs). The total number of unique PDFs to
  download may be different from 5.5M.

### 7b. The 60-70% scan estimate needs validation

The claim that 60-70% of PDFs are scans is based on "sampling ~10 PDFs." Ten
PDFs from one day's export. This is not a statistically meaningful sample. The
scan ratio likely varies dramatically by:
- Time period (older = more scans)
- Institution size (municipalities = more scans, ministries = fewer)
- Contract type (employment contracts = often scanned, IT contracts = often
  digital)

### 7c. Storage concerns are understated

"Average extracted text ~5KB per contract" x 5.5M = 27.5GB for text. But the
PDFs themselves need to be stored somewhere during processing. Average PDF size
from the sample: velkost1 values range from 100KB to 33MB. If even a fraction
are large, you need significant scratch storage. The document does not address
whether PDFs are stored permanently or deleted after text extraction.

**Recommendation**: Fix the throughput calculation (use 24/7 downloading, not
nighttime only). Validate the scan ratio on a larger sample. Specify the PDF
storage strategy.

---

## 8. The Vestnik Integration Is Aspirational, Not a Plan

**Severity: MAJOR**

Section 3.3 describes cross-referencing CRZ with Vestnik (public procurement
journal) but provides almost no detail on how.

Analysis of the actual data shows:
- **Only 79 out of 2,794 contracts (2.8%) have a non-empty `uvo` field.** And
  of those 79, the values are heterogeneous: some are URLs to specific tender
  pages, some are URLs to the generic UVO search page, some say "nepodlieha
  VO" (not subject to procurement), and some are profile page links.
- The document acknowledges "the `uvo` field is often empty, so matching
  requires fuzzy joining on parties + amounts + dates." But it does not
  estimate the match rate or the false-positive rate of fuzzy matching.

Fuzzy matching on parties + amounts + dates across two large datasets is a
research problem, not a feature. It requires:
- Entity resolution for company names (different spellings, abbreviations,
  legal form variations)
- Amount matching with tolerance (CRZ amount vs. tender estimated value vs.
  actual award value -- these are often different)
- Date proximity matching (tender publication date vs. contract signing date
  vs. CRZ publication date -- these can differ by months)
- Validation that the match is correct (high false positive rate without human
  review)

Additionally, the Vestnik data access method is not specified. Does it have an
API? A daily export? Is scraping required? What is the data volume?

**Recommendation**: Either (a) scope Vestnik integration down to only the ~3%
of contracts that have explicit UVO references, which is a tractable problem, or
(b) acknowledge that general fuzzy matching is a Phase 4/research effort and
remove it from Phase 3 scope.

---

## 9. Missing: What the Daily Export Actually Contains Over Time

**Severity: MAJOR**

The bootstrap strategy says "Download all daily ZIPs from 2011-01-01 to present
(~5,500 files)." But the document does not address:

- **Do daily exports contain only that day's new/changed contracts, or
  cumulative data?** Evidence from the 2026-03-04 file shows it contains
  contracts originally published from 2016 through 2026, suggesting some
  cumulative or re-export behavior. If historical daily exports also contain
  re-exports, the total data volume across all 5,500 files may be much larger
  than 5.5M unique records. It might be 5.5M unique IDs across 20M+ total
  records.

- **What happens if you miss a day?** If the daily export for 2026-03-05 is
  0 bytes (as we observed), does the 2026-03-06 export catch up? Or are those
  contracts lost until they are re-exported?

- **Are there bulk/full exports available?** Processing 5,500 daily files to
  reconstruct the full database is fragile. If CRZ provides a full dump (even
  if outdated), it would be a much better bootstrap source.

- **The document says ~400KB average per ZIP.** But the 2026-03-04 ZIP is
  383KB containing 2,794 records. Over 15 years at ~2,800 records/day, that is
  ~15.3M records total (not accounting for dedup), suggesting the 5.5M figure
  is post-deduplication. The raw processing volume is 3x larger.

**Recommendation**: Before building the ingestion pipeline, download a few
historical daily exports from different years and analyze their structure. Check
if a full export endpoint exists. Estimate the actual raw data volume.

---

## 10. Database Schema Issues

**Severity: MINOR to MAJOR (varies)**

### 10a. The `attachments.file_size` column is `INTEGER` but should be `BIGINT`

The actual data shows attachment sizes up to 33,348,050 bytes (33MB). Integer
is fine for this, but some contract PDFs (e.g., large scanned documents) could
exceed 2GB. Use BIGINT to be safe.

### 10b. The `contracts.amount` column does not handle zero vs. null

40% of contracts have `suma_zmluva = 0`. This does not mean the contract is
free -- it often means the amount is unknown, variable, or not applicable (e.g.,
framework agreements, NDAs). Storing 0 as NUMERIC will make aggregate queries
(average contract value, total spending) incorrect unless you filter. The schema
should distinguish between "amount is zero" and "amount is not specified."
Consider using NULL for unspecified amounts.

### 10c. The `date_valid_until` handling of `0000-00-00`

70% of contracts (1,957/2,794) have `datum_platnost_do = 0000-00-00`. This is
not a valid date in PostgreSQL. The ingestion code must convert this to NULL.
This is straightforward but not mentioned in the document.

### 10d. Missing `poznamka` and `ref` columns

As noted in section 3, several fields with classification or linking value are
missing from the schema.

### 10e. The `embedding vector(1024)` column

The document does not specify which embedding model will be used or why 1024
dimensions was chosen. If using a Voyage or OpenAI embedding model, the
dimensions might be different (e.g., text-embedding-3-small is 1536 by default).
This affects the ivfflat index configuration (nlist parameter depends on data
volume -- for 5.5M rows, nlist should be ~2,345 using the sqrt(n) heuristic).
More importantly, the document does not justify *why* semantic embeddings are
needed. The classification and full-text search should cover most use cases.
Embeddings add complexity and storage (~22GB for 5.5M x 1024 x 4 bytes) for
unclear incremental value.

### 10f. The `raw_xml JSONB` column

Storing the raw XML as JSONB means converting XML to JSON during ingestion,
which loses information (attribute vs. element distinction, ordering, empty
elements vs. missing elements). If the goal is auditability, store the raw XML
as TEXT. If the goal is queryability, JSONB is fine but acknowledge the lossy
conversion.

**Recommendation**: Fix the type issues. Add NULL handling documentation.
Justify or remove the embedding column. Store raw XML as TEXT if auditability
is the goal.

---

## 11. Missing: Existing Tools and Competitive Landscape

**Severity: MAJOR**

The document's "Open Questions" section asks about existing tools but does not
answer the question. This should be researched before committing to building
from scratch:

- **otvorenezmluvy.sk** -- Open Contracts Slovakia. This project has been
  scraping and analyzing CRZ data since at least 2015. What does it already
  provide? Does it have an API? Could it be a data source instead of building
  our own ingestion pipeline?

- **datanest.sk / ekosystem.slovensko.digital** -- Slovak open data ecosystem.
  Some CRZ data may already be available in cleaned, structured form.

- **Transparency International Slovakia** -- They have done procurement
  analysis work. What tools/datasets do they use?

- **ARES (Czech Republic)** -- Similar system in Czechia. Have they solved the
  classification problem? Can we learn from their approach?

If otvorenezmluvy.sk already provides structured, searchable CRZ data, then
the value of this project shifts from "basic data access" to "intelligent
classification and anomaly detection" -- which changes the MVP significantly.

**Recommendation**: Research existing tools before finalizing the design. If
otvorenezmluvy.sk provides basic structured data, start from Phase 1.2 (LLM
classification) instead of Phase 1.1 (ingestion).

---

## 12. Missing: Testing and Validation Strategy

**Severity: MAJOR**

The document has no testing strategy whatsoever. For a system that produces
classifications used by journalists for public accountability reporting, this
is a significant gap:

- **Classification accuracy measurement**: How will you know if the LLM is
  getting it right? You need a labeled evaluation set (gold standard) of at
  least 500 contracts, manually classified by domain experts (the journalists).
- **Regression testing**: When the prompt changes, or the model is upgraded
  (Haiku 4.5 -> 5.0), how do you verify accuracy did not degrade?
- **Data pipeline testing**: How do you verify that XML parsing handles all
  edge cases (empty fields, malformed ICOs, dual dokument/dokument1 fields,
  0000-00-00 dates)?
- **Integration testing**: How do you verify that the daily pipeline runs
  correctly end-to-end?

**Recommendation**: Add a "Testing Strategy" section. Define the golden
evaluation set, the accuracy measurement methodology, and the CI/CD pipeline
for the classification prompt.

---

## 13. Minor Issues and Suggestions

### 13a. The `rezort` field is not a ministry ID (MINOR)

The document says `rezort` is a "Ministry/resort ID." But the actual values
(e.g., 114692, 6215909) do not correspond to any known ministry numbering. This
appears to be an internal CRZ identifier for the publishing institution, not a
ministry. The web UI shows "Subjekty verejnej spravy" (Public administration
entities) as the rezort label, confirming it is the *publishing institution*,
not the parent ministry. The mapping from rezort ID to human-readable name
needs to be obtained (likely from the CRZ web interface or a separate lookup
table).

### 13b. The `dokument` vs `dokument1` split (MINOR)

As noted, attachments use either `dokument`+`velkost` or `dokument1`+`velkost1`,
never both. This likely represents two different storage systems (old vs. new).
The URL pattern for downloading may differ between them. The design assumes
a single URL pattern (`/data/att/{id}.pdf`) but this may not work for all
attachments.

### 13c. The `zdroj` field should be investigated (SUGGESTION)

The `zdroj` (source) field has values 0, 1, 2, 3 with a roughly 50/50 split
between 1 and 3. This likely indicates the subsystem that published the
contract (e.g., central CRZ vs. municipal eCRZ). It could be useful for
filtering or for understanding data quality differences between sources.

### 13d. Celery may be overkill for the task queue (SUGGESTION)

The document specifies Celery + Redis for the task queue. For a pipeline that
runs nightly and processes ~3,000 records, this adds significant operational
complexity (Redis server, Celery workers, flower monitoring). Consider starting
with a simpler approach: a Python script run by cron, using PostgreSQL-backed
job tracking (advisory locks or a simple `status` column). Graduate to Celery
only when the workload demands it.

### 13e. The ivfflat index type (SUGGESTION)

For 5.5M vectors, consider HNSW instead of ivfflat. HNSW provides better
recall at similar speed and does not require a separate build step. It uses
more memory but produces better results for approximate nearest neighbor
queries.

### 13f. Slovak full-text search configuration (SUGGESTION)

The document mentions "Slovak-aware" full-text search and a `search_vector
tsvector` column, but does not specify the text search configuration.
PostgreSQL does not ship with a Slovak dictionary by default. You will need
to either (a) use the `simple` configuration (no stemming), (b) install the
`hunspell` Slovak dictionary, or (c) use the `unaccent` extension plus
a generic stemmer. This is a non-trivial decision that affects search quality.

---

## 14. Prioritization Feedback

**Severity: SUGGESTION**

The phasing (metadata -> PDFs -> cross-source) is logical but I would
recommend two adjustments:

**a) Pull forward a minimal PDF extraction pilot into Phase 1.** Even
processing just the born-digital PDFs (which require only `pdftotext`, no
OCR) would cover 20-30% of contracts and could be done in days, not months.
This would let you validate the "does full text improve classification?"
hypothesis before committing to the OCR infrastructure.

**b) Pull forward ORSR/business register enrichment into Phase 1.** Looking up
NACE codes for suppliers is a straightforward API call and dramatically
improves classification accuracy (the document's own example: car repair
company winning a marketing contract). Do this before Phase 2's expensive
PDF processing, not after.

**c) Defer the embedding/vector search until there is a concrete use case.**
The design adds pgvector, embeddings, and a semantic search endpoint without
a clear user story. "Find contracts similar to this one" is cool but may not
be what journalists actually need. Build the keyword search and category
filters first, and add semantic search when someone asks for it.

---

## 15. Summary of Issues by Severity

### CRITICAL (must fix before proceeding)
1. Cost estimates are wrong by ~10x (Section 1)
2. Daily export semantics are misunderstood; dedup strategy is incomplete
   (Section 2)

### MAJOR (significant risk to project success)
3. XML schema is incomplete -- 10+ fields missing, dual attachment fields
   (Section 3)
4. ICO data quality -- 26% empty, schema cannot handle it (Section 4)
5. Classification accuracy estimate is untested (Section 5)
6. Agentic interface is under-specified and unbudgeted (Section 6)
7. PDF download timeline calculation is inconsistent (Section 7)
8. Vestnik integration is aspirational, not actionable (Section 8)
9. Daily export behavior over time is not understood (Section 9)
10. No testing or validation strategy (Section 12)
11. Competitive landscape not researched (Section 11)

### MINOR (should fix)
12. Database schema type issues and NULL handling (Section 10)
13. Rezort field semantics incorrect (Section 13a)
14. Attachment download URL pattern may vary (Section 13b)

### SUGGESTIONS (nice to have)
15. Investigate `zdroj` field meaning (Section 13c)
16. Simplify task queue (Section 13d)
17. Use HNSW instead of ivfflat (Section 13e)
18. Plan Slovak full-text search configuration (Section 13f)
19. Re-prioritize: pull forward pdftotext and ORSR, defer embeddings
    (Section 14)

---

## Recommended Next Steps

1. **Fix the cost math.** Show token counts and per-token pricing explicitly.
2. **Download 5-10 historical daily exports** from different years and analyze
   their structure to understand the export semantics before building ingestion.
3. **Run the classification pilot** (200 manually-labeled contracts) before
   building the pipeline.
4. **Talk to the journalists** about taxonomy -- give them 50 sample contracts
   and ask them to categorize them. See if your taxonomy matches their mental
   model.
5. **Research existing tools** (otvorenezmluvy.sk, datanest.sk) to avoid
   rebuilding what exists.
6. **Update the schema** to include all XML fields and handle data quality
   issues (empty ICOs, dual attachment fields, 0000-00-00 dates).
