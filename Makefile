.DEFAULT_GOAL := help

# ─── Server ───────────────────────────────────────────────────
serve:  ## Start the web server (dashboard + datasette) on port 8001
	uv run python server/serve.py

serve-public:  ## Start the web server on 0.0.0.0:8001 (accessible from network)
	uv run python server/serve.py --host 0.0.0.0

# ─── Pipeline ─────────────────────────────────────────────────
flags:  ## Evaluate all zlta stopa rules
	uv run python server/run.py flags

flags-list:  ## List all rules and their hit counts
	uv run python server/run.py flags --list

extract:  ## Run LLM extraction on unprocessed contracts
	uv run python server/run.py extract

enrich:  ## Scrape FinStat financial data for top suppliers
	uv run python server/run.py enrich

pdf2text:  ## Convert downloaded PDFs to text
	uv run python server/run.py pdf2text

# ─── Data imports ─────────────────────────────────────────────
import-fs:  ## Import Financna sprava XML exports (tax debtors, VAT, corporate tax)
	uv run python pipeline/import_fs_exports.py

import-equity:  ## Fetch equity data from RegisterUZ API (slow, ~4 req/s)
	uv run python pipeline/import_ruz_equity.py

import-equity-500:  ## Fetch equity for up to 500 new suppliers
	uv run python pipeline/import_ruz_equity.py --limit 500

import-debtors:  ## Import VSZP, SocPoist, RUZ entity registers
	uv run python pipeline/import_debtors.py

# ─── Utilities ────────────────────────────────────────────────
download:  ## Download PDFs for current month (limit 200)
	uv run python pipeline/download_sample_pdfs.py --limit 200

db-counts:  ## Show row counts for key tables
	@sqlite3 crz.db "SELECT 'zmluvy: ' || count(*) FROM zmluvy; SELECT 'extractions: ' || count(*) FROM extractions; SELECT 'red_flags: ' || count(*) FROM red_flags; SELECT 'ruz_equity: ' || count(*) FROM ruz_equity; SELECT 'fs_tax_debtors: ' || count(*) FROM fs_tax_debtors;"

db-check:  ## Run SQLite integrity check
	@sqlite3 crz.db "PRAGMA integrity_check;" | head -1

# ─── Help ─────────────────────────────────────────────────────
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: serve serve-public flags flags-list extract enrich pdf2text import-fs import-equity import-equity-500 import-debtors download db-counts db-check help
