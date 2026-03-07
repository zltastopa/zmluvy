# CRZ Open Dataset — Deployment Plan

Automatically updated open dataset of Slovak government contracts from
the Central Register of Contracts (CRZ), aimed at journalists, civil
society, and researchers.

## Architecture

```
GitHub Actions (nightly cron, ~02:00 UTC)
  |
  +-- Download today's CRZ XML export
  |     curl https://www.crz.gov.sk/export/YYYY-MM-DD.zip
  |
  +-- Parse XML -> SQL upserts (load_crz.py, adapted)
  |
  +-- Push ~2,500 new rows to Cloudflare D1
  |     wrangler d1 execute crz-db --remote --file=daily.sql
  |
  +-- Download new PDF attachments
  |     Only for contracts not yet extracted
  |
  +-- pdftotext / OCR -> plain text
  |
  +-- LLM extraction (OpenRouter, Gemini Flash Lite)
  |     ~2,500 contracts/day, ~$2-3/day
  |
  +-- Push extractions to D1
  |
  +-- Export daily Parquet slice (YYYY-MM-DD.parquet)
  |
  +-- Push to HuggingFace dataset
        huggingface-cli upload crz-contracts data/YYYY-MM-DD.parquet

Journalists --> Cloudflare Pages search UI + Workers API + D1 (FTS5)
Everyone else --> HuggingFace (Parquet, DuckDB-queryable)
```

## Distribution channels

### 1. Cloudflare D1 + Workers + Pages (live search)

A custom search UI hosted on Cloudflare Pages, backed by a Worker that
queries D1 with FTS5 full-text search.

**What journalists get:**
- Full-text search across contract titles, suppliers, buyers, notes
- Filters by amount, date, rezort, service category
- Export results as CSV
- Direct links to contracts on crz.gov.sk

**Stack:**
- Cloudflare D1: SQLite database with FTS5 virtual table
- Cloudflare Worker: thin API (~50 lines JS) handling search queries
- Cloudflare Pages: static frontend (~300 lines HTML/JS)

**Free tier limits vs our usage:**

| Resource          | Free limit      | Our usage              |
|-------------------|-----------------|------------------------|
| D1 storage        | 500 MB          | ~11 MB now, ~50 MB/yr  |
| D1 reads/day      | 5M rows         | Low (journalist queries)|
| D1 writes/day     | 100K rows       | ~2,500 contracts/day   |
| Workers reqs/day  | 100K            | Low                    |
| Pages             | Unlimited       | Static site            |

**Daily update mechanism:**
- GitHub Actions runs `wrangler d1 execute crz-db --remote --file=daily.sql`
- SQL file contains `INSERT OR REPLACE INTO zmluvy ...` for new contracts
- FTS5 index updated via triggers (already configured in load_crz.py)
- Extractions table updated separately after LLM processing

**Known limitations:**
- D1 databases with FTS5 tables cannot be exported via `wrangler d1 export`
  (must rebuild from source if migrating away)
- D1 enforces daily free tier limits; exceeding blocks queries until
  00:00 UTC reset

### 2. HuggingFace Dataset (bulk open data)

Daily Parquet slices pushed to a HuggingFace dataset repo, queryable
via DuckDB WASM on the HuggingFace viewer or via download.

**Repository structure:**
```
crz-contracts/
  README.md              # dataset card (schema, license, update freq)
  data/
    zmluvy/
      2026-03-05.parquet
      2026-03-06.parquet
      2026-03-07.parquet  # today's new/updated contracts
    extractions/
      2026-03-05.parquet
      2026-03-06.parquet
      2026-03-07.parquet  # today's LLM extractions
```

**What users get:**
- Built-in dataset viewer with filtering/sorting on huggingface.co
- DuckDB WASM queries across all daily slices:
  `SELECT * FROM 'data/zmluvy/*.parquet' WHERE suma > 100000`
- Full download for offline analysis
- Auto-generated Croissant ML metadata for discoverability
- Git-based versioning (every daily push is a new commit)

**Daily update mechanism:**
- GitHub Actions exports today's contracts as Parquet (via DuckDB or
  pyarrow)
- `huggingface-cli upload crz-contracts data/ --repo-type dataset`
- Each daily file is ~500 KB (~2,500 rows)

**Cost:** Free for public datasets. No storage or bandwidth limits.

**Significance:** Slovakia has no publisher in the OCP Data Registry
(100+ publishers, 50+ countries). This would be the first structured,
machine-readable Slovak contract dataset with daily updates.

## GitHub Actions workflow

**Trigger:** `schedule: cron: "0 2 * * *"` (daily at 02:00 UTC)
plus `workflow_dispatch` for manual runs.

**Secrets required:**
- `CLOUDFLARE_API_TOKEN` — for wrangler D1 access
- `CLOUDFLARE_ACCOUNT_ID` — Cloudflare account
- `HF_TOKEN` — HuggingFace write token
- `OPENROUTER_API_KEY` — for LLM extraction

**Steps:**

1. **Fetch data**
   - Download `https://www.crz.gov.sk/export/{today}.zip`
   - Unzip XML

2. **Parse and generate SQL**
   - Run adapted `load_crz.py` that outputs SQL instead of writing to
     local SQLite
   - Generate `daily.sql` with `INSERT OR REPLACE` statements

3. **Push to D1**
   - `wrangler d1 execute crz-db --remote --file=daily.sql`

4. **Download new PDFs** (for LLM extraction)
   - Query D1 for contracts without extractions
   - Download PDF attachments from crz.gov.sk
   - Convert to text via pdftotext (+ Tesseract for scanned docs)

5. **LLM extraction**
   - Run `extract_contracts.py` on new text files
   - Push extraction results to D1

6. **Export Parquet**
   - Export today's contracts and extractions as Parquet slices
   - Push to HuggingFace

**Estimated runtime:** 10-15 minutes (dominated by PDF download and
LLM extraction). Well within GitHub Actions' 6-hour timeout and free
tier (unlimited minutes for public repos).

## Schema

### D1: zmluvy table

Same as current `crz.db` schema from `load_crz.py`:

| Column              | Type    | Notes                        |
|---------------------|---------|------------------------------|
| id                  | INTEGER | PK, CRZ contract ID          |
| nazov_zmluvy        | TEXT    | Contract title (predmet)      |
| cislo_zmluvy        | TEXT    | Contract number               |
| dodavatel           | TEXT    | Supplier name                 |
| dodavatel_ico       | TEXT    | Supplier ICO                  |
| objednavatel        | TEXT    | Buyer name                    |
| objednavatel_ico    | TEXT    | Buyer ICO                     |
| suma                | REAL    | Contract amount               |
| datum_zverejnenia   | TEXT    | Publication date              |
| datum_podpisu       | TEXT    | Signing date                  |
| poznamka            | TEXT    | Notes                         |
| typ                 | TEXT    | zmluva / dodatok              |
| stav                | TEXT    | aktivna / zrusena             |
| rezort              | TEXT    | Ministry/institution name     |
| crz_url             | TEXT    | Link to crz.gov.sk            |
| ...                 |         | (full schema in load_crz.py)  |

FTS5 index on: `nazov_zmluvy`, `dodavatel`, `objednavatel`,
`poznamka`, `popis`, `dodavatel_adresa`

### D1: extractions table

| Column              | Type    | Notes                        |
|---------------------|---------|------------------------------|
| zmluva_id           | INTEGER | PK, FK to zmluvy             |
| service_category    | TEXT    | LLM-classified category       |
| actual_subject      | TEXT    | What the contract is about    |
| penalty_asymmetry   | TEXT    | Penalty balance assessment    |
| auto_renewal        | BOOLEAN |                               |
| bezodplatne         | BOOLEAN | Gratuitous transfer           |
| funding_type        | TEXT    | EU/state/municipal/none       |
| hidden_entity_count | INTEGER |                               |
| penalty_count       | INTEGER |                               |
| extraction_json     | TEXT    | Full extraction JSON          |

### HuggingFace Parquet schema

Same columns as above, but denormalized — zmluvy fields joined with
extraction fields in a single flat table. Partitioned by publication
date.

## Cost

| Item                      | Monthly cost |
|---------------------------|-------------|
| Cloudflare (D1+Workers+Pages) | $0       |
| GitHub Actions            | $0 (public repo)                  |
| HuggingFace               | $0 (public dataset)              |
| LLM extraction (OpenRouter) | $60-90 (~2,500 contracts/day)   |
| **Total**                 | **$60-90/month** (LLM only)      |

LLM costs can be reduced by:
- Skipping extraction for low-value contracts (cemetery plots, etc.)
- Using cheaper models as they become available
- Batching or caching similar contract types

Without LLM extraction, the entire pipeline is $0/month.

## Implementation order

1. **GitHub Actions workflow** — nightly CRZ XML fetch, parse, SQL
   generation
2. **D1 setup** — create database, schema, FTS index, test upserts
3. **Worker API** — search endpoint over D1
4. **Pages frontend** — search UI
5. **HuggingFace pipeline** — Parquet export and daily push
6. **PDF + LLM extraction** — integrate existing extract_contracts.py
   into the nightly workflow

Steps 1-4 deliver a working searchable interface. Steps 5-6 add the
open dataset and enrichment layers.

## Prior art

This design is informed by research into similar projects:

- **Hlidac statu** (Czech Republic) — 8.5M contracts, Elasticsearch,
  REST API, nonprofit with dedicated servers
- **Prozorro/Dozorro** (Ukraine) — real-time OCDS API, CouchDB, AWS,
  government-funded
- **OpenTender.eu** (EU) — 17.5M tenders, Elasticsearch, CSV/JSON
  bulk download
- **Querido Diario** (Brazil) — Scrapy + OpenSearch + K8s,
  grant-funded
- **Simon Willison's FARA Datasette** — GitHub Actions + Cloud Run,
  ~$0/month
- **US Federal Procurement on HuggingFace** — 99M contracts, 75GB
  Parquet

Our approach takes the zero-cost CI pipeline (a la Willison) with
Cloudflare's free tier for the live interface and HuggingFace for bulk
distribution. This avoids the operational burden of dedicated servers
while serving both journalist and researcher audiences.
