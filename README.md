# CRZ Explorer

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/query-DuckDB-FFF000.svg)](https://duckdb.org/)
[![Delta Lake](https://img.shields.io/badge/storage-Delta%20Lake-003366.svg)](https://delta.io/)
[![Docker](https://img.shields.io/badge/deploy-Docker-2496ED.svg)](compose.yaml)

> Intelligent search and red-flag detection across Slovak government contracts from the [Central Register of Contracts](https://www.crz.gov.sk/) (CRZ).

CRZ.gov.sk only searches contract titles. CRZ Explorer searches across **all fields simultaneously** — contract titles, supplier names, buyer names, notes, extracted text from PDFs, and debtor registries. A legal services contract titled just "Zmluva o dielo" but filed under "Advokátska kancelária XY" is no longer invisible.

---

## Try it now

```bash
git clone https://github.com/zltastopa/zmluvy.git && cd zmluvy
uv sync
uv run python delta_store/serve.py
# → http://localhost:8002
```

### What you can do

- **Full-text search** (BM25) across contract titles, suppliers, buyers, notes, and extracted text
- **36 red flag rules** — tax debtors, terminated companies, NACE mismatches, contract splitting, signatory overlap, and more
- **LLM-powered extraction** of structured data from contract PDFs (subjects, penalties, hidden entities, signatories)
- **Cross-reference** against Financial Administration tax reliability, VšZP/Sociálna poisťovňa debtor lists, and RÚZ company registry
- **Investigation agents** — automated deep-dive analysis powered by Claude
- **Dashboard** with charts, anomalies, top contracts, and filtering
- **Datasette-compatible SQL API** for ad-hoc queries

### Example searches

| Search for | What it finds |
|-----------|--------------|
| `advokát` | Legal services (found in supplier name, not just contract title) |
| `COLAS` | Construction contracts by COLAS Slovakia |
| `44556677` | All contracts for a specific ICO |
| `marketing` | Marketing and advertising contracts |
| `masáž` | Massage/wellness service contracts |

---

## Architecture

```
┌─────────────────┐     ┌────────────────────┐     ┌──────────────────┐
│  CRZ Open Data  │────▶│  ingest.py         │────▶│  delta_store/    │
│  (daily XMLs)   │     │  (6-step pipeline) │     │  tables/         │
└─────────────────┘     └────────────────────┘     │  ├── zmluvy      │
                              │                     │  ├── extractions │
                              │ OCR (ProcessPool)   │  ├── prilohy     │
                              │ LLM (OpenRouter)    │  ├── red_flags   │
                              ▼                     │  ├── flag_rules  │
┌─────────────────┐     ┌────────────────────┐     │  └── ...15 total │
│  Browser        │◀───▶│  serve.py          │◀────└──────────────────┘
│  (dashboard)    │     │  (FastAPI + DuckDB) │        430 MB Parquet
└─────────────────┘     └────────────────────┘
         │
         │  /api/*
         ▼
┌─────────────────┐
│  Claude agents  │  Investigation skills
│  (crz-investigate, crz-deep-investigate)
└─────────────────┘
```

**Storage**: Delta Lake (Parquet files + `_delta_log/` transaction log) — 430 MB vs 981 MB SQLite.
**Query engine**: DuckDB in-memory — materializes Delta tables on startup (~2-3 seconds), then serves from RAM.
**Concurrency**: Threading lock on DuckDB connection handles parallel dashboard requests safely.

---

## Repository structure

```
├── delta_store/           Delta Lake backend
│   ├── ingest.py          End-to-end pipeline (download → parse → PDF → text → extract → flag)
│   ├── serve.py           FastAPI + DuckDB server (port 8002)
│   ├── migrate_from_sqlite.py  One-time SQLite → Delta migration
│   ├── tables/            Delta Lake tables (Parquet + _delta_log/)
│   └── tests/             Parity tests, flag rule tests, SQL validation tests
├── frontend/              Dashboard and detail page (HTML/JS/Chart.js)
│   ├── dashboard.html     Main dashboard with search, charts, anomalies
│   └── detail.html        Contract detail page with flags and extractions
├── agents/                Claude Code agent definitions
│   ├── report-writer.md   Generates investigation reports
│   ├── supplier-profiler.md  Enriches supplier data (FinStat, UVO, RPVS)
│   ├── network-mapper.md  Maps corporate networks via foaf.sk
│   ├── cross-referencer.md Cross-references findings across sources
│   └── phase-gater.md     Gates investigation phases
├── skills/                Claude Code investigation skills
│   ├── crz-investigate/   Broad scan of a time period
│   ├── crz-deep-investigate/  Deep dive into one company
│   ├── sql-analytics/     17 standard investigative SQL queries
│   ├── critical-validation/  Validate findings against innocent explanations
│   ├── finstat-enrichment/   FinStat financial data
│   ├── uvo-procurement/   UVO public procurement lookup
│   ├── rpvs-lookup/       RPVS beneficial ownership (Playwright)
│   └── foaf-network/      Corporate network mapping (Playwright)
├── pipeline/              Legacy SQLite pipeline (still functional)
├── settings.py            Shared configuration (env vars, path resolution)
├── Dockerfile             Container build
├── compose.yaml           Docker Compose deployment
└── pyproject.toml         Dependencies
```

---

## Quick start

### Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **Tesseract OCR** + **ocrmypdf** (for scanned PDF processing)
- **pdftotext** (poppler-utils, for native PDF text extraction)

### Install and run

```bash
# Clone & install dependencies
git clone https://github.com/zltastopa/zmluvy.git
cd zmluvy
uv sync

# Configure
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY for LLM extraction

# Ingest data for a date range
uv run python delta_store/ingest.py --from 2026-03-01 --to 2026-03-19

# Start the server
uv run python delta_store/serve.py
# → Dashboard:  http://localhost:8002
# → SQL API:    http://localhost:8002/data/crz.json?sql=SELECT+count(*)+FROM+zmluvy
```

---

## Ingestion pipeline

A single script handles the full workflow — from downloading CRZ daily exports to flagging contracts. Data is stored as Delta Lake tables (Parquet + transaction log) in `delta_store/tables/`.

```bash
# Full pipeline for a single day
uv run python delta_store/ingest.py --date 2026-03-19

# Full pipeline for a date range
uv run python delta_store/ingest.py --from 2026-03-01 --to 2026-03-19

# Run a single step
uv run python delta_store/ingest.py --date 2026-03-19 --step extract --limit 100
```

### Pipeline steps

| Step | Name | What it does | Resource |
|------|------|-------------|----------|
| 1 | `download` | Fetch daily ZIP from CRZ, extract XML | Network |
| 2 | `parse` | XML → Delta tables (zmluvy, prilohy, rezorty) | CPU (fast) |
| 3 | `pdf` | Download PDF attachments for new contracts | Network |
| 4 | `text` | PDF → text via pdftotext + OCR fallback (ProcessPool) | CPU-heavy |
| 5 | `extract` | LLM extraction of structured fields via OpenRouter | LLM API |
| 6 | `ruz` | Refresh RUZ entity data from RegisterUZ API (CRZ-connected only) | Network |
| 7 | `flag` | Evaluate 36 flag rules → red_flags table | CPU (fast) |

### Key design decisions

- **Idempotent** — every step skips already-processed items. Safe to re-run or resume after Ctrl+C.
- **Delta Lake merge** — steps 2, 5, and 6 use merge (match → update, no match → insert) instead of append-only writes.
- **ProcessPoolExecutor for OCR** — 3.1x faster than ThreadPool since Tesseract is CPU-bound (bypasses GIL).
- **Parallel** — PDF download, text conversion, and LLM extraction run with `--workers N` (default: 8).

### CLI options

| Flag | Purpose | Default |
|------|---------|---------|
| `--date YYYY-MM-DD` | Single date | today |
| `--from / --to` | Date range (YYYY-MM-DD or YYYY-MM) | — |
| `--step NAME` | Run only one step | all steps |
| `--workers N` | Parallel workers | 8 |
| `--limit N` | Max items per step | 0 (unlimited) |
| `--model MODEL` | LLM model for extraction | env `OPENROUTER_MODEL` |
| `--force` | Re-process existing outputs | false |

---

## Red flag rules

36 rules detect anomalies across contracts. Each rule produces entries in the `red_flags` Delta table with severity levels: `danger`, `warning`, `info`.

### Danger (high confidence)

| Flag | Description |
|------|-------------|
| `tax_unreliable` | Supplier is on Financial Administration's "less reliable" list |
| `vszp_debtor` | Supplier is a VšZP health insurance debtor |
| `socpoist_debtor` | Supplier is a Sociálna poisťovňa debtor |
| `fs_tax_debtor` | Supplier is on Financial Administration's tax debtor list |
| `fs_vat_deregistered` | Supplier was removed from VAT register |
| `supplier_advantage` | Penalty clauses favor the supplier (unusual in government contracts) |
| `terminated_company` | All RÚZ entries for supplier are terminated (excludes ICO reuse) |
| `negative_equity` | Supplier has negative equity per RÚZ filings |
| `fresh_micro_large` | Fresh micro company with large contract |

### Warning (needs review)

| Flag | Description |
|------|-------------|
| `signatory_overlap` | Person signs for 10+ different suppliers |
| `contract_splitting` | 5+ contracts under 15k EUR with same buyer in one year |
| `nace_mismatch` | Supplier's registered industry doesn't match contract category |
| `hidden_entities` | Contract contains third parties beyond the main parties |
| `bezodplatne` | Private-entity gratis contract |
| `rapid_succession` | 3+ contracts from same buyer within 14 days |
| `fresh_company` | Company established less than 1 year before signing |
| `missing_attachment` | No PDF document uploaded |

### Info (contextual)

| Flag | Description |
|------|-------------|
| `missing_expiry` | High-value contract (>10k EUR) without expiry date (excludes leases, cemetery) |
| `hidden_price` | Contract amount is NULL |
| `missing_ico` | Supplier has no ICO |
| `weekend_signing` | High-value (>50k) mid-month weekend signing |
| `not_in_ruz` | Private supplier (non-00 ICO) not found in RÚZ |

---

## Web server

FastAPI application serving the dashboard, contract detail pages, and API endpoints.

```bash
uv run python delta_store/serve.py --host 0.0.0.0 --port 8002
```

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` `/dashboard` | Interactive dashboard with charts and search |
| `/detail/{id}` | Contract detail with flags, extractions, attachments |
| `/search?q=...` | Full-text search (BM25 + LIKE across 7 sources) |
| `/api/summary` | Aggregate stats (counts, totals, debtors) |
| `/api/contracts` | Paginated contract list with filters |
| `/api/contract/{id}` | Single contract with full details |
| `/api/timeline` | Monthly contract counts |
| `/api/by_rezort` | Contracts by government department |
| `/api/anomalies` | Anomaly summary |
| `/api/top_contracts` | Highest-value contracts |
| `/api/filters` | Available filter values |
| `/data/crz.json?sql=...` | Datasette-compatible SQL API (read-only, sandboxed) |
| `/methodology` | Flag rule methodology page |

### Full-text search

DuckDB FTS extension with BM25 scoring across 6 fields (`nazov_zmluvy`, `dodavatel`, `objednavatel`, `poznamka`, `popis`, `dodavatel_adresa`). Search also checks extractions, attachments, ICO fields, and debtor registries via LIKE. Results ranked by flag count then date.

- **76,563** unique terms in dictionary
- **2,120,262** term-document postings
- **140,310** documents indexed

---

## Deployment

### Option A: Direct (recommended for single server)

```bash
# 1. Clone & install
git clone https://github.com/zltastopa/zmluvy.git /opt/crz-experiments
cd /opt/crz-experiments
uv sync

# 2. Configure
cp .env.example .env
# Set OPENROUTER_API_KEY

# 3. Initial data load (backfill)
uv run python delta_store/ingest.py --from 2022-01 --to 2026-03

# 4. Start server
uv run python delta_store/serve.py --host 0.0.0.0 --port 8002

# 5. Set up daily cron
crontab -e
# 0 6 * * * cd /opt/crz-experiments && uv run python delta_store/ingest.py --date $(date +\%Y-\%m-\%d) >> /var/log/crz-ingest.log 2>&1
```

**systemd service** (`/etc/systemd/system/crz-explorer.service`):

```ini
[Unit]
Description=CRZ Explorer
After=network.target

[Service]
WorkingDirectory=/opt/crz-experiments
ExecStart=/opt/crz-experiments/.venv/bin/python delta_store/serve.py --host 0.0.0.0 --port 8002
Restart=always
User=crz

[Install]
WantedBy=multi-user.target
```

### Option B: Docker Compose

```bash
docker compose up -d --build
```

The app listens on port 8002 inside the container, published as `127.0.0.1:8321` on the host. Put nginx in front for TLS.

The Compose setup mounts `delta_store/tables/` from the host, keeping deploys fast even with ~430 MB of data.

### No external database needed

DuckDB runs in-process. Delta tables are just Parquet files on disk. The server materializes everything into RAM on startup (~2-3 seconds). No PostgreSQL, no Redis, no database server to manage.

---

## Investigation agents

Claude Code agents automate contract analysis. Two orchestrators compose reusable building blocks:

| Orchestrator | What it does |
|---|---|
| **crz-investigate** | Broad scan: sql-analytics → phase-gater → N supplier-profilers (parallel) → network-mapper → cross-referencer → report-writer |
| **crz-deep-investigate** | Deep dive into one company: target mapping → phase-gater → profilers → network-mapper (deep) → cross-referencer → report-writer |

| Agent | Model | Purpose |
|-------|-------|---------|
| `report-writer` | Opus | Generates structured investigation reports |
| `supplier-profiler` | Sonnet | Enriches suppliers via FinStat, UVO, RPVS |
| `network-mapper` | Sonnet | Maps corporate networks via foaf.sk |
| `cross-referencer` | Opus | Cross-references findings across data sources |
| `phase-gater` | Haiku | Decides which investigation phases to run |

---

## Configuration

Environment is loaded from `.env` by all entrypoints. CLI flags override `.env` values.

| Variable | Purpose | Default |
|----------|---------|---------|
| `CRZ_DATA_DIR` | Base data directory | `data` |
| `CRZ_PDF_DIR` | Downloaded PDFs | `data/pdfs` |
| `CRZ_TEXT_DIR` | Extracted text | `data/texts` |
| `CRZ_EXTRACTIONS_DIR` | LLM extractions | `data/extractions` |
| `OPENROUTER_API_KEY` | API key for LLM extraction | — |
| `OPENROUTER_BASE_URL` | OpenRouter API base URL | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | Model for extraction | `google/gemini-2.5-flash-lite` |
| `PDFTOTEXT_BIN` | Path to `pdftotext` binary | `pdftotext` |

---

## Data sources

| Source | Description | License |
|--------|-------------|---------|
| **[CRZ](https://www.crz.gov.sk/)** | Daily XML exports — Office of the Government of the Slovak Republic | Public by law ([Act No. 211/2000 Coll.](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2000/211/)) |
| **[Tax reliability](https://report.financnasprava.sk/)** | `ds_iz_ran.xml` — Finančná správa SR, updated daily | CC0 |
| **[VšZP debtors](https://www.vszp.sk/)** | Health insurance debtor list | Public |
| **[Sociálna poisťovňa](https://www.socpoist.sk/)** | Social insurance debtor list | Public |
| **[RÚZ](https://registeruz.sk/)** | Register of financial statements (company data, NACE, equity) | Public |
| **[FinStat](https://finstat.sk/)** | Financial data enrichment (via supplier-profiler agent) | Commercial |
| **[UVO](https://www.uvo.gov.sk/)** | Public procurement journal | Public |
| **[RPVS](https://rpvs.gov.sk/)** | Register of public sector partners (beneficial ownership) | Public |
| **[foaf.sk](https://foaf.sk/)** | Corporate network mapping | Public |

---

## Testing

```bash
# Flag rule accuracy tests (42 tests)
uv run pytest delta_store/tests/test_flag_rules.py -v

# SQL injection / sandbox tests
uv run pytest delta_store/tests/test_sql_validation.py -v

# Delta ↔ SQLite parity tests (requires both servers running)
uv run pytest delta_store/tests/test_parity.py -v
```

---

## Contributing

Found a bug or have an idea? [Open an issue](https://github.com/zltastopa/zmluvy/issues/new) or submit a pull request. All contributions are welcome.

## License

[MIT](LICENSE) — made with care by [Žltá stopa](https://github.com/zltastopa).
