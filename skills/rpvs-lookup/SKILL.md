---
name: rpvs-lookup
description: Look up beneficial owners (konecni uzivatelia vyhod) of a Slovak company on rpvs.gov.sk using Playwright browser automation. Use when you need to check RPVS registration, find UBOs, or verify public sector partner status for a given ICO.
---

# RPVS Beneficial Ownership Lookup

Look up the ultimate beneficial owners (UBOs) of a Slovak company on the
Register of Public Sector Partners (RPVS). Legally required for companies
receiving >100K EUR in public contracts.

## Input

One or more **ICO** numbers to check.

## Step 1: Navigate to RPVS

```
mcp__plugin_playwright_playwright__browser_navigate -> https://rpvs.gov.sk/rpvs
```

## Step 2: Search by ICO

Fill the search field and submit:
```
mcp__plugin_playwright_playwright__browser_fill_form ->
  field: textbox "Vyhladat podla priezviska, obchodneho mena alebo ICO"
  value: "{ico}"
```
Click the search icon (generic element next to the search box with cursor=pointer).

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
zlta stopa for companies with large public contracts.

## Step 4: Open detail page

Click the company name button in the **Platny** (active) row.
Detail URL pattern: `https://rpvs.gov.sk/rpvs/Partner/Partner/Detail/{vlozka_id}`

## Step 5: Extract key data

| Section | What to extract |
|---|---|
| **Partner verejneho sektora** | Obchodne meno, ICO, Pravna forma, Adresa, Datum zapisu/vymazu |
| **Opravnena osoba** | Law firm verifying the UBO (name, ICO, address) |
| **Konecni uzivatelia vyhod** | **THE KEY DATA** — Meno a priezvisko, Datum narodenia, Statna prislusnost, Adresa, Verejny funkcionar (Ano/Nie) |
| **Verejni funkcionari v riadiacej strukture** | Public officials in management |
| **Oznamenie o overeni** | Last verification date and type |
| **Udelene pokuty** | Any fines issued |
| **Kvalifikovany podnet** | Qualified complaints filed |

Also available: link to **Verifikacny dokument (pdf)** with full UBO verification report.

## Step 6: Historical data (optional)

Click "Zobrazit aj historicke udaje" for ownership history.
URL: `/rpvs/Partner/Partner/HistorickyDetail/{vlozka_id}`

## Zlte stopy to flag

| Zlta stopa | Severity | When |
|---|---|---|
| Missing from RPVS | danger | Company receiving >100K public money but not registered |
| Verejny funkcionar = Ano | danger | Beneficial owner is a public official (conflict of interest) |
| Recent ownership change | warning | UBO changed shortly before large contract |
| Same UBO across suppliers | danger | One person controls several companies with same buyer |
| Foreign beneficial owners | info | Worth noting for transparency |
| Stale verification | warning | Last verification date is very old |
| Fines or complaints | danger | Entries in Udelene pokuty or Kvalifikovany podnet |

## Cross-referencing UBOs

After collecting UBO names from multiple companies, check if the same person
appears as beneficial owner of different companies receiving contracts from
the same buyer — this is a strong indicator of a coordinated network.

## Output

For each ICO checked, report:
- RPVS status (registered/not registered)
- UBO names and whether they are public officials
- Any fines or complaints
- Last verification date
