---
name: finstat-enrichment
description: Enrich CRZ contract suppliers with financial data from FinStat.sk — revenue, profit, equity, tax reliability, founding date — and evaluate financial zlte stopy. Use this skill whenever you need to check a supplier's financial health, when critical-validation marks a finding as CONFIRMED or INCONCLUSIVE and recommends FinStat enrichment, when the crz-investigate orchestrator enters the enrichment phase, or when the user asks about a company's financials, revenue, equity, or tax status. Two modes — batch pipeline for many suppliers, manual curl for 1-5 specific companies.
---

# FinStat Supplier Financial Enrichment

Enrich CRZ suppliers with financial data from FinStat.sk and flag financial
zlte stopy. This is the "follow the money" step — after sql-analytics finds
anomalies and critical-validation confirms them, finstat-enrichment checks
whether the supplier is financially healthy enough to deliver.

## Input

| Field | Description | Example |
|-------|-------------|---------|
| `mode` | `batch` or `manual` | manual |
| `icos` | List of ICOs to enrich | 51671824, 44965257 |
| `date_from` | Period start (for batch) | 2026-01-01 |
| `date_to` | Period end (for batch) | 2026-02-01 |
| `context` | Why these suppliers matter | CONFIRMED double debtor from critical-validation |

If the user provides specific ICOs (1-5 companies), use **manual mode**.
If they ask to enrich "all suppliers" or "top suppliers" for a period, use
**batch mode**.

## Mode 1: Manual lookup (1-5 companies)

Fetch all companies **in parallel** — launch all curl/WebFetch calls in the
same turn since they're independent. Use `curl` (not Playwright) for speed.

```bash
curl -s "https://finstat.sk/{ico}" -H "User-Agent: Mozilla/5.0"
```

**Where to find data on the page** (saves you exploratory calls):

| Data point | Location in HTML |
|---|---|
| Company name | `<title>{name} - zisk, tržby...</title>` |
| Trzby, Zisk, Aktiva | `og:description` meta tag: `"Zisk: X, Tržby: Y, Aktíva: Z"` |
| Vlastny kapital | Text near "Vlastný kapitál" followed by `>NNN EUR` |
| Datum vzniku | Text near "Dátum vzniku" in a `<span>` |
| Celkova zadlzenost | Text near "Celková zadlženosť" followed by `N,N %` |

Also check the local database registers for all ICOs in one query:

```sql
SELECT 'vszp' as register, ico, dlh as value FROM vszp_debtors WHERE ico IN ('{ico1}','{ico2}')
UNION ALL SELECT 'socpoist', ico, dlh FROM socpoist_debtors WHERE ico IN ('{ico1}','{ico2}')
UNION ALL SELECT 'fs', ico, dlh FROM fs_tax_debtors WHERE ico IN ('{ico1}','{ico2}')
UNION ALL SELECT 'ruz', ico, CAST(vlastne_imanie AS TEXT) FROM ruz_equity WHERE ico IN ('{ico1}','{ico2}')
UNION ALL SELECT 'tax_rel', ico, status FROM tax_reliability WHERE ico IN ('{ico1}','{ico2}')
```

**Skip state institutions** — ministries, universities, state funds won't
have finstat.sk profiles. Focus enrichment on private suppliers (s.r.o., a.s.).

## Mode 2: Batch pipeline (many suppliers)

Run the enrichment pipeline:

```bash
# Top suppliers for a month
uv run python pipeline/enrich_suppliers.py --month 2026-01 --limit 100

# Date range
uv run python pipeline/enrich_suppliers.py --from 2026-01 --to 2026-03 --limit 200

# Single company via pipeline
uv run python pipeline/enrich_suppliers.py --ico 51671824

# Re-evaluate flags only (no scraping)
uv run python pipeline/enrich_suppliers.py --flags-only --month 2026-01
```

Results are stored in `supplier_financials` and `supplier_red_flags` tables.

Query results after pipeline run:

```sql
-- Top flagged suppliers
SELECT sf.ico, sf.nazov, sf.trzby, sf.zisk, sf.vlastny_kapital,
       count(DISTINCT srf.flag_type) as flag_types,
       group_concat(DISTINCT srf.flag_type) as flags
FROM supplier_red_flags srf
JOIN supplier_financials sf ON srf.ico = sf.ico
GROUP BY srf.ico
ORDER BY count(DISTINCT srf.flag_type) DESC LIMIT 20;
```

## Zlte stopy rules

Evaluate these 7 rules for each supplier. Apply them whether using manual
or batch mode:

| Zlta stopa | Severity | Condition | What it means |
|---|---|---|---|
| `contract_exceeds_2x_revenue` | DANGER | Contract > 2x annual revenue | Firm too small for this contract |
| `negative_equity` | DANGER | Vlastne imanie < 0 | Firm is technically insolvent |
| `severe_loss` | DANGER | Loss > 30% of revenue | Firm bleeding money |
| `tax_unreliable` | DANGER | Tax reliability: menej spolahlivy | Tax authority considers them unreliable |
| `missing_rpvs` | WARNING | Not in RPVS, contract > 100K | Should be registered as public sector partner |
| `unusually_high_profit` | WARNING | Profit > 50% of revenue | Unusual margin, possible shell company |
| `young_company` | WARNING | Contract < 1 year after founding | New firm winning big contracts |

**Framework contract adjustment:** For ramcove zmluvy (framework agreements)
with multi-year duration, divide the total contract value by the number of
years before comparing to annual revenue. A 7-year framework for 145M EUR
is ~21M/year — compare that to revenue, not the full 145M.

## Risk assessment rubric

Use this rubric for the Hodnotenie section — it standardizes the assessment
across suppliers:

| Signal | Risk level | Interpretation |
|---|---|---|
| Contract < 1x revenue, positive equity | **LOW** | Firm can handle it from normal operations |
| Contract 1-3x revenue, positive equity | **MEDIUM** | Stretched but feasible, may need financing |
| Contract > 3x revenue OR negative equity | **HIGH** | Serious capacity concern |
| Contract > 5x revenue AND negative equity | **CRITICAL** | Very unlikely to deliver without external help |

For multi-year contracts, use the annualized value in this comparison.

## Output template

```markdown
# FinStat enrichment: {context}

## Sumar
- Pocet dodavatelov: {N}
- Financne zlte stopy: {X} DANGER, {Y} WARNING
- Najkritickejsi dodavatel: {name} ({reasons})

---

## Dodavatel 1: {company_name} (ICO {ico})

| Ukazovatel | Hodnota |
|---|---|
| Trzby (revenue) | {trzby} EUR |
| Zisk (profit) | {zisk} EUR |
| Vlastny kapital (equity) | {vlastny_kapital} EUR |
| Celkova zadlzenost | {zadlzenost}% |
| Datum vzniku | {datum} |
| Danova spolahlivost | {tax_status} |

### Zmluvy v CRZ
| ID | Suma | Nazov zmluvy |
|---|---|---|
| {id} | {suma} EUR | {nazov} |

### Financne zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| {flag_type} | {severity} | {detail} |

### Hodnotenie
**Riziko: {LOW/MEDIUM/HIGH/CRITICAL}** — {1-2 sentence assessment}

---

[...repeat for each supplier...]

---

**Enrichment ukonceny.** {summary of most concerning findings}
```
