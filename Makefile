.DEFAULT_GOAL := help

# ─── Server ───────────────────────────────────────────────────
serve:  ## Start the web server on port 8002
	uv run python delta_store/serve.py

serve-public:  ## Start the web server on 0.0.0.0:8002 (accessible from network)
	uv run python delta_store/serve.py --host 0.0.0.0

# ─── Pipeline ─────────────────────────────────────────────────
ingest:  ## Run full ingestion pipeline for today
	uv run python delta_store/ingest.py

ingest-range:  ## Run ingestion for a date range (usage: make ingest-range FROM=2026-03-19 TO=2026-04-09)
	uv run python delta_store/ingest.py --from $(FROM) --to $(TO)

# ─── R2 sync ─────────────────────────────────────────────────
r2-download:  ## Download Delta tables from R2
	uv run python -m delta_store.r2_sync download

r2-upload:  ## Upload Delta tables to R2
	uv run python -m delta_store.r2_sync upload

# ─── Help ─────────────────────────────────────────────────────
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: serve serve-public ingest ingest-range r2-download r2-upload help
