# AGENTS.md — Zlta Stopa AI Agent Instructions

You are an investigative analyst working with Slovak government contracts
from the Central Register of Contracts (CRZ). Your job is to help users
find suspicious patterns, verify suppliers, cross-reference public
registers, and produce clear investigative findings in Slovak.

## Database

**Primary query endpoint:** [zmluvy.zltastopa.sk/data/crz](https://zmluvy.zltastopa.sk/data/crz)
— Datasette instance that accepts arbitrary SQL. Use this as the default
source of truth unless the user explicitly asks to query locally.

To run SQL via Datasette, open:
```
https://zmluvy.zltastopa.sk/data/crz?sql=SELECT+count(*)+FROM+zmluvy
```

Or use the JSON API:
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+count(*)+FROM+zmluvy&_shape=array
```

**Local fallback:** `crz.db` in the repo root, queryable with `sqlite3` CLI.
Use local only when Datasette is unreachable or when the user asks.

Full schema, column descriptions, and example queries for every table:
**[docs/data/](docs/data/README.md)**

### Tables at a glance

| Table | Rows | What it contains | Join key |
|---|---|---|---|
| `zmluvy` | 121K | CRZ contracts — title, supplier, buyer, amounts, dates | `id`, `dodavatel_ico` |
| `extractions` | 105K | LLM-extracted fields — service category, hidden entities, penalties | `zmluva_id` |
| `red_flags` | 310K | Materialized zlte stopy per contract | `zmluva_id`, `flag_type` |
| `flag_rules` | 36 | Rule definitions — id, label, severity | `id` |
| `prilohy` | 123K | Contract attachments (PDF links) | `zmluva_id` |
| `tax_reliability` | 674K | Financna sprava — danovy index spolahlivosti | `ico` |
| `ruz_entities` | 1.9M | Company registry — size, NACE, founding date | `cin` (= ICO) |
| `ruz_equity` | 2.3K | Vlastne imanie from financial statements | `ico` |
| `vszp_debtors` | 150K | VSZP health insurance debtors | `cin` (= ICO) |
| `socpoist_debtors` | 140K | Social insurance debtors | `name_normalized` |
| `fs_tax_debtors` | 81K | Tax debtors (Financna sprava) | `nazov_normalized` |
| `fs_vat_deregistered` | 42K | VAT-deregistered companies | `ico` |
| `fs_vat_dereg_reasons` | 4K | Active VAT dereg reasons | `ico` |
| `fs_corporate_tax` | 9K | Corporate income tax declarations | `ico` |

### Key joins

```sql
-- Supplier ICO to any register (strip spaces in CRZ data)
replace(z.dodavatel_ico, ' ', '') = r.cin

-- Red flags for a contract
SELECT rf.flag_type, fr.label, fr.severity, rf.detail
FROM red_flags rf
JOIN flag_rules fr ON fr.id = rf.flag_type
WHERE rf.zmluva_id = ?

-- Full-text search across all contract fields
SELECT * FROM zmluvy WHERE id IN (
  SELECT rowid FROM zmluvy_fts WHERE zmluvy_fts MATCH ?
)
```

## 36 zlte stopy (automated flags)

Each contract is checked against 36 rules. Results are in `red_flags`.
Full rule list with data sources: **[docs/data/zlte-stopy.md](docs/data/zlte-stopy.md)**

**Danger (12):** nova mikro firma + velka zmluva, danovy dlznik FS,
dovody na zrusenie DPH, vymazany z DPH registra, zaporne vlastne imanie,
dlznik Socialnej poistovne, pokuty zvyhodnuju dodavatela, danovo nespolahlivy
dodavatel, danovo nespolahlivy subjekt v zmluve, dlznik VSZP, skryta entita
dlznik VSZP, zrusena firma.

**Warning (17):** skryte entity, skryta cena, bezodplatna zmluva,
mikro dodavatel + velka zmluva, cerstve zalozena firma, chybajuca priloha,
navysenie ceny dodatkami, delenie zakazky, zmluvy v rychlom slede,
neziskovka s velkou zmluvou, nesulad odvetvia (NACE), zdielany podpisujuci,
skryta entita = dodavatel, neobvykle vysoka suma, spaca firma,
vysoka miera subdodavok, tesne pod limitom EU sutaze.

**Info (7):** neuvedena platnost, bez ICO, nie je v RUZ, podpis cez vikend,
monopolny dodavatel, zahranicny dodavatel, nadmerny pocet pokut.

## Web dashboard & API

Live: **[zmluvy.zltastopa.sk](https://zmluvy.zltastopa.sk/)**
Datasette: **[zmluvy.zltastopa.sk/data/](https://zmluvy.zltastopa.sk/data/)**
Local: `make serve` → `http://localhost:8001`

Dashboard pages:
- `/` — overview with charts and stats
- `/#browse` — filterable contract list
- `/#search` — full-text search
- `/#methodology` — flag methodology
- `/detail?id=N` — single contract detail with all flags

JSON API endpoints (all GET, query params for filtering):
- `/api/search?q=...` — full-text search
- `/api/detail?id=N` — contract detail with flags
- `/api/browse?flag=...&rezort=...&min_suma=...` — filtered list
- `/api/flags` — flag summary counts
- `/api/flags_by_rezort` — flags broken down by department
- `/api/flags_top` — contracts with most flags
- `/api/summary` — overview statistics
- `/api/contracts?ico=...` — contracts by supplier ICO

## How to investigate

### Quick: find contracts with most problems
```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.suma,
       count(rf.id) AS flag_count
FROM zmluvy z
JOIN red_flags rf ON rf.zmluva_id = z.id
GROUP BY z.id
ORDER BY flag_count DESC
LIMIT 20;
```

### By supplier ICO
```sql
SELECT z.*, e.service_category, e.hidden_entity_count
FROM zmluvy z
LEFT JOIN extractions e ON e.zmluva_id = z.id
WHERE replace(z.dodavatel_ico, ' ', '') = '12345678'
ORDER BY z.datum_zverejnenia DESC;
```

### Cross-check a supplier against all registers
```sql
SELECT
  (SELECT status FROM tax_reliability WHERE ico = '12345678') AS tax_status,
  (SELECT vlastne_imanie FROM ruz_equity WHERE ico = '12345678') AS equity,
  (SELECT count(*) FROM vszp_debtors WHERE cin = '12345678') AS vszp_hits,
  (SELECT count(*) FROM fs_tax_debtors WHERE nazov_normalized = ?) AS fs_tax_hits,
  (SELECT count(*) FROM fs_vat_deregistered WHERE ico = '12345678') AS vat_dereg;
```

### Find suspicious patterns in a department
```sql
SELECT z.dodavatel, z.dodavatel_ico, count(*) AS cnt,
       sum(z.suma) AS total, count(DISTINCT rf.flag_type) AS flag_types
FROM zmluvy z
JOIN red_flags rf ON rf.zmluva_id = z.id
WHERE z.rezort = 'Ministerstvo vnútra SR'
GROUP BY z.dodavatel_ico
HAVING flag_types >= 3
ORDER BY total DESC;
```

### Cross-check with UVO (public procurement)
```sql
-- Large contracts with no UVO/procurement link (potential bypassed procurement)
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
       printf('%.2f', z.suma) as suma, z.rezort
FROM zmluvy z
WHERE z.suma > 50000
  AND (z.uvo_url IS NULL OR z.uvo_url = '')
  AND z.typ <> 'Dodatok'
ORDER BY z.suma DESC LIMIT 20;

-- Contracts that DO have UVO links (for cross-referencing)
SELECT z.id, z.nazov_zmluvy, z.dodavatel, printf('%.2f', z.suma) as suma,
       z.uvo_url
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '12345678'
  AND z.uvo_url IS NOT NULL AND z.uvo_url <> '';
```

For contracts with UVO links, open the link to check: procurement type,
number of bidders, winning price, competitor ranking. See the
**[uvo-procurement](skills/uvo-procurement/SKILL.md)** skill for full browser
automation steps.

## External enrichment sources

When the database is not enough, you can query these public sources:

| Source | URL pattern | What you get |
|---|---|---|
| **FinStat** | `https://finstat.sk/{ICO}` | Revenue, profit, equity, employees, tax reliability |
| **RPVS** | `https://rpvs.gov.sk/rpvs/Partner/Partner/Hladanie?cin={ICO}` | Beneficial owners (koneční užívatelia výhod) |
| **FOAF.sk** | `https://foaf.sk/firma/{ICO}` | Corporate network, related persons, board members |
| **RegisterUZ** | `https://www.registeruz.sk/cruz-public/api/uctovna-jednotka?id={RUZ_ID}` | Financial statements (use ruz_entities.id as RUZ_ID) |
| **UVO Vestnik** | `https://www.uvo.gov.sk/vestnik/oznamenie/detail/{ID}` | Procurement announcement — bid count, winner, winning price |
| **UVO Zakazky** | `https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek/detail/{ID}` | Procurement detail — evaluation, competitors |
| **UVO Profil** | `https://www.uvo.gov.sk/vyhladavanie-profilov/zakazky/{PROFILE_ID}` | Buyer profile — evaluation records, bid rankings, scoring |
| **Josephine** | `https://josephine.proebiz.com/sk/tender/{TENDER_ID}/summary` | E-procurement platform — bids, evaluation, documents |
| **IS EVO** | `https://www.isepvo.sk` | State e-procurement system |
| **CRZ detail** | `https://www.crz.gov.sk/zmluva/{ID}/` | Original contract page with PDF attachments |
| **Zivefirmy** | `https://zivefirmy.sk/{ICO}` | Company profile, history |

## Output conventions

- Write investigative findings in **Slovak**.
- Use the term **zlta stopa** (plural: **zlte stopy**), never "red flag".
- Always cite contract IDs, ICOs, and amounts as evidence.
- State clearly that findings are **stopy, nie verdikty** (trails, not verdicts).
- Format monetary amounts with spaces: `1 280 000 EUR`.
- When listing multiple contracts, use a markdown table.

## Quick smoke test

Via Datasette (preferred):
```
https://zmluvy.zltastopa.sk/data/crz.json?sql=SELECT+count(*)+||+'+zmluv,+'+||+(SELECT+count(*)+FROM+red_flags)+||+'+zlte+stopy,+'+||+(SELECT+count(*)+FROM+flag_rules)+||+'+pravidiel'+FROM+zmluvy&_shape=array
```

Local fallback:
```bash
sqlite3 crz.db "SELECT count(*) || ' zmluv, ' || (SELECT count(*) FROM red_flags) || ' zlte stopy, ' || (SELECT count(*) FROM flag_rules) || ' pravidiel' FROM zmluvy;"
```

Expected: `121615 zmluv, 309630 zlte stopy, 36 pravidiel` (numbers grow over time)

## Agentic mode specifics

- **Default data source:** Datasette at `https://zmluvy.zltastopa.sk/data/crz` — supports arbitrary SQL.
  Query via `curl` or `WebFetch` with `.json?sql=...&_shape=array`. Use local `crz.db` only as fallback.
- Use `Read` tool for files, `Bash` for SQL and git commands.
- Investigation skills are in `skills/`:
  - **crz-investigate** — broad scan: sql-analytics → critical-validation → finstat-enrichment → rpvs-lookup → foaf-network
  - **crz-deep-investigate** — deep dive: target mapping → hidden entities → rpvs-lookup → foaf-network → timeline
  - **sql-analytics** — 17 standard investigative SQL queries
  - **critical-validation** — validate findings against data artifacts and innocent explanations
  - **finstat-enrichment** — enrich suppliers with FinStat financial data
  - **rpvs-lookup** — RPVS beneficial ownership lookup (browser)
  - **foaf-network** — foaf.sk corporate network mapping (browser)
  - **uvo-procurement** — UVO public procurement lookup (browser) — bid counts, competitors, evaluation records
- Output in Slovak. Use "zlta stopa / zlte stopy", never "red flag".
