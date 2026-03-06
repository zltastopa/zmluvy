# CRZ Smart Contracts — Design Document (v2)

**Date**: 2026-03-06
**Status**: Draft v2 — incorporates review feedback
**Stakeholders**: 360ka / 360tka.sk (Michal, Barbora)
**Review**: See `2026-03-06-crz-design-review.md` for the v1 review

---

## Changes from v1

Key fixes based on review:

1. **Cost estimates recalculated** with explicit token math (was off by ~10x)
2. **Daily export semantics clarified** — exports include re-processed old contracts, not just new ones
3. **XML schema completed** — added 10+ missing fields (poznamka, ref, zdroj, dual attachment fields)
4. **Supplier schema redesigned** — surrogate key instead of ICO-only, GDPR considerations
5. **Classification pilot added** as a prerequisite gate before building the pipeline
6. **Agentic interface specified** with tool schemas and cost budget
7. **Vestník scoped down** to explicit UVO references only (2.8% of contracts)
8. **Embeddings deferred** until a concrete use case emerges
9. **pdftotext + ORSR pulled forward** into Phase 1
10. **Testing strategy added**

---

## Problem Statement

Slovakia's Central Register of Contracts (CRZ, crz.gov.sk) contains 5.5M+ published contracts. Every contract involving public funds must be published here to become legally effective.

**The core problem**: Contract metadata is structurally useless for investigative purposes. A "Zmluva o dielo" could be legal services, marketing, or construction — you cannot tell without opening the PDF. There is no semantic categorization, no full-text search of attachments, and many PDFs are scanned images.

**Who needs this**: Investigative journalists (360ka), civic watchdogs, procurement analysts.

---

## Data Landscape

### Access Methods

| Method | URL Pattern | Format | Notes |
|--------|-------------|--------|-------|
| Daily XML export | `https://www.crz.gov.sk/export/YYYY-MM-DD.zip` | ZIP → XML | Nightly at 02:00. **Includes re-processed old contracts, not just new.** Can be 0 bytes on some days. |
| PDF attachments | `https://www.crz.gov.sk/data/att/{id}.pdf` | PDF | Rate-limited: 1 req/2s daytime, 3 req/s nighttime |
| Contract detail | `https://www.crz.gov.sk/zmluva/{id}/` | HTML | Same rate limits |

### Complete XML Schema

Based on analysis of actual 2026-03-04 export (2,794 records):

```xml
<zmluva>
  <!-- Core identification -->
  <ID>12075397</ID>                <!-- CRZ internal ID (primary identifier) -->
  <nazov>104/2026</nazov>          <!-- Contract number (assigned by institution) -->
  <predmet>Zmluva o dielo</predmet> <!-- Subject/title — THE PROBLEM FIELD -->

  <!-- Parties -->
  <zs1>MESTO DETVA</zs1>           <!-- Buyer name -->
  <ico1>00319805</ico1>            <!-- Buyer ICO (can be empty) -->
  <sidlo1>J. G. Tajovského...</sidlo1> <!-- Buyer address -->
  <zs2>JP Constructions s.r.o.</zs2>  <!-- Supplier name -->
  <ico>56048441</ico>              <!-- Supplier ICO (EMPTY in 26.4% of records!) -->
  <sidlo>Banská Bystrica</sidlo>   <!-- Supplier address -->

  <!-- Financial -->
  <suma_zmluva>8200</suma_zmluva>  <!-- Agreed amount (0 = unknown/NA, not free) -->
  <suma_spolu>8200</suma_spolu>    <!-- Total amount including amendments -->

  <!-- Dates -->
  <datum>2026-03-06</datum>        <!-- Signing date -->
  <datum_ucinnost>2026-03-08</datum_ucinnost>  <!-- Effective date -->
  <datum_platnost_do>0000-00-00</datum_platnost_do> <!-- Valid until (0000-00-00 = indefinite → NULL) -->
  <datum_zverejnene>2026-03-06 09:00:00</datum_zverejnene> <!-- Publication date -->

  <!-- Classification -->
  <rezort>6215909</rezort>         <!-- Publishing institution ID (NOT ministry ID) -->
  <stav>2</stav>                   <!-- Status: 2=active, 3=cancelled -->
  <typ>1</typ>                     <!-- Type: 1=contract, 2=amendment -->
  <druh>1</druh>                   <!-- Kind: 1=contract, 2=order, 0=other -->
  <zdroj>1</zdroj>                 <!-- Source system: 1 or 3 (~50/50 split) -->

  <!-- Additional text fields (HIGH CLASSIFICATION VALUE) -->
  <poznamka>auditorske sluzby</poznamka>  <!-- Notes — 6.3% populated, strong signal -->
  <popis></popis>                  <!-- Description — 0.9% populated -->
  <popis_predmetu></popis_predmetu> <!-- Subject description — rarely populated -->
  <internapozn></internapozn>      <!-- Internal notes — 1% populated -->
  <text_ucinnost></text_ucinnost>  <!-- Effectiveness text — 1.3% populated -->
  <poznamka_zmena></poznamka_zmena> <!-- Change notes — rarely populated -->

  <!-- Linking -->
  <ref></ref>                      <!-- Parent contract reference (2.3% populated) -->
                                   <!-- Contains URLs, internal IDs, or contract numbers -->
                                   <!-- CRITICAL for linking amendments to parent contracts -->
  <uvo></uvo>                      <!-- Public procurement reference (2.8% populated) -->
  <id>0</id>                       <!-- Internal ID (lowercase, different from ID) -->

  <!-- Administrative -->
  <potv_ziadost>5</potv_ziadost>   <!-- Confirmation request status -->
  <potv_datum>2026-03-08</potv_datum> <!-- Confirmation date -->
  <potvrdenie>12075397_potvrdenie.pdf</potvrdenie> <!-- Confirmation PDF (10% populated) -->
  <chan>2026-03-06 09:00:00</chan>  <!-- Last changed timestamp -->

  <!-- Attachments (CRITICAL: uses EITHER dokument+velkost OR dokument1+velkost1, never both) -->
  <prilohy>
    <priloha>
      <ID>12075399</ID>
      <nazov>Zmluva o dielo</nazov>
      <dokument></dokument>         <!-- Old storage system filename (49% of attachments) -->
      <velkost>0</velkost>          <!-- Old storage system size -->
      <dokument1>6575230.pdf</dokument1> <!-- New storage system filename (51%) -->
      <velkost1>33348050</velkost1>      <!-- New storage system size -->
      <chan>2026-03-04 12:00:00</chan>    <!-- Attachment change timestamp (independent of contract chan) -->
    </priloha>
  </prilohy>
</zmluva>
```

### Key Data Quality Issues

| Issue | Prevalence | Impact |
|-------|-----------|--------|
| Empty supplier ICO | 26.4% | Cannot cross-reference with business register |
| Garbage ICO values | ~0.1% | Need validation/cleaning |
| `suma_zmluva = 0` | 40% | Means unknown, not free — must use NULL |
| `datum_platnost_do = 0000-00-00` | 70% | Invalid date — convert to NULL |
| Dual attachment fields | 50/50 split | Must check both `dokument` and `dokument1` |
| Re-exported old contracts in daily export | ~3-5% | Dedup must track change timestamps |
| Suppliers are natural persons | ~20% | GDPR implications for profiling |

---

## Pre-Requisites (Before Building Anything)

### P1: Classification Pilot

**Gate**: Do not build the classification pipeline until this is done.

1. Select 200 contracts spanning different types, institutions, and amounts
2. Have the 360ka journalists manually classify them into categories
3. Use their categories to refine the taxonomy (their mental model, not ours)
4. Run the LLM classifier on the same 200 contracts
5. Measure accuracy. Target: >75% agreement with human labels
6. Iterate on prompt and taxonomy until target is met

### P2: Historical Export Analysis

Download 10 daily exports from different years (2012, 2015, 2018, 2020, 2023, 2025) and verify:
- Same XML schema across years?
- How many unique contract IDs appear across multiple daily exports?
- Total volume estimate for full historical bootstrap

### P3: Competitive Landscape Research

Investigate before building:
- **otvorenezmluvy.sk** — if they already provide structured CRZ data, skip ingestion
- **datanest.sk / ekosystem.slovensko.digital** — existing cleaned datasets?
- **Transparency International Slovakia** — existing analysis tools?

---

## Architecture — Two Phases (Vestník deferred)

### Phase 1: Smart Metadata + Lightweight PDF Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  CRZ Daily  │────▶│  Ingestion   │────▶│  PostgreSQL   │
│  XML Export │     │  Worker      │     │               │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                    ┌──────────────┐              │
                    │  ORSR API    │──────────────┤ supplier enrichment
                    │  (NACE codes)│              │
                    └──────────────┘              │
                                                 │
                    ┌──────────────┐     ┌───────┴──────┐     ┌──────────────┐
                    │  Claude API  │◀───▶│  Classifier  │     │  FastAPI     │
                    │  (Haiku 4.5) │     │  Pipeline    │     │  REST API    │
                    └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                      │
                    ┌──────────────┐                           ┌──────┴───────┐
                    │  pdftotext   │──── born-digital PDFs ──▶│  Search UI   │
                    │  (Phase 1)   │                           │  + Agent     │
                    └──────────────┘                           └──────────────┘
```

**Phase 1 includes**:
- Full historical data ingestion from daily XML exports
- LLM classification of all contracts by service category
- ORSR business register lookup for top suppliers (NACE codes → classification signal)
- pdftotext extraction for born-digital PDFs only (no OCR yet — covers ~25-30%)
- REST API with search and filters
- Basic agentic interface

#### 1.1 Data Ingestion

**Bootstrap**: Download all ~5,500 daily ZIPs. Process chronologically, tracking:
- Contract-level `chan` timestamp
- Attachment-level `chan` timestamp (independent!)
- On conflict (same ID appears in multiple exports): update only if contract `chan` is newer

**Daily incremental**: Cron at 03:00, downloads previous day's ZIP. Handles:
- Empty/0-byte ZIPs gracefully (log, don't alert)
- Re-exported old contracts (update only changed fields)
- New contracts (insert)

**Attachment filename resolution**:
```python
def get_attachment_filename(priloha):
    """Check both old and new storage fields."""
    if priloha.find('dokument1') is not None and priloha.find('dokument1').text:
        return priloha.find('dokument1').text
    elif priloha.find('dokument') is not None and priloha.find('dokument').text:
        return priloha.find('dokument').text
    return None
```

#### 1.2 Database Schema

```sql
CREATE TABLE contracts (
    id BIGINT PRIMARY KEY,                  -- CRZ contract ID (uppercase <ID>)
    internal_id INTEGER,                     -- lowercase <id> field
    contract_number TEXT,                    -- nazov
    subject TEXT,                            -- predmet

    -- Parties
    buyer_name TEXT,                         -- zs1
    buyer_ico TEXT,                          -- ico1
    buyer_address TEXT,                      -- sidlo1
    supplier_name TEXT,                      -- zs2
    supplier_ico TEXT,                       -- ico (NULL for 26% of records)
    supplier_address TEXT,                   -- sidlo

    -- Financial (NULL = unknown, not free)
    amount NUMERIC(15, 2),                  -- suma_zmluva (0 → NULL)
    total_amount NUMERIC(15, 2),            -- suma_spolu (0 → NULL)

    -- Classification
    rezort_id INTEGER,                       -- rezort (institution ID, not ministry)
    status SMALLINT,                         -- stav: 2=active, 3=cancelled
    contract_type SMALLINT,                  -- typ: 1=contract, 2=amendment
    contract_kind SMALLINT,                  -- druh: 1=contract, 2=order, 0=other
    source_system SMALLINT,                  -- zdroj: 1 or 3

    -- Dates
    date_published TIMESTAMPTZ,              -- datum_zverejnene
    date_signed DATE,                        -- datum
    date_effective DATE,                     -- datum_ucinnost
    date_valid_until DATE,                   -- datum_platnost_do (0000-00-00 → NULL)
    date_confirmed DATE,                     -- potv_datum
    last_changed TIMESTAMPTZ,                -- chan (contract-level)

    -- Additional text (classification signal)
    notes TEXT,                              -- poznamka
    description TEXT,                        -- popis
    subject_description TEXT,                -- popis_predmetu
    internal_notes TEXT,                     -- internapozn
    effectiveness_text TEXT,                 -- text_ucinnost
    change_notes TEXT,                       -- poznamka_zmena

    -- Linking
    parent_ref TEXT,                         -- ref (parent contract reference)
    uvo_ref TEXT,                            -- uvo (public procurement reference)
    confirmation_status SMALLINT,            -- potv_ziadost
    confirmation_pdf TEXT,                   -- potvrdenie

    -- Enrichment (populated by classifier)
    category TEXT,
    subcategory TEXT,
    category_confidence REAL,
    category_reasoning TEXT,
    flags TEXT[],

    -- Search
    search_vector tsvector,

    -- Audit
    raw_xml TEXT,                            -- Original XML (TEXT, not JSONB — lossless)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE attachments (
    id BIGINT PRIMARY KEY,                   -- Attachment ID from CRZ
    contract_id BIGINT REFERENCES contracts(id),
    original_name TEXT,                      -- nazov
    filename TEXT,                           -- COALESCE(dokument1, dokument)
    file_size BIGINT,                        -- COALESCE(velkost1, velkost)
    storage_system TEXT,                     -- 'old' (dokument) or 'new' (dokument1)
    last_changed TIMESTAMPTZ,                -- Attachment-level chan (independent!)

    -- PDF extraction
    text_extracted TEXT,
    text_extraction_method TEXT,             -- 'pdftotext', 'ocr_tesseract', 'ocr_cloud', NULL
    text_extracted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,                   -- Surrogate key (NOT ico)
    ico TEXT,                                -- Business ICO (NULL for natural persons)
    name TEXT NOT NULL,
    address TEXT,
    is_natural_person BOOLEAN DEFAULT FALSE,

    -- ORSR enrichment
    nace_codes TEXT[],
    legal_form TEXT,
    established_date DATE,
    orsr_data JSONB,

    -- Aggregates (materialized)
    contract_count INTEGER DEFAULT 0,
    total_contract_value NUMERIC(15, 2) DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_ico UNIQUE (ico) -- Unique where not null
);

-- Indexes
CREATE INDEX idx_contracts_category ON contracts(category);
CREATE INDEX idx_contracts_supplier_ico ON contracts(supplier_ico);
CREATE INDEX idx_contracts_buyer_ico ON contracts(buyer_ico);
CREATE INDEX idx_contracts_rezort ON contracts(rezort_id);
CREATE INDEX idx_contracts_published ON contracts(date_published);
CREATE INDEX idx_contracts_amount ON contracts(amount) WHERE amount IS NOT NULL;
CREATE INDEX idx_contracts_search ON contracts USING gin(search_vector);
CREATE INDEX idx_contracts_parent_ref ON contracts(parent_ref) WHERE parent_ref IS NOT NULL;
CREATE INDEX idx_attachments_contract ON attachments(contract_id);
CREATE INDEX idx_suppliers_ico ON suppliers(ico) WHERE ico IS NOT NULL;
CREATE INDEX idx_suppliers_name ON suppliers USING gin(to_tsvector('simple', name));
```

#### 1.3 LLM Classification

**Taxonomy**: To be finalized after classification pilot with journalists. Starting proposal:

```
legal, consulting, IT, marketing, construction, healthcare,
education, transport, facilities, real_estate, financial,
HR, grants, culture_sports, municipal_services, other
```

**Classification prompt** (uses all available metadata signals):

```
Classify this Slovak government contract into a service category.

Metadata:
- Subject: {predmet}
- Supplier: {zs2}
- Buyer: {zs1}
- Amount: {suma_zmluva} EUR
- Institution: {rezort_name}
- Notes: {poznamka}
- Description: {popis}
- Supplier NACE codes: {nace_codes}  ← from ORSR lookup

Categories: [taxonomy list]

Return JSON: {"category": "...", "subcategory": "...", "confidence": 0.X, "reasoning": "..."}
```

**Processing strategy**:
- Use Anthropic Batch API (50% discount, 24h turnaround) for backfill
- Use standard API for daily incremental (immediate)
- For confidence < 0.5, mark as "needs_pdf_content" (don't escalate to bigger model — same input, same ambiguity)

**Cost estimates (explicit math)**:

| | Tokens | Haiku 4.5 price | Cost |
|--|--------|-----------------|------|
| Input per contract | ~250 tok | $0.25/MTok | $0.0000625 |
| Output per contract | ~60 tok | $1.25/MTok | $0.000075 |
| **Per contract** | | | **$0.000138** |
| Backfill 5.5M (Batch API, 50% off) | | | **~$379** |
| Daily 2,800 (standard API) | | | **$0.39/day = ~$12/month** |

#### 1.4 ORSR Business Register Enrichment

For suppliers with ICO (73.6% of contracts), look up:
- NACE activity codes (reveals actual business type)
- Legal form, establishment date
- Feed NACE codes into classification prompt as additional signal

Priority: Top 10,000 suppliers by contract count/value first.

#### 1.5 Lightweight PDF Extraction

**Phase 1 only does pdftotext** (no OCR):
- Run `pdftotext` on downloaded PDFs
- If >100 chars extracted → born-digital → store extracted text
- If ≤100 chars → scanned → mark as `needs_ocr` for Phase 2
- Use extracted text to re-classify low-confidence contracts

**Download strategy** (both daytime and nighttime):
- Daytime (06:00-20:00): 1 req/3s (safe margin) = ~16,800/day
- Nighttime (20:00-06:00): 2 req/s (safe margin under 3/s limit) = ~72,000/night
- Total: ~88,800 PDFs/day
- Priority queue: high-value + low-confidence contracts first
- Full backfill of unique attachments: ~62 days (~2 months)

#### 1.6 API Layer

```
GET  /api/v1/contracts              -- Search & filter (category, supplier, amount, date, rezort)
GET  /api/v1/contracts/{id}         -- Contract detail with enrichments
GET  /api/v1/suppliers/{ico}        -- Supplier profile + contract history
GET  /api/v1/stats/categories       -- Category distribution (filterable by rezort, year)
GET  /api/v1/stats/top-suppliers    -- Top suppliers by value/count
GET  /api/v1/anomalies              -- Flagged patterns
```

#### 1.7 Agentic Interface

**Model**: Claude Sonnet 4.6 (good balance of capability and cost for conversational use)

**Tools available to the agent**:

```json
[
  {
    "name": "search_contracts",
    "description": "Search CRZ contracts with filters",
    "input_schema": {
      "q": "string — fulltext search query (Slovak)",
      "category": "string — service category filter",
      "supplier_ico": "string",
      "buyer_ico": "string",
      "rezort": "string — institution name or ID",
      "amount_min": "number",
      "amount_max": "number",
      "date_from": "string (YYYY-MM-DD)",
      "date_to": "string (YYYY-MM-DD)",
      "sort": "string — date|amount|relevance",
      "limit": "integer (max 100)"
    }
  },
  {
    "name": "get_contract_detail",
    "description": "Get full contract detail including extracted text",
    "input_schema": { "id": "integer — CRZ contract ID" }
  },
  {
    "name": "get_supplier_profile",
    "description": "Get supplier info, NACE codes, and contract history",
    "input_schema": { "ico": "string" }
  },
  {
    "name": "get_statistics",
    "description": "Get aggregate statistics for contracts",
    "input_schema": {
      "group_by": "string — category|rezort|supplier|year|month",
      "filters": "same as search_contracts",
      "metric": "string — count|total_amount|avg_amount"
    }
  },
  {
    "name": "get_anomalies",
    "description": "Get flagged anomalous contracts or patterns",
    "input_schema": {
      "anomaly_type": "string — price_outlier|new_company_big_contract|concentration|splitting",
      "rezort": "string — optional filter"
    }
  }
]
```

**Language policy**: Agent responds in Slovak. Tool calls use English keys with Slovak values.

**Cost estimate**:
- ~5,000 input tokens + ~2,000 output tokens per query (with tool use)
- Sonnet 4.6: $3/MTok in, $15/MTok out
- Per query: ~$0.045
- Assuming 10 users × 20 queries/day = 200 queries/day
- **Monthly agent cost: ~$270**

**Ambiguity handling**: When classification confidence is low or data has gaps, the agent should communicate uncertainty: "Našiel som 45 zmlúv o dielo z tohto ministerstva, ale 12 z nich nemá spoľahlivú kategorizáciu (dôveryhodnosť pod 60%). Odporúčam preveriť tieto zmluvy manuálne."

---

### Phase 2: OCR + Deep PDF Intelligence

**Trigger**: Phase 1 is complete and classification pilot confirms that PDF content meaningfully improves accuracy for ambiguous contracts.

**Additions**:
- Tesseract OCR with Slovak language model for scanned PDFs
- Cloud OCR fallback (Google Document AI) for poor Tesseract results
- Re-classification of all "needs_pdf_content" contracts with full text
- Key clause extraction for contracts > €50,000
- Full-text search across extracted contract content

**Vestník (scoped down)**: Only cross-reference contracts that have explicit `uvo` field values (2.8% of contracts). Parse the UVO URLs/IDs and link to the corresponding Vestník records. Do not attempt fuzzy matching.

---

## Technology Stack

| Component | Technology | Reasoning |
|-----------|-----------|-----------|
| Language | Python 3.12+ | Data processing, LLM APIs, good ecosystem |
| Database | PostgreSQL 16 | Full-text search, JSONB, handles 5.5M+ rows easily |
| Full-text search | PostgreSQL with `unaccent` + `simple` config | Slovak dictionary TBD (hunspell if available) |
| API | FastAPI | Async, auto-docs, type-safe |
| Task scheduling | Cron + Python scripts | Simple. Graduate to Celery only if needed. |
| LLM (classification) | Claude Haiku 4.5 (Batch API for backfill) | Cost-efficient, ~$0.00014/contract |
| LLM (agent) | Claude Sonnet 4.6 | Capable conversational agent |
| OCR (Phase 2) | Tesseract 5 + slk model | Free, decent Slovak |
| PDF text | pdftotext (poppler-utils) | Fast, reliable for born-digital |
| Containerization | Docker Compose | Simple deployment |

## Cost Summary

### Phase 1

| Item | One-time | Monthly |
|------|----------|---------|
| Classification backfill (5.5M × Haiku, Batch API) | ~$380 | — |
| Daily classification (~2,800/day) | — | ~$12 |
| ORSR lookups (10K suppliers) | ~$50 | ~$10 |
| PostgreSQL hosting (managed, 50GB) | — | ~$30 |
| API hosting (small VM) | — | ~$20 |
| Agent usage (Sonnet, 200 queries/day) | — | ~$270 |
| **Phase 1 Total** | **~$430** | **~$342** |

### Phase 2 (incremental)

| Item | One-time | Monthly |
|------|----------|---------|
| Cloud OCR for difficult scans | ~$1,500 | ~$100 |
| Re-classification with full text | ~$200 | ~$25 |
| Additional storage (text, ~30GB) | — | ~$10 |
| **Phase 2 Total** | **~$1,700** | **~$135** |

## Testing Strategy

### Classification Evaluation
- **Golden set**: 500 contracts manually labeled by journalists (expanded from pilot's 200)
- **Accuracy metric**: Category match rate (exact) and near-match rate (same Level 1)
- **Regression testing**: Re-run golden set when prompt or model changes
- **Continuous monitoring**: Sample 50 random new classifications weekly, spot-check

### Data Pipeline Testing
- **Unit tests**: XML parsing edge cases (empty fields, garbage ICOs, dual attachment fields, 0000-00-00 dates)
- **Integration tests**: End-to-end daily pipeline with a sample ZIP file
- **Monitoring**: Alert on: parse failures, empty daily exports for >2 consecutive days, classification error rate spikes

### API Testing
- Standard FastAPI test suite with pytest
- Load testing: verify <500ms response for filtered queries on 5.5M rows

## Open Questions for 360ka

1. **Taxonomy**: We'll refine during the classification pilot, but initial question — do you care more about *what* was purchased (legal services, marketing) or *why* it's suspicious (new company, high price, repeated supplier)?
2. **Historical depth**: 2011-present is ~15 years. Would 2020-present suffice for a quicker MVP?
3. **Language**: Slovak-only UI, or also English?
4. **Access**: Fully public tool, or login-required for advanced features?
5. **Deployment**: Do you have infrastructure, or do we need to provision everything?
6. **Existing data**: Do you already use otvorenezmluvy.sk or similar tools?

## Recommended Execution Order

1. Classification pilot (1 week)
2. Historical export analysis (2 days)
3. Competitive landscape research (2 days)
4. Data ingestion pipeline (1 week)
5. ORSR enrichment (3 days)
6. Classification pipeline (1 week)
7. API + basic search UI (1 week)
8. pdftotext extraction for born-digital PDFs (runs in background, ~2 months)
9. Agentic interface (1 week)
10. Phase 2: OCR + deep PDF intelligence (after Phase 1 is validated)
