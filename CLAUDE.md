# CLAUDE.md

Read `AGENTS.md` first — it contains the database schema, flag rules,
investigation queries, and output conventions.

## Claude Code specifics

- **Default data source:** FastAPI + DuckDB at `https://zmluvy.zltastopa.sk` — supports arbitrary SQL.
  Query via `curl` or `WebFetch` with `/data/crz.json?sql=...&_shape=array`.
  **DuckDB syntax** — use `strftime(TRY_CAST(col AS DATE), fmt)`, `DATE_DIFF`, `string_agg`, `TRY_CAST`.
- Use `Read` tool for files, `Bash` for SQL and git commands.

## Project skills

Located in `skills/` directory. Two orchestrators compose the reusable building blocks.

### Orchestrators
- **crz-investigate** — broad scan of a time period: sql-analytics → critical-validation → finstat-enrichment → uvo-procurement → rpvs-lookup → foaf-network
- **crz-deep-investigate** — deep dive into one company/ICO: target mapping → hidden entities → rpvs-lookup → foaf-network → uvo-procurement → timeline

### Building blocks
- **sql-analytics** — 20 standard investigative SQL queries (DuckDB syntax)
- **critical-validation** — validate findings against data artifacts and innocent explanations
- **finstat-enrichment** — enrich suppliers with FinStat financial data
- **uvo-procurement** — UVO public procurement lookup (bid counts, competitors, evaluation)
- **rpvs-lookup** — RPVS beneficial ownership lookup via Playwright
- **foaf-network** — foaf.sk corporate network mapping via Playwright

## Local setup

Data files (`delta_store/tables/`) are **not in the repo** — they're stored
in Cloudflare R2 and downloaded on demand. After cloning:

```bash
uv sync                                           # install deps
uv run python -m delta_store.r2_sync download      # download ~133 MB from R2 (no credentials needed)
uv run python delta_store/serve.py                 # starts server (auto-downloads if tables missing)
```

`serve.py` auto-downloads from R2 on startup if tables are missing, so the
explicit download step is optional — but avoids surprises when running tests
or other scripts that expect the tables to exist.

## Things 3 Integration

Project: **zltastopa** (Area: AI)
