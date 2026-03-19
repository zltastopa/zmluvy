---
name: sql-analytics
description: Run 20 standard investigative SQL queries against CRZ Slovak government contract data to surface anomalies — top suppliers, contract splitting, threshold gaming, weekend publishing, late publication, debtors, hidden entities, negative equity, dormant firms, and daily volume spikes. Use this skill whenever the user asks to scan, analyze, audit, or investigate CRZ contracts for a time period, find suspicious patterns, run analytics on zmluvy, or identify zlte stopy in government spending. Also trigger when the user provides a date range and wants to know what's fishy, even if they don't say "sql-analytics" explicitly.
---

# CRZ SQL Analytics

Run targeted SQL queries against CRZ contract data to identify anomalies
and suspicious patterns across a time period.

## When to use this skill

- User asks to "scan contracts for January 2026"
- User asks to "find suspicious patterns in Q4"
- User wants an overview of anomalies for a date range
- The crz-investigate orchestrator calls this as Phase 1

## Input

Two required parameters:

| Parameter | Format | Example |
|-----------|--------|---------|
| `date_from` | `YYYY-MM-DD` | `2026-01-01` |
| `date_to` | `YYYY-MM-DD` | `2026-02-01` |

These map to the date filter used in every query:
```sql
WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
```

If the user says "January 2026", interpret as `date_from=2026-01-01`, `date_to=2026-02-01`.
If they say "Q1 2026", use `2026-01-01` to `2026-04-01`.

## Data source

**Primary:** FastAPI + DuckDB at `https://zmluvy.zltastopa.sk` — query via:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+...&_shape=array
```

**Important:** The backend uses DuckDB, not SQLite. Key syntax differences:
- `strftime(TRY_CAST(col AS DATE), '%w')` — date first, format second
- `DATE_DIFF('day', start, end)` instead of `julianday(a) - julianday(b)`
- `string_agg(col, ',')` instead of `group_concat(col)`
- `TRY_CAST(x AS DATE) - INTERVAL N DAY` instead of `date(x, '-N days')`
- `any_value(col)` required for non-aggregated columns not in GROUP BY

Full schema: **[docs/data/](docs/data/README.md)**

## Execution strategy

Run queries in batches where possible to reduce round-trips:
- **Batch 1** (independent, run in parallel): Queries 1-3 (money flow) + 5-6 (threshold/round)
- **Batch 2** (independent, run in parallel): Queries 4 (splitting) + 7-8 (timing) + 9-11 (phantom)
- **Batch 3** (independent, run in parallel): Queries 12-14 (extractions) + 15-17 (debtors)
- **Batch 4** (independent, run in parallel): Queries 18-20 (bonus: equity, dormant, daily volume)

This reduces total execution time. If any query fails or times out, continue
with the remaining queries — partial results are still valuable.

## Queries

Run all 20 queries below. Skip a query only if it returns zero rows.
Group results by category in the output.

### Category 1: Money flow

**1. Top suppliers by total value** — who gets the most money?
```sql
SELECT any_value(dodavatel) as dodavatel, dodavatel_ico, count(*) as pocet,
       printf('%.2f', sum(suma)) as celkom
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
GROUP BY dodavatel_ico ORDER BY sum(suma) DESC LIMIT 30
```

**2. Buyer-supplier concentration** — is any buyer captured by a single supplier?
```sql
SELECT any_value(objednavatel) as objednavatel, any_value(dodavatel) as dodavatel,
       count(*) as pocet, printf('%.2f', sum(suma)) as celkom
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
GROUP BY objednavatel_ico, dodavatel_ico
HAVING sum(suma) > 1000000 ORDER BY sum(suma) DESC
```

**3. Service category breakdown** — where does the money flow?
```sql
SELECT e.service_category, count(*) as pocet,
       printf('%.2f', sum(z.suma)) as celkom
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
GROUP BY e.service_category ORDER BY sum(z.suma) DESC
```

### Category 2: Procurement manipulation

**4. Contract splitting** — same pair, many small contracts below thresholds
```sql
-- IMPORTANT: GROUP BY dodavatel name+ico to avoid merging NULL-ICO suppliers
SELECT any_value(dodavatel) as dodavatel, any_value(dodavatel_ico) as dodavatel_ico,
       any_value(objednavatel) as objednavatel, objednavatel_ico,
       count(*) as pocet, printf('%.2f', max(suma)) as max_suma,
       printf('%.2f', sum(suma)) as celkom
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
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
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
  AND suma BETWEEN 210000 AND 220000
GROUP BY band
```

**6. Round amounts** — suspiciously exact numbers (multiples of 100K)
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_zverejnenia
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
  AND suma >= 100000 AND suma = cast(suma/100000 as int) * 100000
ORDER BY suma DESC
```

### Category 3: Timing anomalies

**7. Weekend publishing** — contracts buried on Saturdays/Sundays
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_zverejnenia,
       strftime(TRY_CAST(datum_zverejnenia AS DATE), '%w') as day_of_week
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
  AND CAST(strftime(TRY_CAST(datum_zverejnenia AS DATE), '%w') AS INTEGER) IN (0, 6)
  AND suma > 100000
ORDER BY suma DESC
```

**8. Late publication** — signed months before being published
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_podpisu, datum_zverejnenia,
       DATE_DIFF('day', TRY_CAST(datum_podpisu AS DATE), TRY_CAST(datum_zverejnenia AS DATE)) as days_late
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
  AND DATE_DIFF('day', TRY_CAST(datum_podpisu AS DATE), TRY_CAST(datum_zverejnenia AS DATE)) > 90
  AND suma > 100000
ORDER BY days_late DESC
```

### Category 4: Phantom suppliers

**9. Suppliers without ICO** — unnamed entities receiving money
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma,
       datum_zverejnenia
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
  AND (dodavatel_ico IS NULL OR dodavatel_ico = '')
  AND suma > 100000
ORDER BY suma DESC
```

**10. 'Neuvedene' suppliers** — contracts to literally "not specified"
```sql
SELECT id, nazov_zmluvy, printf('%.2f', suma) as suma, objednavatel
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
  AND dodavatel = 'Neuvedene' AND suma > 10000
ORDER BY suma DESC
```

**11. Supplier groups (konzorcia)** — who hides behind "Skupina dodavatelov"
```sql
SELECT id, nazov_zmluvy, dodavatel, printf('%.2f', suma) as suma
FROM zmluvy WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
  AND dodavatel LIKE '%skupina%dodavatelov%'
ORDER BY suma DESC
```

### Category 5: Extraction-based (requires `extractions` table)

**12. Supplier advantage penalties** — buyer bears more risk
```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, printf('%.2f', z.suma) as suma
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE e.penalty_asymmetry = 'supplier_advantage'
  AND z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
ORDER BY z.suma DESC
```

**13. Bezodplatne (free) contracts** — what's being given away?
```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.objednavatel,
       printf('%.2f', z.suma) as suma
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE e.bezodplatne = 1
  AND z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
ORDER BY z.suma DESC
```

**14. Hidden entities** — third parties lurking in contracts
```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, printf('%.2f', z.suma) as suma,
       e.hidden_entity_count
FROM extractions e JOIN zmluvy z ON e.zmluva_id = z.id
WHERE e.hidden_entity_count >= 3
  AND z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
ORDER BY e.hidden_entity_count DESC
```

### Category 6: Debtor cross-checks

**15. VSZP debtors with government contracts**
```sql
SELECT any_value(z.dodavatel) as dodavatel, replace(z.dodavatel_ico, ' ', '') as ico,
       count(*) as pocet_zmluv,
       printf('%.2f', sum(z.suma)) as celkom_zmluvy,
       printf('%.2f', any_value(v.amount)) as dlh_vszp
FROM zmluvy z
JOIN vszp_debtors v ON v.cin = replace(z.dodavatel_ico, ' ', '')
WHERE z.suma > 0
  AND z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
GROUP BY z.dodavatel_ico ORDER BY any_value(v.amount) DESC LIMIT 30
```

**16. Socialna poistovna debtors with government contracts**
```sql
SELECT any_value(z.dodavatel) as dodavatel, z.dodavatel_ico,
       count(*) as pocet_zmluv,
       printf('%.2f', sum(z.suma)) as celkom_zmluvy,
       any_value(rf.detail) as dlh_socpoist
FROM zmluvy z
JOIN red_flags rf ON rf.zmluva_id = z.id AND rf.flag_type = 'socpoist_debtor'
WHERE z.suma > 0
  AND z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
GROUP BY z.dodavatel_ico ORDER BY sum(z.suma) DESC LIMIT 30
```

**17. Double debtors** — owe BOTH health and social insurance
```sql
SELECT any_value(z.dodavatel) as dodavatel, replace(z.dodavatel_ico, ' ', '') as ico,
       printf('%.2f', sum(z.suma)) as celkom_zmluvy,
       printf('%.2f', any_value(v.amount)) as dlh_vszp
FROM zmluvy z
JOIN vszp_debtors v ON v.cin = replace(z.dodavatel_ico, ' ', '')
WHERE z.id IN (SELECT zmluva_id FROM red_flags WHERE flag_type = 'socpoist_debtor')
  AND z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
GROUP BY z.dodavatel_ico ORDER BY any_value(v.amount) DESC
```

### Category 7: Bonus cross-checks

These queries were added based on patterns that baseline analysis consistently
discovered — they catch findings the core 17 queries miss.

**18. Negative equity suppliers** — companies in technical bankruptcy receiving contracts
```sql
SELECT any_value(z.dodavatel) as dodavatel, replace(z.dodavatel_ico, ' ', '') as ico,
       count(*) as pocet_zmluv,
       printf('%.2f', sum(z.suma)) as celkom_zmluvy,
       printf('%.2f', any_value(re.vlastne_imanie)) as vlastne_imanie
FROM zmluvy z
JOIN ruz_equity re ON re.ico = replace(z.dodavatel_ico, ' ', '')
WHERE re.vlastne_imanie < 0
  AND z.suma > 50000
  AND z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
GROUP BY z.dodavatel_ico
ORDER BY sum(z.suma) DESC LIMIT 20
```

**19. Dormant-then-active suppliers** — companies with no contracts for 2+ years suddenly active
```sql
SELECT z.dodavatel, replace(z.dodavatel_ico, ' ', '') as ico,
       printf('%.2f', z.suma) as suma, z.nazov_zmluvy,
       z.datum_zverejnenia,
       (SELECT max(z2.datum_zverejnenia) FROM zmluvy z2
        WHERE replace(z2.dodavatel_ico, ' ', '') = replace(z.dodavatel_ico, ' ', '')
          AND z2.datum_zverejnenia < '{date_from}') as posledna_predtym
FROM zmluvy z
WHERE z.datum_zverejnenia >= '{date_from}' AND z.datum_zverejnenia < '{date_to}'
  AND z.suma > 50000
  AND replace(z.dodavatel_ico, ' ', '') != ''
  AND TRY_CAST((SELECT max(z2.datum_zverejnenia) FROM zmluvy z2
       WHERE replace(z2.dodavatel_ico, ' ', '') = replace(z.dodavatel_ico, ' ', '')
         AND z2.datum_zverejnenia < '{date_from}') AS DATE)
      < TRY_CAST('{date_from}' AS DATE) - INTERVAL 730 DAY
ORDER BY z.suma DESC LIMIT 15
```

**20. Daily volume distribution** — spot end-of-month rushes and anomalous spikes
```sql
SELECT datum_zverejnenia as den, count(*) as pocet,
       printf('%.2f', sum(suma)) as celkom,
       strftime(TRY_CAST(datum_zverejnenia AS DATE), '%w') as day_of_week
FROM zmluvy
WHERE datum_zverejnenia >= '{date_from}' AND datum_zverejnenia < '{date_to}'
GROUP BY datum_zverejnenia
ORDER BY sum(suma) DESC LIMIT 15
```

## Output template

Present results using this exact structure. Each category becomes a section.
Only include categories that produced results.

The key addition is the **Top 5 highlights** section right after Sumar — this
gives readers the most important leads immediately, before the full query-by-query
breakdown. Think of it as the "executive summary" of findings: what would a
journalist or auditor want to know first? Pick the 5 most suspicious, highest-value,
or most unusual findings from across all queries.

```markdown
# SQL Analytics: {date_from} -- {date_to}

## Sumar
- Pocet zmluv v obdobi: {N}
- Celkova suma: {X} EUR
- Pocet spustenych dopytov: 20
- Pocet dopytov s vysledkami: {M}

## Top 5 najdov

The 5 most notable findings across all queries, ranked by investigative value.
For each, state what was found, why it matters, and the key numbers.

1. **[Headline]** — [1 sentence: who, what, how much, why suspicious]
2. **[Headline]** — ...
3. **[Headline]** — ...
4. **[Headline]** — ...
5. **[Headline]** — ...

---

## 1. Toky penazi

### 1.1 Top dodavatelia podla celkovej sumy
| Dodavatel | ICO | Pocet | Celkom (EUR) |
|-----------|-----|-------|--------------|
| ...       | ... | ...   | ...          |

**Interpretacia:** [1-2 sentences on what stands out]

### 1.2 Koncentracia objednavatel-dodavatel
| Objednavatel | Dodavatel | Pocet | Celkom (EUR) |
|--------------|-----------|-------|--------------|

**Interpretacia:** ...

[...continue for each query with results...]

---

## 2. Manipulacia obstaravania
### 2.1 Delenie zakazky
...

## 3. Casove anomalie
### 3.1 Zverejnenie cez vikend
...

## 4. Fantomovi dodavatelia
...

## 5. Extrakcie
...

## 6. Dlznicki
...

## 7. Bonusove kontroly
### 7.1 Dodavatelia so zapornym vlastnym imanim
...
### 7.2 Spiace firmy (dormant-then-active)
...
### 7.3 Denne rozlozenie objemu
...

---

## Zhrnutie najdov

| # | Nazov najdu | Kategoria | Severity | Pocet zaznamov |
|---|-------------|-----------|----------|----------------|
| 1 | ...         | ...       | ...      | ...            |

**Tieto najdy este neboli validovane** — pred reportovanim pouzite
skill critical-validation.
```

## Example invocation

**User says:** "Preskenuj zmluvy za januar 2026"

**Agent interprets:**
- `date_from` = `2026-01-01`
- `date_to` = `2026-02-01`

**Agent runs:** All 20 queries via the SQL API in 4 batches, e.g.:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+dodavatel,+dodavatel_ico,+count(*)+as+pocet,+printf('%.2f',+sum(suma))+as+celkom+FROM+zmluvy+WHERE+datum_zverejnenia+>=+'2026-01-01'+AND+datum_zverejnenia+<+'2026-02-01'+GROUP+BY+dodavatel_ico+ORDER+BY+sum(suma)+DESC+LIMIT+30&_shape=array
```

**Agent outputs:** The structured report above with all non-empty query results,
markdown tables, and a summary table of findings.

**What happens next:** The output feeds into critical-validation for
verification before anything gets reported.
