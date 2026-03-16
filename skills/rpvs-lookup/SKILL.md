---
name: rpvs-lookup
description: Look up beneficial owners (konecni uzivatelia vyhod) of Slovak companies on rpvs.gov.sk using Playwright browser automation. Cross-reference UBOs across multiple suppliers to detect coordinated networks. Use this skill whenever you need to check RPVS registration, find who really owns a company receiving public money, verify public sector partner status for a given ICO, when finstat-enrichment or critical-validation flags missing_rpvs, or when investigating whether the same person controls multiple suppliers winning contracts from the same buyer.
---

# RPVS Beneficial Ownership Lookup

Look up the ultimate beneficial owners (UBOs) of Slovak companies on the
Register of Public Sector Partners (RPVS). Any company receiving >100K EUR
in public contracts or >250K EUR in other public funds must be registered.

This answers the critical question: **Who really benefits from this contract?**

## Input

| Field | Description | Example |
|-------|-------------|---------|
| `icos` | One or more ICO numbers to check | 44965257, 51900921 |
| `context` | Why these companies matter | CONFIRMED suppliers, trojity dlznik |

## Pre-check: Skip state entities (no browser needed)

RPVS only applies to private companies. Before launching the browser, filter
out state entities by checking ICO patterns in CRZ:

```sql
-- Find the supplier's contracts and check if it's a state entity
SELECT z.dodavatel, replace(z.dodavatel_ico, ' ', '') as ico,
       z.rezort, z.objednavatel,
       printf('%.2f', SUM(z.suma)) as total_suma,
       COUNT(*) as contracts
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') IN ('{ico1}', '{ico2}')
GROUP BY ico;
```

Skip RPVS lookup for entities that are clearly state institutions:
- Ministries (Ministerstvo...)
- Universities (Univerzita..., STU, TUKE)
- State funds (Statny fond..., SFRB)
- Agencies (Implementacna agentura..., NDS)
- Hospitals (Nemocnica..., UVN)

These are public entities — they don't have private beneficial owners.

## Step 1: Navigate to RPVS

```
browser_navigate -> https://rpvs.gov.sk/rpvs
```

## Step 2: Search by ICO

Fill the search field and submit:
```
browser_fill_form ->
  field: textbox "Vyhladat podla priezviska, obchodneho mena alebo ICO"
  value: "{ico}"
```
Click the search icon (generic element next to the search box with cursor=pointer).

**Wait for results** — the page uses async loading. Take a snapshot after
clicking to confirm results appeared.

**If search returns 0 results:**
1. Wait 2-3 seconds and take another snapshot (async loading may be slow)
2. If still 0, clear the search field and retry the same ICO
3. If still 0, try searching by **company name** instead of ICO
4. Only report NEREGISTROVANY after both ICO and name search fail

The RPVS search is sometimes flaky — a company can be registered but the
search may return 0 on the first attempt. Always retry before concluding
a company is not registered.

## Step 3: Interpret search results

The results table has columns:

| Column | Meaning |
|---|---|
| Cislo vlozky | File number |
| Meno osoby | Entity name |
| Typ osoby | Entity type ("Partner verejneho sektora") |
| ICO | Company ID |
| Stav | **Platny** = active, **Neplatny** = inactive |
| Meno opravnenej osoby | Authorized verifier (law firm) |
| Datum zapisu | Registration date |

**"Nie su k dispozicii ziadne data"** = NOT REGISTERED. This is a major
zlta stopa for companies with >100K EUR in public contracts — but only
after confirming via retry (see Step 2 fallback).

## Step 4: Open detail page

Click the company name button in the **Platny** (active) row.
Detail URL pattern: `https://rpvs.gov.sk/rpvs/Partner/Partner/Detail/{vlozka_id}`

## Step 5: Extract key data

| Section | What to extract |
|---|---|
| **Partner verejneho sektora** | Obchodne meno, ICO, Pravna forma, Adresa, Datum zapisu/vymazu |
| **Opravnena osoba** | Law firm verifying the UBO (name, ICO, address) |
| **Konecni uzivatelia vyhod** | **THE KEY DATA** — Meno, Datum narodenia, Statna prislusnost, Adresa, Verejny funkcionar (Ano/Nie) |
| **Verejni funkcionari v riadiacej strukture** | Public officials in management |
| **Oznamenie o overeni** | Last verification date and type |
| **Udelene pokuty** | Any fines issued |
| **Kvalifikovany podnet** | Qualified complaints filed |

Also available: link to **Verifikacny dokument (pdf)** — only open if
specifically requested or if the UBO data on the detail page is incomplete.

**Efficiency tip:** The detail page usually shows all key data in one
snapshot. Extract everything from the snapshot rather than clicking into
sub-sections. One snapshot of the detail page should give you: partner
data, opravnena osoba, UBOs, verification date, fines, and complaints.

## Step 5b: Historical data (when to go deeper)

Historical UBO data shows ownership changes over time. Navigate to
`/rpvs/Partner/Partner/HistorickyDetail/{vlozka_id}` or click
"Zobrazit aj historicke udaje".

**When to extract history:**
- **Single company with large contract (>1M EUR):** Always extract history.
  Ownership changes before big contracts are a key zlta stopa.
- **Batch mode (3+ companies):** Skip history unless the current UBO data
  raises a flag (e.g., very recent registration, or a flag from another skill).

**What to look for in history:**
- UBO change shortly before a large contract (ownership transfer to hide beneficiary)
- Frequent changes of opravnena osoba (shopping for a lenient verifier)
- Brief UBO appearances (someone added then quickly removed)

## Step 6: Cross-reference UBOs (the real value)

After collecting UBO names from multiple companies, cross-check:

1. **Same UBO across suppliers** — same person as beneficial owner of
   different companies receiving contracts from the same buyer
2. **UBO matches signatory** — check if any UBO name appears in
   signatory fields of contracts from the same objednavatel
3. **UBO is public official** — Verejny funkcionar = Ano means conflict
   of interest risk

```sql
-- Find contracts from same buyer to check for coordinated network
SELECT z.objednavatel, z.dodavatel, replace(z.dodavatel_ico,' ','') as ico,
       printf('%.2f', SUM(z.suma)) as total, COUNT(*) as contracts
FROM zmluvy z
WHERE z.objednavatel IN (
  SELECT z2.objednavatel FROM zmluvy z2
  WHERE replace(z2.dodavatel_ico,' ','') IN ('{ico1}', '{ico2}')
)
AND replace(z.dodavatel_ico,' ','') IN ('{ico1}', '{ico2}')
GROUP BY z.objednavatel, ico
ORDER BY total DESC;
```

## Batch strategy for multiple ICOs

When checking 3+ companies, optimize for speed:
1. Filter out state entities (no browser needed)
2. Open browser once, navigate to rpvs.gov.sk/rpvs
3. Search each ICO sequentially — after each search, extract current UBOs
   from the detail page snapshot (skip historical data unless flagged)
4. Collect all UBO names into a list
5. After all lookups, cross-reference UBO names for overlaps
6. Only go back for historical data on companies where flags warrant it

## Zlte stopy

| Zlta stopa | Severity | Condition |
|---|---|---|
| **Missing from RPVS** | DANGER | Company receiving >100K public money but not registered |
| **Verejny funkcionar = Ano** | DANGER | Beneficial owner is a public official (conflict of interest) |
| **Same UBO across suppliers** | DANGER | One person controls several companies with same buyer |
| **Recent ownership change** | WARNING | UBO changed shortly before large contract |
| **Stale verification** | WARNING | Last verification > 1 year old |
| **Fines or complaints** | DANGER | Entries in Udelene pokuty or Kvalifikovany podnet |
| **Foreign beneficial owners** | INFO | Worth noting for transparency |

## Output template

```markdown
# RPVS lookup: {context}

## Sumar
- Firmy skontrolovane: {N}
- Registrovane v RPVS: {X} z {N}
- Neregistrovane (>100K EUR): {Y}
- Prekryv UBO: {ziadny / najdeny}
- Zlte stopy: {Z}

---

## Firma 1: {nazov} (ICO {ico})

### RPVS status
| Pole | Hodnota |
|---|---|
| Stav | Platny / Neplatny / NEREGISTROVANY |
| Cislo vlozky | {vlozka} |
| Datum zapisu | {datum} |
| Opravnena osoba | {law_firm} |
| Posledne overenie | {datum_overenia} |

### Konecni uzivatelia vyhod
| Meno | Datum narodenia | Statna prislusnost | Verejny funkcionar |
|---|---|---|---|
| {meno} | {datum} | {prislusnost} | Ano / Nie |

### CRZ kontrakty (>100K EUR)
| ID | Nazov | Objednavatel | Suma (EUR) |
|---|---|---|---|
| {id} | {nazov} | {objednavatel} | {suma} |

### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| {flag} | {severity} | {detail} |

---

[...repeat for each company...]

## Prekryv UBO (ak najdeny)
| UBO meno | Firma 1 | Firma 2 | Spolocny objednavatel |
|---|---|---|---|
| {meno} | {firma1} | {firma2} | {objednavatel} |

---

**Lookup ukonceny.** {summary}
```
