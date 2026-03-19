# CRZ Explorer

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Docker](https://img.shields.io/badge/deploy-Docker-2496ED.svg)](compose.yaml)
[![GitHub issues](https://img.shields.io/github/issues/zltastopa/zmluvy)](https://github.com/zltastopa/zmluvy/issues)

> Intelligent search across Slovak government contracts from the [Central Register of Contracts](https://www.crz.gov.sk/) (CRZ).

CRZ.gov.sk only searches contract titles. But the actual service type is often buried in the **supplier name** or **notes** field. CRZ Explorer searches across **all fields simultaneously** — so a legal services contract titled just "Zmluva o dielo" but filed under "Advokátska kancelária XY" is no longer invisible.

---

## Try it now

**[Open CRZ Explorer in your browser](https://lite.datasette.io/?url=https://github.com/zltastopa/zmluvy/blob/main/crz.db)** — no installation needed, runs entirely via WebAssembly.

### What you can do

- **Full-text search** across contract titles, supplier names, buyer names, and notes
- **Filter** by amount, date, contract type, status, department
- **Red flag detection** for anomalies and risk indicators
- **LLM-powered extraction** of structured data from contract PDFs
- **Tax reliability cross-reference** against the Financial Administration index
- **Export** to CSV or JSON, or write SQL queries directly

### Example searches

| Search for | What it finds |
|-----------|--------------|
| `advokát` | Legal services (found in supplier name, not just contract title) |
| `COLAS` | Construction contracts by COLAS Slovakia |
| `poroty` | Jury/panel contracts (hidden in notes field) |
| `marketing` | Marketing and advertising contracts |
| `dielo` | All "Zmluva o dielo" contracts |

---

## Repository structure

```
├── delta_store/       Delta Lake backend: ingestion, FastAPI server, tests
│   ├── ingest.py      End-to-end pipeline (download → parse → PDF → text → extract → flag)
│   ├── serve.py       FastAPI + DuckDB server (port 8002)
│   └── tables/        Delta Lake tables (Parquet + _delta_log/)
├── frontend/          Dashboard and detail page HTML/JS
├── server/            SQLite web server (serve.py) and CLI runner (run.py)
├── pipeline/          Legacy SQLite-based pipeline scripts
├── docs/              Reference documentation and investigation notes
├── settings.py        Shared configuration (env vars, path resolution)
├── Dockerfile         Container build
├── compose.yaml       Docker Compose deployment
└── crz.db             SQLite database (not in git — see Quick start)
```

---

## Quick start

```bash
# Clone the repo
git clone https://github.com/zltastopa/zmluvy.git
cd zmluvy

# Configure local defaults
cp .env.example .env

# Download a CRZ daily export
curl -o data.zip https://www.crz.gov.sk/export/2026-03-05.zip
unzip data.zip

# Parse into SQLite
uv run python pipeline/load_crz.py 2026-03-05.xml

# Start the server (dashboard + datasette on one port)
uv run python server/serve.py
# → http://localhost:8001
```

### Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **pdftotext** (optional, for PDF extraction pipeline)

---

## Deploy with Docker Compose

```bash
docker compose up -d --build
```

The app listens on `127.0.0.1:8001` inside the container (published as `127.0.0.1:8321` on the host), ready for nginx to reverse-proxy.

The Compose setup mounts `crz.db` from the host instead of baking it into the image, keeping deploys fast even with a ~1 GB database.

<details>
<summary>Useful commands</summary>

```bash
docker compose logs -f
docker compose ps
docker compose restart
docker compose pull
```
</details>

---

## Configuration

Environment is loaded from `.env` by all entrypoints. CLI flags override `.env` values.

| Variable | Purpose | Default |
|----------|---------|---------|
| `CRZ_DB_PATH` | SQLite database path | `crz.db` |
| `CRZ_PDF_DIR` | Downloaded PDFs | `data/pdfs` |
| `CRZ_TEXT_DIR` | Extracted text | `data/texts` |
| `CRZ_EXTRACTIONS_DIR` | LLM extractions | `data/extractions` |
| `OPENROUTER_API_KEY` | API key for LLM extraction | — |
| `OPENROUTER_MODEL` | Model for extraction | `google/gemini-2.5-flash-lite` |
| `CRZ_DOWNLOAD_MONTH` | Default download month | `2026-03` |
| `CRZ_DOWNLOAD_LIMIT` | Max contracts to download | `50000` |
| `PDFTOTEXT_BIN` | Path to `pdftotext` binary | `pdftotext` |

---

## Ingestion pipeline (Delta Lake)

A single script handles the full ingestion workflow — from downloading CRZ daily exports to flagging contracts. Data is stored as Delta Lake tables (Parquet + transaction log) in `delta_store/tables/`.

```bash
# Full pipeline for a single day
uv run python delta_store/ingest.py --date 2026-03-18

# Full pipeline for a date range
uv run python delta_store/ingest.py --from 2026-03-01 --to 2026-03-18

# Run a single step
uv run python delta_store/ingest.py --date 2026-03-18 --step extract --limit 100
```

### Pipeline steps

| Step | Name | What it does | Source → Target |
|------|------|-------------|-----------------|
| 1 | `download` | Fetches daily ZIP exports, extracts XML | `crz.gov.sk/export/YYYY-MM-DD.zip` → `data/xml/` |
| 2 | `parse` | Parses XML, upserts contracts and attachments | XML → Delta `zmluvy`, `prilohy`, `rezorty` |
| 3 | `pdf` | Downloads PDF attachments for new contracts | `crz.gov.sk/data/att/` → `data/pdfs/` |
| 4 | `text` | Converts PDFs to plain text via `pdftotext` | `data/pdfs/` → `data/texts/` |
| 5 | `extract` | Sends text/PDF to LLM, extracts structured fields | OpenRouter API → Delta `extractions` + `data/extractions/` |
| 6 | `flag` | Evaluates flag rules against new contracts | Delta tables → Delta `red_flags` |

### How it works

- **Idempotent** — every step skips already-processed items. Safe to re-run or resume after Ctrl+C.
- **Delta Lake merge** — steps 2, 5, and 6 use Delta Lake's merge API (match → update, no match → insert) instead of append-only writes.
- **DuckDB queries** — steps 3–6 query Delta tables via `delta_scan()` to discover which PDFs to download, which contracts need extraction, etc.
- **Parallel** — PDF download, text conversion, and LLM extraction run with `--workers N` (default: 8). All steps show a tqdm progress bar.

### CLI options

| Flag | Purpose | Default |
|------|---------|---------|
| `--date YYYY-MM-DD` | Single date | today |
| `--from / --to` | Date range (YYYY-MM-DD or YYYY-MM) | — |
| `--step NAME` | Run only one step | all steps |
| `--workers N` | Parallel workers | 8 |
| `--limit N` | Max items per step | 0 (unlimited) |
| `--model MODEL` | LLM model for extraction | `google/gemini-2.5-flash-lite` |
| `--force` | Re-process existing outputs | false |

### Extracted fields

Service category, actual subject, hidden entities (with subcontractor percentages), penalties, penalty asymmetry, signatories, duration, funding source, bank accounts, and more. Results go into `data/extractions/` as JSON sidecars and the Delta `extractions` table.

### Legacy pipeline (SQLite)

The original per-step scripts in `pipeline/` still work for the SQLite-based workflow:

```bash
uv run python pipeline/load_crz.py data/*.xml           # parse XML → SQLite
uv run python pipeline/download_sample_pdfs.py --all     # download PDFs
uv run python pipeline/pdf_to_text.py                    # PDF → text
uv run python pipeline/extract_contracts.py              # LLM extraction → SQLite
```

---

## Tax reliability data

Cross-reference contracts against the Financial Administration's [Tax Reliability Index](https://www.financnasprava.sk/sk/elektronicke-sluzby/verejne-sluzby/zoznamy/detail/_5cd6a827-0ee0-4028-8982-4d8bb1de3008).

```bash
curl -o ds_iz_ran.zip https://report.financnasprava.sk/ds_iz_ran.zip
unzip ds_iz_ran.zip
uv run python pipeline/load_tax_reliability.py
```

This creates a `tax_reliability` table (~680K subjects) joinable on ICO:

```sql
SELECT z.nazov_zmluvy, z.dodavatel, z.suma, t.status
FROM zmluvy z
JOIN tax_reliability t ON z.dodavatel_ico = t.ico
WHERE t.status = 'menej spoľahlivý'
ORDER BY z.suma DESC
```

---

## Data sources

| Source | Description | License |
|--------|-------------|---------|
| **[CRZ](https://www.crz.gov.sk/)** | Daily XML exports from the Office of the Government of the Slovak Republic | Public by law ([Act No. 211/2000 Coll.](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2000/211/)) |
| **[Tax reliability](https://report.financnasprava.sk/)** | `ds_iz_ran.xml` from Finančná správa SR, updated daily | CC0 |

---

## Contributing

Found a bug or have an idea? [Open an issue](https://github.com/zltastopa/zmluvy/issues/new) or submit a pull request. All contributions are welcome.

## License

[MIT](LICENSE) — made with care by [Žltá stopa](https://github.com/zltastopa).
