---
name: foaf-network
description: Map a Slovak company's corporate network using foaf.sk via Playwright browser automation. Extract board members, shareholders, related companies, ownership chains, and debt status. Use when you need to trace corporate connections, find related entities, or build a person-to-company matrix for a given ICO or person name.
---

# Foaf.sk Corporate Network Mapping

Map the full corporate network around a Slovak company or person using foaf.sk.
Identifies board members, shareholders, related companies, ownership chains,
and cross-entity overlaps.

## Input

A **company ICO** or **person name** to investigate.

## Step 1: Look up the company

Navigate directly by ICO:
```
mcp__plugin_playwright_playwright__browser_navigate -> https://www.foaf.sk/{ico}
```

Or search by name via the header search box at `https://www.foaf.sk`:
- Fill textbox "Hladat osobu, spolocnost, ICO, adresu..." with the query
- Click "Hladat"
- Search URL pattern: `https://www.foaf.sk/search?searchString={query}`

## Step 2: Extract company data

| Section | What to extract |
|---|---|
| **Fakturacne udaje** | ICO, DIC, IC DPH, registered court |
| **Osoby vo firme** | ALL persons with roles and appointment dates ("Od"): Predstavenstvo (board), Prokurista, Dozorna rada, Jediny akcionar, Spolocnik |
| **Prepojene osoby** (sidebar) | Level 1 person connections |
| **Prepojene spolocnosti** (sidebar) | Parent/subsidiary, shared shareholders |
| **Dlhy a nedoplatky** | Debt status — "Zobrazit dlhy" link if present |
| **Obchodne cinnosti** | SK NACE codes — what the company actually does |

## Step 3: Trace persons

For each person found in Step 2, search their name on foaf.sk to find ALL
their other companies. This is the critical step for detecting **the same
persons controlling multiple companies** that contract with the same buyer.

When searching for a person name, look for:
- **"Osoba vo firme: {name}"** entries — companies where this person has a role
- Multiple companies linked to the same person
- Same-address companies — entities sharing registered office

## Step 4: Trace related companies

For each related company found, look it up by ICO, extract its board,
and compare with the target. Build a **person-to-company matrix**:

| Funkcia | Company A | Company B | Company C |
|---|---|---|---|
| Konatel | Jan Novak | Jan Novak | - |
| Spolocnik | Jan Novak | Jan Novak | Maria Novakova |
| Jediny akcionar | - | Company A | Company A |
| Dozorna rada | Peter Horvat | - | Peter Horvat |

## Step 5: Trace ownership chains

If a **Jediny akcionar** (sole shareholder) is another company, look that
company up too. Continue until you reach a natural person or a loop.

```
Company C (ICO: 55555555)
  └── owned by Company B (ICO: 44444444)
       └── owned by Company A (ICO: 33333333)
            └── owned by Jan Novak (natural person)
```

## Key patterns to detect

| Pattern | What it means |
|---|---|
| **Identical boards across companies** | Same persons, same roles, same dates = shell company network |
| **Same registered address** | Multiple entities at one location |
| **Family clusters** | Shared surnames (e.g., Kovacic + Kovacicova) |
| **Recently appointed boards** | All members appointed on same date shortly before contracts |
| **Ownership chains** | Company A owns B owns C — trace to ultimate controller |
| **Cross-entity board overlap** | Same person on boards of companies contracting with same buyer |

## Zlte stopy to flag

| Zlta stopa | Severity | When |
|---|---|---|
| Same person in multiple supplier companies | danger | Companies contract with the same buyer |
| Recently appointed board members | warning | Installed shortly before large contracts |
| Sole shareholder chain | warning | Opaque ownership through holding companies |
| "Dlhy a nedoplatky" flagged | danger | Confirms known debts/arrears |
| Family connections in multiple roles | warning | Suggests family-controlled structure |

## Limitations

Foaf.sk has a premium paywall for some features (e.g., "zobrazit firmy kde ma
funkcie"). The free tier provides company profiles, persons in company,
connections, and basic financial indicators. If blocked by paywall, work with
available data.

## Output

For each company/person checked, report:
- Board members and their roles with appointment dates
- Related companies with shared persons highlighted
- Ownership chain (if applicable)
- Person-to-company matrix (if multiple companies investigated)
- Debt status
