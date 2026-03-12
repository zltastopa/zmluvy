---
name: finstat-enrichment
description: Enrich CRZ contract suppliers with financial data from FinStat.sk and evaluate financial zlte stopy (revenue mismatch, negative equity, tax unreliability, young company). Use when you need to check a supplier's financials or batch-enrich suppliers for a time period.
---

# FinStat Supplier Financial Enrichment

Enrich CRZ contract suppliers with financial data from FinStat.sk and
evaluate financial zlte stopy.

## Data source

**FinStat.sk:** `https://finstat.sk/{ico}` — revenue, profit, equity,
employees, tax reliability, founding date.

Results are stored in `supplier_financials` and `supplier_red_flags` tables
in the local database.

## CLI commands

```bash
# Enrich top 100 suppliers for a month
uv run python pipeline/enrich_suppliers.py --month 2026-01 --limit 100

# Enrich specific company
uv run python pipeline/enrich_suppliers.py --ico 51671824

# Date range
uv run python pipeline/enrich_suppliers.py --from 2026-01 --to 2026-03 --limit 200

# Re-evaluate flags only (no scraping)
uv run python pipeline/enrich_suppliers.py --flags-only --month 2026-01
```

## Zlte stopy evaluated

| Zlta stopa | Severity | Condition |
|---|---|---|
| `contract_exceeds_2x_revenue` | danger | Contract value > 2x annual revenue |
| `negative_equity` | danger | Negative equity (vlastne imanie < 0) |
| `unusually_high_profit` | warning | Profit > 0.5x revenue |
| `severe_loss` | danger | Loss exceeds 30% of revenue |
| `missing_rpvs` | warning | Not in RPVS despite contract > 100K |
| `tax_unreliable` | danger | Tax reliability: menej spolahlivy |
| `young_company` | warning | Contract signed < 1 year after founding |

## Querying results

```sql
-- Contracts flagged with financial zlte stopy
SELECT srf.flag_type, srf.severity, srf.detail,
       z.nazov_zmluvy, z.dodavatel, printf('%.2f', z.suma) as suma
FROM supplier_red_flags srf
JOIN zmluvy z ON srf.zmluva_id = z.id
ORDER BY z.suma DESC;

-- Suppliers with most flag types
SELECT sf.nazov, srf.ico, count(DISTINCT srf.flag_type) as flag_types,
       sf.trzby, sf.zisk, sf.vlastny_kapital
FROM supplier_red_flags srf
JOIN supplier_financials sf ON srf.ico = sf.ico
GROUP BY srf.ico ORDER BY flag_types DESC LIMIT 20;
```

## Output

For each enriched supplier, report:
- Company name, ICO, key financials (revenue, profit, equity)
- Tax reliability status
- Which zlte stopy triggered and why
- Contract value vs revenue ratio
