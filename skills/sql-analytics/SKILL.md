---
name: sql-analytics
description: Run 17 standard investigative SQL queries against CRZ contract data to surface anomalies — top suppliers, contract splitting, threshold gaming, weekend publishing, late publication, debtors, hidden entities, and more. Use when asked to scan contracts for a time period or find suspicious patterns in CRZ data.
---

# CRZ SQL Analytics

Run targeted SQL queries against CRZ contract data to identify anomalies
and suspicious patterns across a time period.

## Data source

**Primary:** Datasette at `https://zmluvy.zltastopa.sk/data/crz` — query via:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+...&_shape=array
```

**Local fallback:** `sqlite3 -header -column crz.db "..."` when Datasette is
unreachable. Full schema: **[docs/data/](docs/data/README.md)**

## Input

A **date range** to filter contracts:
```sql
WHERE datum_zverejnenia >= '{from_date}' AND datum_zverejnenia < '{to_date}'
```

## Queries

### Money flow

**1. Top suppliers by total value** — who gets the most money?
```sql
SELECT dodavatel, dodavatel_ico, count(*) as pocet,
       printf('%.2f', sum(suma)) as celkom
FROM zmluvy WHERE {date_filter}
GROUP BY dodavatel_ico ORDER BY sum(suma) DESC LIMIT 30
```

**2. Buyer-supplier concentration** — is any buyer captured by a single supplier?
```sql
SELECT objednavatel, dodavatel, count(*) as pocet,
       printf('%.2f', sum(suma)) as celkom
FROM zmluvy WHERE {date_filter}
GROUP BY objednavatel_ico, dodavatel_ico
HAVING sum(suma) > 1000000 ORDER BY sum(suma) DESC
```

**3. Service category breakdown** — where does the money flow?
```sql
SELECT e.service_category, count(*) as pocet,
       printf('%.2f', sum(z.suma)) as celkom
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE {date_filter}
GROUP BY e.service_category ORDER BY sum(z.suma) DESC
```

### Procurement manipulation

**4. Contract splitting** — same pair, many small contracts below thresholds
```sql
-- IMPORTANT: GROUP BY dodavatel name+ico to avoid merging NULL-ICO suppliers
SELECT dodavatel, dodavatel_ico, objednavatel, objednavatel_ico,
       count(*) as pocet, printf('%.2f', max(suma)) as max_suma,
       printf('%.2f', sum(suma)) as celkom
FROM zmluvy WHERE {date_filter}
GROUP BY COALESCE(dodavatel_ico, dodavatel), objednavatel_ico
HAVING count(*) >= 5 AND max(suma) < 50000
ORDER BY sum(suma) DESC
```

**5. Threshold gaming** — clustering just below EU procurement threshold (215K)
```sql
SELECT CASE
  WHEN suma BETWEEN 210000 AND 214999 THEN 'just-below'
  WHEN suma BETWEEN 215000 AND 220000 THEN 'just-above'
END as band, count(*) as pocet, printf('%.2f', sum(suma)) as celkom
FROM zmluvy WHERE {date_filter}
  AND suma BETWEEN 210000 AND 220000
GROUP BY band
```

**6. Round amounts** — suspiciously exact numbers (multiples of 100K)
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_zverejnenia
FROM zmluvy WHERE {date_filter}
  AND suma >= 100000 AND suma = cast(suma/100000 as int) * 100000
ORDER BY suma DESC
```

### Timing anomalies

**7. Weekend publishing** — contracts buried on Saturdays/Sundays
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_zverejnenia, strftime('%w', datum_zverejnenia) as day_of_week
FROM zmluvy WHERE {date_filter}
  AND cast(strftime('%w', datum_zverejnenia) as int) IN (0, 6)
  AND suma > 100000
ORDER BY suma DESC
```

**8. Late publication** — signed months before being published
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_podpisu, datum_zverejnenia,
       cast(julianday(datum_zverejnenia) - julianday(datum_podpisu) as int) as days_late
FROM zmluvy WHERE {date_filter}
  AND julianday(datum_zverejnenia) - julianday(datum_podpisu) > 90
  AND suma > 100000
ORDER BY days_late DESC
```

### Phantom suppliers

**9. Suppliers without ICO** — unnamed entities receiving money
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_zverejnenia
FROM zmluvy WHERE {date_filter}
  AND (dodavatel_ico IS NULL OR dodavatel_ico = '')
  AND suma > 100000
ORDER BY suma DESC
```

**10. 'Neuvedene' suppliers** — contracts to literally "not specified"
```sql
SELECT id, nazov_zmluvy, printf('%.2f', suma) as suma, objednavatel
FROM zmluvy WHERE {date_filter}
  AND dodavatel = 'Neuvedene' AND suma > 10000
ORDER BY suma DESC
```

**11. Supplier groups (konzorcia)** — who hides behind "Skupina dodavatelov"
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma
FROM zmluvy WHERE {date_filter}
  AND dodavatel LIKE '%skupina%dodavatelov%'
ORDER BY suma DESC
```

### Extraction-based (requires `extractions` table)

**12. Supplier advantage penalties** — buyer bears more risk
```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, printf('%.2f', z.suma) as suma
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE e.penalty_asymmetry = 'supplier_advantage' AND {date_filter}
ORDER BY z.suma DESC
```

**13. Bezodplatne (free) contracts** — what's being given away?
```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.objednavatel,
       printf('%.2f', z.suma) as suma
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE e.bezodplatne = 1 AND {date_filter}
ORDER BY z.suma DESC
```

**14. Hidden entities** — third parties lurking in contracts
```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, printf('%.2f', z.suma) as suma,
       e.hidden_entity_count
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE e.hidden_entity_count >= 3 AND {date_filter}
ORDER BY e.hidden_entity_count DESC
```

### Debtor cross-checks

**15. VSZP debtors with government contracts**
```sql
SELECT z.dodavatel, replace(z.dodavatel_ico, ' ', '') as ico,
       count(*) as pocet_zmluv,
       printf('%.2f', sum(z.suma)) as celkom_zmluvy,
       printf('%.2f', v.amount) as dlh_vszp
FROM zmluvy z
JOIN vszp_debtors v ON v.cin = replace(z.dodavatel_ico, ' ', '')
WHERE z.suma > 0 AND {date_filter}
GROUP BY z.dodavatel_ico ORDER BY v.amount DESC LIMIT 30
```

**16. Socialna poistovna debtors with government contracts**
```sql
SELECT z.dodavatel, z.dodavatel_ico,
       count(*) as pocet_zmluv,
       printf('%.2f', sum(z.suma)) as celkom_zmluvy,
       rf.detail as dlh_socpoist
FROM zmluvy z
JOIN red_flags rf ON rf.zmluva_id = z.id AND rf.flag_type = 'socpoist_debtor'
WHERE z.suma > 0 AND {date_filter}
GROUP BY z.dodavatel_ico ORDER BY sum(z.suma) DESC LIMIT 30
```

**17. Double debtors** — owe BOTH health and social insurance
```sql
SELECT z.dodavatel, replace(z.dodavatel_ico, ' ', '') as ico,
       printf('%.2f', sum(z.suma)) as celkom_zmluvy,
       printf('%.2f', v.amount) as dlh_vszp
FROM zmluvy z
JOIN vszp_debtors v ON v.cin = replace(z.dodavatel_ico, ' ', '')
WHERE z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = 'socpoist_debtor')
  AND {date_filter}
GROUP BY z.dodavatel_ico ORDER BY v.amount DESC
```

## Output

For each query that returns results, report:
- Query name and what it found
- Result table (markdown)
- Brief interpretation of what stands out

**Do NOT draw conclusions yet** — findings need validation via the
**critical-validation** skill before reporting.
