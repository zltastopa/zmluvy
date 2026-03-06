# Hackathon Suggestions -- Critical Review

**Reviewer**: Senior Code Reviewer
**Date**: 2026-03-06
**Document under review**: `2026-03-06-hackathon-suggestions.md`
**Context**: Open Data Heroes hackathon (March 7-8, 2026, Bratislava). 2-day event. Challenge by 360ka (investigative journalists). Target: tools to intelligently search Slovak government contracts from CRZ (5.5M+ contracts).
**Technical reference**: `2026-03-06-crz-smart-contracts-design-v2.md`

---

## Executive Summary

The suggestions document is well-structured and technically grounded. It
correctly identifies the CRZ daily XML export as the key data access
mechanism and proposes six concrete project ideas with realistic code
sketches. The document benefits significantly from the deep data
exploration already done (XML schema analysis, rate limit discovery,
attachment storage dual-field behavior).

However, the document underestimates several hackathon-specific risks:
LLM API latency during live demos, the gap between "parse XML" and
"have enough data to be impressive," and the tension between breadth
(6 suggestions) and depth (what a team can actually ship in ~16 working
hours). The prioritization section at the bottom is good but could be
sharper.

**Overall verdict**: The document provides a strong foundation.
Suggestion 1 (CRZ Classifier) is the correct anchor. But the
recommendations need tightening: teams should be warned about specific
failure modes, the "combine 1+3+6" recommendation is too ambitious for
a single team, and one high-impact idea is missing entirely.

---

## 1. Feasibility Analysis: Can Each Suggestion Be Built in a Weekend?

### Suggestion 1: CRZ Classifier -- FEASIBLE (4-8 hours)

This is the most realistic suggestion and the document correctly
identifies it as the "quickest path to demo." The 5-step build plan
(download XML, parse, classify, store, UI) is accurate.

**Where teams will get stuck**:
- Step 3 (LLM classification) at scale. Classifying even 1 day of
  contracts (~2,800) sequentially at ~1 second per API call = ~47
  minutes. Teams will need to parallelize or pre-classify before the
  demo. The document does not mention this.
- The code sketch uses the synchronous Anthropic client. A hackathon
  team unfamiliar with `asyncio` or the Batch API will hit this wall
  and either wait or reduce scope to 100 contracts.
- Building a "simple search UI" in Streamlit is genuinely fast (1-2
  hours) if the developer has used Streamlit before. If not, add 2
  hours for learning.

**Realistic scope**: 1-3 days of contracts classified, filterable in
Streamlit. Not "all marketing contracts from Ministry of Agriculture
over 10K in 2025" -- that requires much more data than a weekend
download provides.

**Recommendation**: Add a note about pre-classifying data the night
before the demo. Suggest using `asyncio` with `anthropic.AsyncAnthropic`
or pre-computing classifications for a fixed dataset of a few thousand
contracts. Also mention that the Anthropic Batch API (used in the design
doc) has a 24h turnaround -- too slow for hackathon iteration but
perfect for a Friday-night bulk run whose results are ready Saturday
morning.

---

### Suggestion 2: Supplier X-Ray -- FEASIBLE (6-10 hours)

Aggregating contracts by supplier ICO is straightforward SQL/pandas.
The ORSR enrichment (NACE codes) is the risky part.

**Where teams will get stuck**:
- ORSR API: The document says "Enrich with ORSR data" without specifying
  *how*. Is there a public API? A bulk download? Rate limits? The design
  doc (v2, Section 1.4) says "ORSR business register lookup" but does
  not give an endpoint. If there is no stable API, this step could
  consume the entire hackathon on scraping.
- 26.4% of contracts have no supplier ICO. The aggregation will have a
  large "unknown supplier" bucket that dilutes the analysis. The
  document does not mention this, though the design doc does.
- The anomaly flags (step 3) are conceptually simple but require joining
  against external data (company age from ORSR, NACE codes). Each join
  is a potential failure point.

**Realistic scope**: Aggregation by ICO with top-N suppliers per
institution. ORSR enrichment for maybe 50-100 companies (manual or
semi-automated). Anomaly detection limited to "same supplier, many
contracts" without NACE mismatch (which needs ORSR).

**Recommendation**: Decouple the ORSR enrichment from the core
suggestion. Present Supplier X-Ray as "aggregate CRZ data by supplier"
(doable) with ORSR enrichment as a stretch goal. If ORSR has no usable
API, the team should know this before committing.

---

### Suggestion 3: Contract Companion (AI Agent) -- RISKY (8-14 hours)

This depends on Suggestion 1 being done first (classified data in a
database), then building a tool-use agent on top. The tool-use pattern
(Claude + tools) is well-established but has subtle implementation
challenges.

**Where teams will get stuck**:
- Building the underlying database and API layer that the agent calls.
  The document lists `search_contracts`, `get_supplier_profile`,
  `get_statistics` as agent tools -- each of these is effectively a
  separate endpoint that needs to be implemented and tested. That is 3-5
  small APIs plus the agent orchestration.
- Agent hallucination during live demos. If the agent fabricates a
  contract number or misinterprets a query, the demo is worse than
  having no agent at all. Journalists and fact-checkers are the
  harshest possible audience for hallucination.
- Latency: a tool-use conversation with Claude involves multiple round
  trips (user query -> agent decides tool -> tool executes -> agent
  interprets result). Each round trip adds 2-5 seconds. A multi-step
  query could take 15-20 seconds. During a live demo, this feels
  painfully slow.
- Slovak language: The agent needs to understand queries in Slovak and
  map them to structured filters. This mostly works with Claude but
  edge cases will appear during demo.

**Realistic scope**: A CLI or simple chat UI where the agent can answer
basic questions about a small pre-loaded dataset. It will be impressive
when it works, frustrating when it does not. High risk, high reward.

**Recommendation**: If a team builds this, they should have 3-5
pre-tested "golden path" queries that they know work perfectly for the
demo, with live improvisation as a bonus. Never demo an agent cold.

---

### Suggestion 4: PDF Decoder -- PARTIALLY FEASIBLE (6-12 hours)

The document correctly scopes this to born-digital PDFs only. pdftotext
is fast and reliable for these.

**Where teams will get stuck**:
- Downloading enough PDFs within rate limits. At 1 req/2s daytime,
  that is 1,800 PDFs per hour. If the hackathon runs 08:00-22:00, that
  is ~25,000 PDFs. Sounds like a lot, but if only 25-30% are
  born-digital (per the design doc), you get ~6,000-7,500 with usable
  text.
- The LLM structured extraction step (step 4: "extract scope of work,
  payment terms, duration") is a separate project in itself. Contract
  PDFs are not standardized -- different institutions use different
  templates. Extracting structured fields from free-text contracts is
  a research problem, not a hackathon task.
- Full-text search (step 5) over extracted content is straightforward
  with SQLite FTS or PostgreSQL tsvector, but only if the text quality
  is good. pdftotext output from complex layouts (tables, multi-column)
  can be garbled.

**Realistic scope**: Download 500-1000 PDFs (a few hours of downloading),
run pdftotext, do basic keyword search over the extracted text. The LLM
structured extraction is a stretch goal at best.

**Recommendation**: Start downloading PDFs Friday evening (the hackathon
starts March 7). Have a pre-built corpus ready by Saturday morning.
Drop the LLM extraction from the hackathon scope entirely -- keyword
search over raw text is impressive enough as a proof of concept.

---

### Suggestion 5: Splitting Detector -- FEASIBLE (4-8 hours)

This is algorithmically simple and does not require any LLM calls. It
is pure data analysis: group by buyer+supplier, apply time window,
check for suspicious patterns.

**Where teams will get stuck**:
- False positives. Many legitimate scenarios produce the same pattern as
  splitting: framework agreements with monthly invoicing, recurring
  service contracts, phased construction. Without domain knowledge to
  filter these out, the "top 50 suspicious clusters" will be mostly
  noise.
- The procurement thresholds (50K for goods/services, 180K for
  construction) are specific to Slovak public procurement law. The
  document mentions these but does not cite the relevant law or confirm
  current thresholds. If these changed (they do, periodically), the
  detector produces wrong results.
- The demo depends on having enough data to find real splitting cases.
  If the team only loads a few days of contracts, there will not be
  enough buyer+supplier pairs with multiple contracts to detect
  anything interesting.

**Realistic scope**: Load 1-2 years of XML data, run the splitting
algorithm, present results. If the team pre-loads the data Friday night,
this is doable. The quality of results depends entirely on the scoring
heuristic and threshold tuning.

**Recommendation**: Explicitly mention that this suggestion requires
a larger dataset than the others (months or years, not days). Pre-load
data before the hackathon. Also add: consult with the 360ka journalists
during the hackathon about which results look like real splitting vs.
false positives -- this iteration is the real value.

---

### Suggestion 6: Ministry Budget Tracker -- FEASIBLE (6-10 hours)

This is essentially Suggestion 1 + aggregation + charting. It depends
on classification being done first.

**Where teams will get stuck**:
- This is a downstream consumer of Suggestion 1. If classification
  quality is poor, the budget breakdown is meaningless ("other: 60%"
  tells nobody anything).
- Building good-looking charts in a hackathon is surprisingly
  time-consuming. Streamlit's built-in charts are limited; Plotly or
  Altair look better but require more code.
- The "drill-down: click a category to see individual contracts"
  interaction is conceptually simple but adds significant UI complexity.

**Realistic scope**: Bar charts showing spending by category per
ministry for a pre-classified dataset. Year-over-year trends require
multi-year data (which means more download/processing time).

**Recommendation**: This works best as an extension of Suggestion 1,
not a standalone project. A team building Suggestion 1 should plan to
add this dashboard as their "polish" phase on Sunday.

---

## 2. Demo-ability Assessment

The judges are investigative journalists, IT consultants, and
fact-checkers. What impresses them is different from what impresses
a typical hackathon audience.

### What will impress these judges:

1. **Answering a real question they have tried and failed to answer
   using crz.gov.sk.** The most powerful demo starts with: "Here is
   a question you cannot answer today" and ends with an answer.

2. **Speed.** crz.gov.sk is notoriously slow and has basic search. Any
   tool that returns results in under 2 seconds for a query that takes
   minutes on the original site will get attention.

3. **Concrete findings.** "We found 47 cases where contracts appear to
   be split to avoid procurement thresholds" is vastly more compelling
   than "here is a tool that could theoretically find splitting."

4. **Data they can verify.** Journalists trust tools they can
   cross-check. Every result should link back to the original CRZ
   contract page. This is a small detail that the document does not
   mention but that makes a huge difference for credibility.

### What will NOT impress these judges:

1. **Chat interfaces that hallucinate.** A journalist who sees the
   agent confidently cite a nonexistent contract will write off the
   entire tool. Suggestion 3 is high-risk for this reason.

2. **Dashboards with no real insights.** Bar charts showing "Ministry X
   spends more than Ministry Y" are not interesting. Bar charts showing
   "Ministry X's marketing spending tripled in the quarter before
   elections" are interesting.

3. **Technology for technology's sake.** "We used RAG with embeddings
   and a vector database" does not matter to journalists. "We can find
   the cleaning contract that was hidden as 'Zmluva o dielo'" matters.

### The winning demo:

The strongest demo combines: (a) a specific investigative finding
surfaced by the tool, (b) live interactive querying that shows the tool
is real, and (c) a clear path to daily use by journalists.

Suggestion 1 + 5 is the highest demo-impact combination:
- Start with: "CRZ has 5.5M contracts but no categorization. We
  classified them."
- Show the filter UI: "All marketing contracts from Ministry X."
- Then reveal: "We also detected 47 suspected cases of contract
  splitting. Here is the most suspicious one." Click through to CRZ
  to verify.
- Close with: "This runs daily. We can alert you when new suspicious
  patterns appear."

---

## 3. Impact Assessment

Ranked by real-world value to investigative journalists:

| Rank | Suggestion | Impact | Reasoning |
|------|-----------|--------|-----------|
| 1 | **S1: CRZ Classifier** | Foundational | Every other suggestion depends on it. Without categorization, CRZ data is structurally useless for systematic investigation. This is infrastructure, not a feature. |
| 2 | **S5: Splitting Detector** | High | Detects a specific, legally actionable fraud pattern. Each positive finding is a potential published story. Journalists can immediately verify and use results. |
| 3 | **S2: Supplier X-Ray** | High | Company profiling is bread and butter for investigative journalists. "This company was formed 3 months ago and won 500K in contracts" is a lead, not just data. |
| 4 | **S4: PDF Decoder** | Medium-High | Unlocks the actual contract content. High long-term value but low hackathon-demo value (keyword search over raw PDF text is underwhelming without curation). |
| 5 | **S6: Budget Tracker** | Medium | Useful for ongoing monitoring but does not surface specific leads. It is an analysis tool, not an investigation tool. Journalists usually have a target already; they need depth, not breadth. |
| 6 | **S3: Contract Companion** | Medium-Low | Impressive as a concept but the least useful in practice today. Journalists who use CRZ regularly are faster with direct search than conversational AI. The agent adds value only after the underlying data layer is mature. |

The impact ranking differs from the demo-ability ranking. The agent
(S3) demos well but delivers less real investigative value. The
splitting detector (S5) demos less flashily but produces directly
actionable leads.

---

## 4. Missing Suggestions

### Missing Idea A: "Amendment Tracker" -- Follow the Money Through Contract Changes

**This is the most significant gap in the document.**

The design doc (v2) documents that `typ=2` means "amendment" and the
`ref` field (2.3% populated) links amendments to parent contracts. The
`suma_spolu` field tracks the total amount including amendments. This
creates a powerful investigation pattern that is entirely absent from
the suggestions:

- Original contract: 45,000 EUR (just below 50K threshold)
- Amendment 1: +20,000 EUR
- Amendment 2: +30,000 EUR
- Total: 95,000 EUR -- nearly double the original, no public tender

This is arguably more common and more significant than contract
splitting, because it is perfectly legal at each step but circumvents
the spirit of procurement law. The CRZ data explicitly supports this
analysis through the `suma_zmluva` vs `suma_spolu` fields.

**Build in a weekend**: Parse XML, identify contracts where
`suma_spolu >> suma_zmluva`, link amendments via `ref` field, rank by
inflation ratio.

**Demo**: "Here are the top 20 contracts where the final amount is more
than 3x the original contract value, with no new tender."

This would be a 4-6 hour build with high journalistic impact.

### Missing Idea B: "Deadline Monitor" -- Contracts Expiring Without Renewal

Contracts with `datum_platnost_do` in the near future and no linked
amendment or replacement contract may represent services that are about
to become uncontracted. This is less investigative and more
accountability-focused, but could be interesting for civic watchdogs.

Lower priority than Amendment Tracker but worth mentioning as a
downstream use of the parsed data.

### Missing Idea C: "Cross-Ministry Supplier Overlap"

Which suppliers work with multiple ministries? A supplier that has
contracts with 8 different ministries is either a large legitimate
vendor (cleaning, telecoms) or a well-connected intermediary worth
investigating. This is a variant of Suggestion 2 but focused on the
network aspect rather than individual supplier profiles.

Simple to build (GROUP BY supplier_ico HAVING COUNT(DISTINCT rezort) > N)
and produces a visually compelling network graph for the demo.

---

## 5. Technical Gotchas

### 5a: LLM API Rate Limits and Latency

The Anthropic API has rate limits that could bite during the hackathon.
Free-tier and low-tier accounts have restrictive limits (especially
requests per minute). A team that tries to classify 2,800 contracts
will hit rate limits within minutes.

**Mitigation**: Use tier-appropriate API keys. Pre-classify data the
night before. The Batch API has a 24h turnaround -- submit Friday
evening, results are ready Saturday morning.

### 5b: CRZ Data Quality

The design doc documents several data quality issues that the
suggestions document glosses over:

- 26.4% of contracts have no supplier ICO. Suggestion 2 (Supplier
  X-Ray) will miss a quarter of all contracts.
- 40% of contracts have `suma_zmluva = 0` (unknown amount). Any
  financial aggregation (Suggestion 6) will be incomplete.
- The `poznamka` field is only 6.3% populated. The classification
  sketch puts heavy weight on it ("auditorske sluzby") but it will
  be empty for 94% of contracts.

Teams that discover these issues mid-hackathon will lose hours
debugging "why is everything showing up as 0 EUR?" or "why are there
no results for this supplier?"

**Mitigation**: The suggestions document should explicitly warn about
these data quality issues. Add a "Data Quality Cheat Sheet" section
listing the gotchas and how to handle them (0 = NULL, empty ICO is
normal, etc.).

### 5c: CRZ Server Availability

CRZ.gov.sk is a government website with no SLA. It has been known to go
down during business hours or return errors under load. If the daily
export endpoint is down on Friday evening, the team cannot even start.

**Mitigation**: Download the XML exports before the hackathon and
include them in the repo or a shared drive. Do not depend on being able
to download data during the event.

### 5d: LLM Costs

The suggestions document correctly estimates costs (~$0.00014 per
contract). For a hackathon demo, classifying a few thousand contracts
costs under $1. This is not a concern.

However, if teams use Claude Sonnet for classification (instead of
Haiku as recommended) or build a chatbot with Sonnet (Suggestion 3),
costs scale quickly. 200 agent queries at ~$0.045 each = $9. Still not
a problem for a hackathon, but worth noting.

### 5e: XML Parsing Edge Cases

The design doc lists several XML edge cases: dual attachment fields,
0000-00-00 dates, empty fields, garbage ICO values. The code sketch
in the suggestions document uses `z.find('predmet').text` which will
throw `AttributeError` if `predmet` is missing or the element has no
text. This is a small thing, but a hackathon team that copies this
sketch verbatim will hit `NoneType has no attribute 'text'` within
minutes.

**Mitigation**: Update the code sketch to use safe access:
```python
def get_text(element, tag, default=''):
    node = element.find(tag)
    return node.text if node is not None and node.text else default
```

### 5f: Streamlit Deployment for Demo

If teams use Streamlit, they need to either run it locally (fine for
in-person demo) or deploy it (Streamlit Cloud, which requires a public
GitHub repo). The document does not mention deployment. For a hackathon
demo, localhost is almost always fine, but teams should test their demo
on the actual presentation setup (projector, network) before going on
stage.

---

## 6. Prioritization: The One Suggestion to Build

**If I could recommend only ONE suggestion: build Suggestion 1 (CRZ
Classifier) combined with the missing "Amendment Tracker" idea.**

### Why:

1. **Suggestion 1 is the foundation.** Without classification, the CRZ
   data is a flat list of "Zmluva o dielo" entries. Classification
   transforms it into queryable, structured investigative data. Every
   other suggestion either depends on it (S3, S6) or benefits from it
   (S2, S5).

2. **The Amendment Tracker is a natural extension.** It uses the same
   parsed data but adds a second analysis dimension (amendment
   inflation) that produces concrete investigative findings. It does
   not require LLM calls (it is pure data analysis on `suma_zmluva`
   vs `suma_spolu` and the `ref` field).

3. **The combined demo tells a complete story.** "We classified all
   contracts so you can search by category. And we found 35 contracts
   where the final amount is 5x the original value with no new tender."
   This gives judges both infrastructure value (the classifier) and
   immediate investigative value (the amendment findings).

4. **It is buildable in a weekend.** Classification: 4-6 hours.
   Amendment analysis: 2-3 hours. UI: 2-3 hours. Total: 8-12 hours
   with margin.

5. **It avoids the high-risk components.** No agent (hallucination
   risk), no PDF downloading (rate limits), no external API
   dependencies (ORSR). Just XML parsing, LLM classification, and
   data analysis.

### What to cut from the current recommendation:

The document recommends combining S1 + S3 + S6 for a single team. This
is too much. S3 (agent) is the riskiest component and adds the least
investigative value. S6 (dashboard) is nice but is "more charts" rather
than "more findings." Replace both with the Amendment Tracker, which is
simpler to build and more impactful to demo.

---

## 7. Suggestions for the Document Itself

### 7a: Add a "Pre-Hackathon Checklist"

The document should include a section listing what teams should do
before arriving Saturday morning:

- Download 1-2 years of CRZ XML exports (curl loop, ~30 minutes)
- Set up Anthropic API key with sufficient credits
- Install dependencies: `pdftotext` (poppler-utils), Python 3.12+,
  streamlit, anthropic SDK
- Pre-classify a dataset of ~2,000 contracts using the Batch API
  (submit Friday evening, ready Saturday morning)
- Have a fallback dataset in case CRZ is down

### 7b: Add a "Data Quality Cheat Sheet"

Pull the data quality issues from the design doc into the suggestions
document. Teams should not have to read the 600-line design doc to
know that `suma_zmluva = 0` means "unknown."

### 7c: Fix the Code Sketch

The code sketch (Section "Technical Quick-Start") will fail on edge
cases. At minimum:
- Add null-safe field access
- Add error handling for the Anthropic API call
- Show how to handle rate limits (`time.sleep` or async with
  `asyncio.Semaphore`)

### 7d: Be Explicit About Dataset Size vs. Demo Quality

The document's demo examples ("all marketing contracts from Ministry
of Agriculture over 10K in 2025") require a full year of data. If a
team only downloads 3 days of contracts (~8,400 records), the filters
will return 0 or 1 result and the demo will fall flat. The document
should state: "For an impressive demo, load at least 3-6 months of
data (download the night before)."

### 7e: Add Links Back to CRZ

Every result displayed in the UI should include a clickable link to
`https://www.crz.gov.sk/zmluva/{id}/`. This is one line of code and
it transforms the tool from "a database someone built" to "a lens on
top of the official register." Journalists will immediately trust
results they can verify. Mention this explicitly.

---

## 8. Overall Assessment

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Technical accuracy | Strong | Grounded in actual data exploration. XML schema, rate limits, costs are realistic. |
| Hackathon feasibility | Good with caveats | S1 and S5 are well-scoped. S3 is too risky. S4 depends on pre-downloaded data. |
| Demo-ability | Good | S1 + S5 or S1 + Amendment Tracker produce the strongest demo. |
| Completeness | Gap | Amendment tracking (the biggest investigative pattern in the data) is missing. |
| Practical advice | Needs work | Missing pre-hackathon checklist, data quality warnings, and deployment notes. |
| Prioritization | Slightly off | The S1+S3+S6 recommendation overweights the agent. S1 + anomaly detection is stronger. |

**Bottom line**: This is a solid document that gives hackathon teams a
significant head start. The main improvements needed are: (1) add the
Amendment Tracker suggestion, (2) replace the S1+S3+S6 recommendation
with S1 + anomaly detection (splitting or amendments), (3) add
practical pre-hackathon preparation guidance, and (4) be honest about
data quality issues that will trip teams up.
