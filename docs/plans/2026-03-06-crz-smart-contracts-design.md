# CRZ Smart Contracts — Design Document

**Date**: 2026-03-06
**Status**: Draft — pending review
**Stakeholders**: 360ka / 360tka.sk (Michal, Barbora)

## Problem Statement

Slovakia's Central Register of Contracts (CRZ, crz.gov.sk) contains 5.5M+ published contracts between state institutions and private entities. The register is legally mandated — every contract involving public funds must be published here to become effective.

**The core problem**: The metadata is structurally useless for investigative purposes.

- A "Zmluva o dielo" (Contract for Work) could be legal services, marketing, IT consulting, or construction — you cannot tell without opening the PDF
- There is no semantic categorization of contract types by service category
- The `predmet` (subject) field contains free-text titles, not structured categories
- PDFs are often scanned images, not machine-readable text
- No cross-referencing exists between contracts, suppliers, or institutions
- Searching for "all marketing contracts from Ministry X" is impossible without manually reading every document

**Who needs this**: Investigative journalists (360ka), civic watchdogs, procurement analysts, and any citizen wanting transparency into how public money is spent.

## Data Landscape — What We Know

### CRZ Data Access Methods

| Method | URL Pattern | Format | Freshness | Rate Limits |
|--------|-------------|--------|-----------|-------------|
| Daily XML export | `https://www.crz.gov.sk/export/YYYY-MM-DD.zip` | ZIP → XML | Nightly at 02:00 | None (single file) |
| PDF attachments | `https://www.crz.gov.sk/data/att/{id}.pdf` | PDF | Real-time | 1 req/2s daytime, 3 req/s nighttime |
| Web search | `https://www.crz.gov.sk/zmluva/{id}/` | HTML | Real-time | Same rate limits |
| RSS feed | `https://www.crz.gov.sk/rss/` | XML/RSS | Unknown | Unknown |
| Fulltext search | Web UI only (ElasticSearch backend) | HTML | Real-time | Rate-limited |

### Daily XML Export Schema

Each daily ZIP contains a single XML file with all changes from that day. On a typical day: ~2,800 contract records. The XML structure per contract:

```xml
<zmluva>
  <nazov>104/2026</nazov>                    <!-- Contract number -->
  <ID>12075397</ID>                           <!-- CRZ internal ID -->
  <zs1>MESTO DETVA</zs1>                     <!-- Buyer (objednávateľ) -->
  <zs2>JP Constructions s. r. o.</zs2>       <!-- Supplier (dodávateľ) -->
  <predmet>Zmluva o dielo</predmet>          <!-- Subject/title (THE PROBLEM) -->
  <datum_ucinnost>2026-03-08</datum_ucinnost>
  <datum_platnost_do>0000-00-00</datum_platnost_do>
  <suma_zmluva>8200</suma_zmluva>            <!-- Agreed amount -->
  <suma_spolu>8200</suma_spolu>              <!-- Total amount -->
  <rezort>6215909</rezort>                    <!-- Ministry/resort ID -->
  <datum_zverejnene>2026-03-06 09:00:00</datum_zverejnene>
  <ico>56048441</ico>                         <!-- Supplier ICO -->
  <ico1>00319805</ico1>                       <!-- Buyer ICO -->
  <sidlo>...</sidlo>                          <!-- Supplier address -->
  <sidlo1>...</sidlo1>                        <!-- Buyer address -->
  <stav>2</stav>                              <!-- Status: 2=active, 3=cancelled -->
  <typ>1</typ>                                <!-- Type: 1=contract, 2=amendment -->
  <druh>1</druh>                              <!-- Kind: 1=contract, 2=order, 0=other -->
  <prilohy>
    <priloha>
      <ID>12075399</ID>
      <nazov>Zmluva o dielo</nazov>
      <dokument1>6575230.pdf</dokument1>      <!-- Attachment filename -->
      <velkost1>33348050</velkost1>            <!-- Size in bytes -->
    </priloha>
  </prilohy>
</zmluva>
```

### Key Observations from Data Analysis (2026-03-04 export)

- **2,794 records** in a single day's export
- **Top subjects**: Cemetery plot rentals (215), Purchase contracts (56), Rental agreements (53), Employment agency agreements (72), **"Zmluva o dielo" (28)**, Service contracts (19)
- **60% of contracts have non-zero monetary amounts** (1,668/2,794)
- **97% have exactly 1 attachment** (2,690/2,794)
- **Status distribution**: 99.7% active (stav=2), 0.3% cancelled (stav=3)
- **Type distribution**: 94% contracts (typ=1), 6% amendments (typ=2)

### PDF Attachment Reality

From sampling ~10 PDFs across different size ranges:

| Category | % of PDFs (estimated) | Extractable? |
|----------|----------------------|--------------|
| Scanned images | ~60-70% | Only via OCR |
| Born-digital (text layer) | ~20-30% | Yes, via pdftotext |
| Mixed (scan + text overlay) | ~5-10% | Partially |

**Critical insight**: Most contracts from smaller municipalities and older institutions are scans. Larger institutions (ministries, universities) more often produce born-digital PDFs. This means OCR is not optional — it's required for the majority of documents.

### Metadata Classification Potential

Even without PDF content, metadata alone carries signal:

| Metadata Field | Classification Signal |
|---------------|----------------------|
| `predmet` (subject) | Direct: "Zmluva o poskytovaní právnych služieb" = legal services |
| `zs2` (supplier name) | Strong: "Advokátska kancelária" = legal, "KPMG" = consulting |
| `nazov` (contract number) | Weak: numbering patterns sometimes indicate department |
| `suma_zmluva` (amount) | Contextual: helps narrow category when combined |
| `rezort` (ministry) | Contextual: Ministry of Health + "Zmluva o dielo" likely medical equipment |
| `ico` (supplier ICO) | Cross-reference: lookup in business register reveals NACE codes |

**Estimated classification accuracy from metadata alone**: 70-85% (for broad categories like legal/IT/construction/marketing). For ambiguous cases ("Zmluva o dielo" from a generic supplier), PDF content is needed.

---

## Architecture — Three Phases

### Phase 1: Smart Metadata Pipeline ("The Foundation")

**Goal**: Ingest all CRZ data, classify contracts by service category using LLM, provide searchable API.

```
                                    ┌──────────────┐
                                    │  Claude API   │
                                    │  (Haiku 4.5)  │
                                    └──────┬───────┘
                                           │ classify
┌─────────────┐     ┌──────────────┐     ┌─┴────────────┐     ┌──────────────┐
│  CRZ Daily  │────▶│  Ingestion   │────▶│  Enrichment  │────▶│  PostgreSQL  │
│  XML Export │     │  Worker      │     │  Pipeline     │     │  + pgvector  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                      │
                                                                ┌─────┴──────┐
                                                                │  REST API  │
                                                                │  (FastAPI) │
                                                                └─────┬──────┘
                                                                      │
                                                                ┌─────┴──────┐
                                                                │  Web UI    │
                                                                └────────────┘
```

#### 1.1 Data Ingestion

**Strategy**: Bootstrap with historical data, then run nightly incremental sync.

- **Bootstrap**: Download all daily ZIPs from 2011-01-01 to present (~5,500 files). At ~400KB average per ZIP, total download is ~2.2GB. Parse XML, deduplicate by contract ID (later exports may update earlier contracts via the `chan` field).
- **Incremental**: Cron job at 03:00 daily downloads previous day's ZIP, parses, upserts into database.
- **Deduplication**: Use contract `ID` as primary key. When a contract appears in multiple daily exports (updates/amendments), keep the most recent version but track change history.

**Database schema (PostgreSQL)**:

```sql
CREATE TABLE contracts (
    id BIGINT PRIMARY KEY,              -- CRZ contract ID
    contract_number TEXT,                -- nazov
    subject TEXT,                        -- predmet
    buyer_name TEXT,                     -- zs1
    buyer_ico TEXT,                      -- ico1
    buyer_address TEXT,                  -- sidlo1
    supplier_name TEXT,                  -- zs2
    supplier_ico TEXT,                   -- ico
    supplier_address TEXT,               -- sidlo
    amount NUMERIC(15, 2),              -- suma_zmluva
    total_amount NUMERIC(15, 2),        -- suma_spolu
    rezort_id INTEGER,                   -- rezort
    status SMALLINT,                     -- stav
    contract_type SMALLINT,              -- typ (contract vs amendment)
    contract_kind SMALLINT,              -- druh (contract vs order)
    date_published TIMESTAMPTZ,          -- datum_zverejnene
    date_signed DATE,                    -- datum
    date_effective DATE,                 -- datum_ucinnost
    date_valid_until DATE,               -- datum_platnost_do
    last_changed TIMESTAMPTZ,            -- chan
    raw_xml JSONB,                       -- full original record for audit

    -- Enrichment fields (Phase 1)
    category TEXT,                        -- LLM-assigned: legal, marketing, IT, construction, etc.
    category_confidence REAL,             -- 0.0 - 1.0
    category_reasoning TEXT,              -- LLM explanation for classification
    subcategory TEXT,                     -- More specific: "IT consulting", "web development"
    flags TEXT[],                         -- Anomaly flags: unusual_amount, repeated_supplier, etc.

    -- Search
    search_vector tsvector,              -- Full-text search on Slovak text
    embedding vector(1024),              -- Semantic embedding for similarity search

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE attachments (
    id BIGINT PRIMARY KEY,               -- Attachment ID from CRZ
    contract_id BIGINT REFERENCES contracts(id),
    filename TEXT,                        -- dokument1
    original_name TEXT,                   -- nazov
    file_size INTEGER,                    -- velkost1
    content_type TEXT,                    -- pdf, doc, etc.

    -- Phase 2 fields
    text_extracted TEXT,                  -- Full text from PDF
    text_extraction_method TEXT,          -- 'pdftotext', 'ocr_tesseract', 'ocr_cloud'
    text_extracted_at TIMESTAMPTZ,
    ocr_confidence REAL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE suppliers (
    ico TEXT PRIMARY KEY,
    name TEXT,
    address TEXT,
    -- Enrichment from business register
    nace_codes TEXT[],
    legal_form TEXT,
    established_date DATE,
    employee_count_range TEXT,
    annual_revenue_range TEXT,
    orsr_data JSONB,                     -- Raw business register data
    contract_count INTEGER,
    total_contract_value NUMERIC(15, 2),
    first_contract_date DATE,
    last_contract_date DATE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE classification_runs (
    id SERIAL PRIMARY KEY,
    run_date DATE,
    contracts_processed INTEGER,
    contracts_classified INTEGER,
    model_used TEXT,
    avg_confidence REAL,
    cost_usd NUMERIC(8, 4),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_contracts_category ON contracts(category);
CREATE INDEX idx_contracts_supplier_ico ON contracts(supplier_ico);
CREATE INDEX idx_contracts_buyer_ico ON contracts(buyer_ico);
CREATE INDEX idx_contracts_rezort ON contracts(rezort_id);
CREATE INDEX idx_contracts_published ON contracts(date_published);
CREATE INDEX idx_contracts_amount ON contracts(amount);
CREATE INDEX idx_contracts_search ON contracts USING gin(search_vector);
CREATE INDEX idx_contracts_embedding ON contracts USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_attachments_contract ON attachments(contract_id);
```

#### 1.2 LLM Classification Pipeline

**Service category taxonomy** (designed for the 360ka use case):

```
Level 1 (broad)          Level 2 (specific)
─────────────────────────────────────────────
legal                    legal_representation, legal_consulting, notary, mediation
consulting               management_consulting, financial_consulting, hr_consulting, strategy
IT                       software_development, IT_infrastructure, IT_consulting, licenses, hosting
marketing                advertising, PR, media, events, branding, social_media
construction             building, renovation, maintenance, roads, infrastructure
healthcare               medical_equipment, pharmaceuticals, health_services
education                training, courses, scholarships, research
transport                fleet, fuel, travel, logistics, shipping
facilities               cleaning, security, catering, utilities, waste
real_estate              rental, lease, purchase, easement
financial                insurance, banking, audit, accounting
HR                       employment, recruitment, temp_staffing
grants                   EU_funds, state_subsidies, donations
other                    cemetery, culture, sports, miscellaneous
```

**Classification prompt (batch mode)**:

```
You are classifying Slovak government contracts into service categories.

Given the following contract metadata, assign:
1. category (from the taxonomy)
2. subcategory (from the taxonomy)
3. confidence (0.0-1.0)
4. reasoning (1 sentence explaining why)

Contract:
- Subject: {predmet}
- Supplier: {zs2}
- Buyer: {zs1}
- Amount: {suma_zmluva} EUR
- Ministry: {rezort_name}

Respond as JSON: {"category": "...", "subcategory": "...", "confidence": 0.X, "reasoning": "..."}
```

**Batch processing strategy**:
- Use Claude Haiku 4.5 for cost efficiency (~$0.001 per contract)
- Process in batches of 100 contracts per API call (using batch API)
- Full 5.5M historical backfill: ~$5,500 at Haiku rates
- Daily incremental: ~$2.80/day for ~2,800 contracts
- For ambiguous cases (confidence < 0.6), escalate to Sonnet for re-classification

**Confidence calibration**:
- High confidence (>0.8): "Zmluva o poskytovaní právnych služieb" → legal (title is explicit)
- Medium confidence (0.5-0.8): "Zmluva o dielo" + supplier "STRABAG" → construction (supplier name is strong signal)
- Low confidence (<0.5): "Zmluva o dielo" + supplier "ABC s.r.o." → needs PDF content

#### 1.3 API Layer

**FastAPI endpoints**:

```
GET  /api/v1/contracts                    -- Search & filter
GET  /api/v1/contracts/{id}               -- Contract detail
GET  /api/v1/contracts/{id}/attachments   -- List attachments
GET  /api/v1/contracts/search?q=          -- Semantic search
GET  /api/v1/suppliers/{ico}              -- Supplier profile + contract history
GET  /api/v1/suppliers/{ico}/contracts    -- All contracts for a supplier
GET  /api/v1/stats/categories             -- Category distribution
GET  /api/v1/stats/top-suppliers          -- Top suppliers by value/count
GET  /api/v1/anomalies                    -- Flagged suspicious patterns
GET  /api/v1/export                       -- Bulk export of enriched data
```

**Query parameters for /contracts**:
- `category`, `subcategory` — filter by service type
- `supplier_ico`, `buyer_ico` — filter by party
- `rezort` — filter by ministry
- `amount_min`, `amount_max` — price range
- `date_from`, `date_to` — publication date range
- `q` — fulltext search (Slovak-aware)
- `sort` — by date, amount, relevance
- `page`, `per_page` — pagination

#### 1.4 Agentic Interface

A conversational agent (Claude) that can:
1. **Answer natural language queries**: "Koľko zaplatilo Ministerstvo pôdohospodárstva za marketing v roku 2025?"
2. **Generate reports**: "Vytvor prehľad top 10 dodávateľov právnych služieb pre všetky ministerstvá"
3. **Flag anomalies**: "Upozorni ma na zmluvy nad 100,000 EUR s novými dodávateľmi"
4. **Compare patterns**: "Porovnaj výdavky na IT konzulting naprieč ministerstvami"

The agent uses the REST API as its tool interface — it constructs queries, retrieves data, and synthesizes answers. This is a standard tool-use pattern with Claude.

---

### Phase 2: PDF Content Intelligence

**Goal**: Extract and index the actual text content of contract PDFs, enabling true full-text search and more accurate classification.

#### 2.1 PDF Processing Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Attachment  │────▶│  Download    │────▶│  Classify    │────▶│  Extract     │
│  Queue       │     │  (rate-ltd)  │     │  PDF type    │     │  Text        │
└─────────────┘     └──────────────┘     └──────┬───────┘     └──────┬───────┘
                                                 │                     │
                                          ┌──────┴───────┐     ┌──────┴───────┐
                                          │ born-digital │     │  Re-classify │
                                          │ → pdftotext  │     │  with full   │
                                          │ scan         │     │  text context │
                                          │ → OCR        │     └──────────────┘
                                          └──────────────┘
```

**Prioritization strategy** (process high-value contracts first):
1. Contracts > €100,000 where category confidence < 0.7
2. Contracts from top 20 ministries by budget
3. Contracts classified as "other" or with low confidence
4. Remaining contracts by recency

**OCR approach**:
- **First pass**: Try `pdftotext` — if >100 chars extracted, use that (free, fast)
- **Second pass**: For scan-only PDFs, use Tesseract with `slk` (Slovak) language model
- **Third pass**: For poor Tesseract results (<50% confidence), use cloud OCR (Google Document AI or Azure Form Recognizer) which handles Slovak better

**Rate limit compliance**:
- Download queue runs at 1 request per 3 seconds during daytime (safe margin under the 1/2s limit)
- 3 requests per second between 20:00-06:00
- Nighttime throughput: ~36,000 PDFs/night (10 hours × 3,600 seconds × 1 req/s average)
- Full backfill of 5.5M attachments: ~153 nights (~5 months) — acceptable for historical data

**Storage**: Store extracted text in `attachments.text_extracted`. Average extracted text ~5KB per contract → 5.5M × 5KB = ~27.5GB of text. Manageable in PostgreSQL.

#### 2.2 Enhanced Classification

With full text available, re-run classification on contracts where:
- Phase 1 confidence was < 0.7
- Category was "other"
- Subject was generic ("Zmluva o dielo", "Zmluva o poskytovaní služieb")

Expected improvement: from ~75% accuracy (metadata-only) to ~95% (with full text).

**Enhanced prompt** adds contract text (first 2000 chars) as additional context.

#### 2.3 Key Clause Extraction

For high-value contracts (>€50,000), extract structured information:
- **Scope of work**: What exactly is being delivered
- **Payment terms**: Milestones, schedule, penalties
- **Duration**: Contract period
- **Termination clauses**: Conditions for early termination
- **Subcontracting**: Whether subcontracting is allowed

Store as JSONB in a `contract_details` column.

---

### Phase 3: Cross-Source Investigation Platform

**Goal**: Cross-reference CRZ data with other public sources to detect patterns, anomalies, and potential corruption indicators.

#### 3.1 Business Register Integration (ORSR)

**Data source**: `orsr.sk` — Slovak Business Register

For each unique supplier ICO in CRZ (~500K unique ICOs estimated):
- Company name, legal form, registered address
- NACE activity codes (reveals actual business type)
- Date of establishment
- Statutory representatives (owners, directors)
- Capital structure

**Value**: If a company registered as "car repair" (NACE 45.20) wins a "marketing consulting" contract, that's a red flag.

#### 3.2 Anomaly Detection Patterns

| Pattern | Description | Detection Method |
|---------|-------------|-----------------|
| **Category mismatch** | NACE codes don't match contract category | Compare ORSR NACE with LLM classification |
| **New company, big contract** | Company < 1 year old wins contract > €100K | Join establishment date with contract date/amount |
| **Concentration** | Single supplier dominates a ministry's spending | Aggregate by supplier × rezort, flag >20% share |
| **Price anomaly** | Contract price far from median for same category | Statistical outlier detection per category |
| **Splitting** | Multiple contracts just below procurement threshold (€50K) | Detect clusters of contracts with same parties near thresholds |
| **Amendment inflation** | Original contract amount grows >50% via amendments | Track amendment chain via parent contract references |
| **Revolving door** | Same company appears across many unrelated ministries | Count distinct rezorts per supplier |
| **Ghost bidder** (Vestník) | Company repeatedly bids but never wins except with specific partner | Analyze bid/win patterns in procurement data |

#### 3.3 Vestník Integration (Public Procurement Journal)

**Data source**: `vestnik.uvo.gov.sk` — Public Procurement Bulletin

Cross-reference:
- Match CRZ contracts to Vestník tender IDs (some CRZ records include `uvo` field)
- For each tender: number of bidders, bid amounts, winner
- Detect bid-rigging: companies that always appear together but take turns winning

This is the most complex data source. The `uvo` field in CRZ XML is often empty, so matching requires fuzzy joining on parties + amounts + dates.

#### 3.4 Institution Website Scraping

For individual ministry websites (e.g., Ministerstvo pôdohospodárstva):
- Scrape invoices and orders (not in CRZ)
- Normalize into same schema
- Enable queries like "all flights booked by Ministry of Agriculture"

**Challenges**: Each institution has different website structure, no standard format. This requires per-institution scrapers — labor-intensive but high-value.

---

## Technology Stack

| Component | Technology | Reasoning |
|-----------|-----------|-----------|
| Language | Python 3.12+ | Best ecosystem for data processing, ML, LLM APIs |
| Database | PostgreSQL 16 + pgvector | Full-text search (Slovak), vector search, JSONB, mature |
| API | FastAPI | Async, auto-docs, type-safe, fast |
| Task queue | Celery + Redis | For PDF download queue, classification jobs |
| LLM | Claude Haiku 4.5 (bulk), Sonnet 4.6 (agent) | Cost-efficient classification + capable agent |
| OCR | Tesseract 5 + slk model | Free, good Slovak support |
| PDF | pdftotext (poppler) | Fast, reliable for born-digital PDFs |
| Containerization | Docker Compose | Simple local dev, easy deployment |
| Scheduling | Cron (or Celery Beat) | Nightly ingestion + classification |

## Cost Estimates

### Phase 1 (Metadata Intelligence)

| Item | One-time | Monthly |
|------|----------|---------|
| Historical backfill classification (5.5M contracts × Haiku) | ~$5,500 | — |
| Daily classification (~2,800/day × Haiku) | — | ~$84 |
| PostgreSQL hosting (managed, 100GB) | — | ~$50 |
| API hosting (small VM) | — | ~$20 |
| **Total** | **~$5,500** | **~$154** |

### Phase 2 (PDF Intelligence) — incremental

| Item | One-time | Monthly |
|------|----------|---------|
| OCR processing (cloud, for hard cases) | ~$2,000 | ~$100 |
| Storage for extracted text (~30GB) | — | ~$10 |
| Re-classification of ambiguous contracts | ~$500 | ~$50 |
| **Total** | **~$2,500** | **~$160** |

### Phase 3 (Cross-Source) — incremental

| Item | One-time | Monthly |
|------|----------|---------|
| Business register scraping/API | ~$500 | ~$50 |
| Vestník data processing | ~$1,000 | ~$100 |
| Additional compute for anomaly detection | — | ~$50 |
| **Total** | **~$1,500** | **~$200** |

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| CRZ rate limiting blocks our IP | Pipeline stops | Medium | Use rotating IPs for PDF downloads; rely on daily ZIP (not scraping) for metadata |
| LLM classification accuracy below 70% | Low trust in categories | Low | Pilot on 1000 contracts first, measure accuracy, iterate on taxonomy + prompts |
| Daily ZIP format changes | Ingestion breaks | Low | Schema validation on ingest, alerts on parse failures |
| OCR quality too low for Slovak | Can't extract text from scans | Medium | Fall back to cloud OCR (Google/Azure) which handles Slovak well |
| PostgreSQL can't handle 5.5M contracts | Slow queries | Very low | Well-indexed; Postgres handles 10M+ rows routinely |
| Cost overrun on LLM API | Budget exceeded | Low | Use Haiku for bulk, monitor daily spend, set hard limits |
| Legal issues with scraping | Cease and desist | Very low | CRZ is public by law; daily ZIP is explicitly provided for machine access |

## Success Criteria

### Phase 1 MVP
- [ ] All historical contracts (2011-present) ingested into database
- [ ] >80% of contracts classified into service categories with >0.7 confidence
- [ ] API responds to filtered queries in <500ms
- [ ] Natural language agent can answer "how much did Ministry X spend on {category} in {year}?"
- [ ] Daily pipeline runs unattended, classifies new contracts within 24h

### Phase 2
- [ ] Text extracted from >50% of PDF attachments
- [ ] Classification accuracy >90% for contracts with extracted text
- [ ] Full-text search across contract content works in <2s

### Phase 3
- [ ] Supplier profiles enriched with business register data for top 10,000 suppliers
- [ ] At least 3 anomaly detection patterns implemented and generating alerts
- [ ] Cross-reference with Vestník for at least 2024-2025 contracts

## Open Questions

1. **Taxonomy granularity**: Is the proposed 14-category / ~40-subcategory taxonomy right? Or do journalists need different slicing?
2. **Historical depth**: How far back is useful? 2011-present is ~15 years. Would 2020-present suffice for MVP?
3. **Language**: Should the UI/API be Slovak-only, or bilingual (SK/EN)?
4. **Access control**: Is this fully public, or are some features (anomaly detection, raw data export) restricted?
5. **Deployment**: Cloud (which provider?) or self-hosted? Budget constraints?
6. **Existing tools**: Does 360ka already have any infrastructure, databases, or tools for this domain?
