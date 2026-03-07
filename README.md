# CRZ Explorer

Intelligent search across Slovak government contracts from the [Central Register of Contracts](https://www.crz.gov.sk/) (CRZ).

## Try it now

**[Open CRZ Explorer in your browser](https://lite.datasette.io/?url=https://github.com/mrshu/crz-experiments/blob/main/crz.db)**

No installation needed — runs entirely in your browser via WebAssembly.

### What you can do

- **Full-text search** across contract titles, supplier names, buyer names, and notes
- **Filter** by amount, date, contract type, status
- **Sort** by any column
- **Export** to CSV or JSON
- **Write SQL** queries directly

### Example searches

| Search for | What it finds |
|-----------|--------------|
| `advokát` | Legal services (found in supplier name, not just contract title) |
| `COLAS` | Construction contracts by COLAS Slovakia |
| `poroty` | Jury/panel contracts (hidden in notes field) |
| `marketing` | Marketing and advertising contracts |
| `dielo` | All "Zmluva o dielo" contracts |

## Why this exists

CRZ.gov.sk only searches contract titles (`predmet`). But the actual service type is often hidden in the **supplier name** or **notes** field. This tool searches across ALL fields simultaneously.

For example: a legal services contract where the title just says "Zmluva o dielo" but the supplier is "Advokátska kancelária XY" — CRZ can't find it, but this tool can.

## Build locally

```bash
# Configure local defaults
cp .env.example .env

# Download CRZ daily exports
curl -o data.zip https://www.crz.gov.sk/export/2026-03-05.zip
unzip data.zip

# Parse into SQLite
uv run python load_crz.py 2026-03-05.xml

# Browse
uv run datasette crz.db
```

Environment is loaded automatically from `.env` by all Python
entrypoints. The main variables are:

- `CRZ_DB_PATH` for the SQLite database path
- `CRZ_PDF_DIR`, `CRZ_TEXT_DIR`, `CRZ_EXTRACTIONS_DIR` for pipeline
  directories
- `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`,
  `OPENROUTER_BASE_URL` for extraction
- `CRZ_DOWNLOAD_MONTH`, `CRZ_DOWNLOAD_LIMIT` for downloader defaults
- `PDFTOTEXT_BIN` if `pdftotext` is not on your default `PATH`

CLI flags still override `.env` values on a per-run basis.

## Update with more data

```bash
# Download a range of daily exports
for i in $(seq 0 30); do
  date=$(date -v-${i}d +%Y-%m-%d)
  curl -s -o "data/${date}.zip" "https://www.crz.gov.sk/export/${date}.zip"
done

# Unzip and load all
for f in data/*.zip; do unzip -o "$f" -d data/; done
uv run python load_crz.py data/*.xml
```

## Data source

- Daily XML exports from `https://www.crz.gov.sk/export/YYYY-MM-DD.zip`
- Published nightly by the Office of the Government of the Slovak Republic
- All data is public by law (Act No. 211/2000 Coll.)
