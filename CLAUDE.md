# CLAUDE.md

Read `AGENTS.md` first — it contains the database schema, flag rules,
investigation queries, and output conventions.

## Claude Code specifics

- **Default data source:** Datasette at `https://zmluvy.zltastopa.sk/data/crz` — supports arbitrary SQL.
  Query via `curl` or `WebFetch` with `.json?sql=...&_shape=array`. Use local `crz.db` only as fallback.
- Use `Read` tool for files, `Bash` for SQL and git commands.

## Project skills

Located in `skills/` directory. Two orchestrators compose the reusable building blocks.

### Orchestrators
- **crz-investigate** — broad scan of a time period: sql-analytics → critical-validation → finstat-enrichment → uvo-procurement → rpvs-lookup → foaf-network
- **crz-deep-investigate** — deep dive into one company/ICO: target mapping → hidden entities → rpvs-lookup → foaf-network → uvo-procurement → timeline

### Building blocks
- **sql-analytics** — 17 standard investigative SQL queries
- **critical-validation** — validate findings against data artifacts and innocent explanations
- **finstat-enrichment** — enrich suppliers with FinStat financial data
- **uvo-procurement** — UVO public procurement lookup (bid counts, competitors, evaluation)
- **rpvs-lookup** — RPVS beneficial ownership lookup via Playwright
- **foaf-network** — foaf.sk corporate network mapping via Playwright

## Things 3 Integration

Project: **zltastopa** (Area: AI)
