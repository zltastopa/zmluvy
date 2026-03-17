---
name: foaf-network
description: Map a Slovak company's corporate network using foaf.sk via Playwright browser automation. Extract board members, shareholders, related companies, ownership chains, and debt status. Use this skill whenever you need to trace corporate connections, find related entities, build a person-to-company matrix, when rpvs-lookup reveals shared UBOs across suppliers, when investigating whether the same persons control multiple companies contracting with the same buyer, or when the user asks about company ownership, connections, or network analysis.
---

# Foaf.sk Corporate Network Mapping

Map the full corporate network around a Slovak company or person using foaf.sk.
This answers the critical question: **Who else does this person/company control?**

A CRZ contract shows two parties. Foaf.sk shows the hidden network behind them —
shared board members, ownership chains, family clusters, shell companies.

## Input

| Field | Description | Example |
|-------|-------------|---------|
| `target` | Company ICO or person name | 44965257, "Jozef Marinic" |
| `context` | Why this investigation matters | UBO from RPVS, shared signatory |
| `depth` | How deep to trace | shallow (1 hop) / deep (follow all chains) |

## Step 1: Look up the company

Navigate directly by ICO (fastest):
```
browser_navigate -> https://www.foaf.sk/{ico}
```

Or search by name via the header search box at `https://www.foaf.sk`:
- Fill textbox "Hladat osobu, spolocnost, ICO, adresu..." with the query
- Click "Hladat"

**Efficiency tip:** Direct ICO URL is faster than search. Always use
`https://www.foaf.sk/{ico}` when you have the ICO.

## Step 2: Extract company data from snapshot

Take one snapshot of the company page. Extract all of the following from
that single snapshot — don't click into sub-pages yet:

| Section | What to extract |
|---|---|
| **Fakturacne udaje** | ICO, DIC, IC DPH, registered court |
| **Osoby vo firme** | ALL persons with roles and dates: Konatel, Spolocnik, Predstavenstvo, Prokurista, Dozorna rada, Jediny akcionar |
| **Prepojene osoby** (sidebar) | Person connections (names + company count) |
| **Prepojene spolocnosti** (sidebar) | Related companies (names + relationship type) |
| **Dlhy a nedoplatky** | Debt status — note if "Zobrazit dlhy" link is present |
| **Obchodne cinnosti** | SK NACE codes |

**One snapshot should capture most of this.** Only navigate further if
specific sections are cut off or if you need person detail pages.

## Step 2b: Check historical persons

The company page may also show historical konatelia/spolocnici (marked with
end dates or in a "Historicky prehlad" section). Former directors often
retain connections to the company's network — they may still control related
entities that contract with the same buyers.

**In deep mode:** Also check the "Historicky prehlad" tab/link on foaf.sk.
Include former konatelia in your person list for Step 3 tracing, especially
if they had long tenures or overlap with the contract period.

**In shallow mode:** Note historical persons but don't trace them further.

## Step 3: Trace persons (the critical step)

For each person found in Step 2 (and 2b in deep mode), check their other
companies. This detects **the same persons controlling multiple companies**
contracting with the same buyer.

**Efficient approach:**
- Use the "Prepojene osoby" sidebar link count first — if a person shows
  "1 firma", they only have this one company, no need to click further
- Only click into persons with 2+ companies
- When searching a person, use `https://www.foaf.sk/search?searchString={name}`

**Who to trace (prioritized):**
1. Current konatelia and spolocnici — always trace in deep mode
2. Historical konatelia with long tenure — trace in deep mode (they often
   still control related entities)
3. Prokuristi and dozorna rada members — trace if they show 3+ companies
4. Persons appearing only in "Prepojene osoby" sidebar — note but lower priority

Look for:
- Multiple companies linked to the same person
- Same-address companies — entities sharing registered office
- Companies that also appear in CRZ as suppliers to the same buyer

## Step 4: Build person-to-company matrix

When multiple companies are investigated, build a cross-reference matrix:

```
| Funkcia | Company A | Company B | Company C |
|---|---|---|---|
| Konatel | Jan Novak | Jan Novak | - |
| Spolocnik | Jan Novak | Jan Novak | Maria Novakova |
| Jediny akcionar | - | Company A | Company A |
| Dozorna rada | Peter Horvat | - | Peter Horvat |
```

Then cross-check against CRZ:

```sql
-- Check if related companies also have CRZ contracts
SELECT z.dodavatel, replace(z.dodavatel_ico,' ','') as ico,
       z.objednavatel, printf('%.2f', SUM(z.suma)) as total,
       COUNT(*) as contracts
FROM zmluvy z
WHERE replace(z.dodavatel_ico,' ','') IN ('{ico1}', '{ico2}', '{ico3}')
GROUP BY ico, z.objednavatel
ORDER BY SUM(z.suma) DESC;
```

## Step 5: Trace ownership chains (if needed)

If a **Jediny akcionar** (sole shareholder) is another company, look that
company up too. Continue until you reach a natural person or a loop.

```
Company C (ICO: 55555555)
  └── owned by Company B (ICO: 44444444)
       └── owned by Company A (ICO: 33333333)
            └── owned by Jan Novak (natural person)
```

**When to trace chains:**
- Always trace if the sole shareholder is a foreign company (offshore risk)
- Always trace if the chain goes through 3+ entities (opacity)
- Skip if the sole shareholder is a well-known Slovak holding company

**Ownership-focused tasks:** When the user specifically asks "who controls
this company" or "trace ownership", focus on the ownership chain (Steps 1,
2, 5) and skip broad person tracing (Steps 3-4) unless you find something
suspicious along the way. This keeps the investigation efficient — don't
build a full person-to-company matrix when only the ownership chain was
requested.

## Depth strategy

| Depth | When to use | What to do |
|---|---|---|
| **Shallow** (1 hop) | Quick check, batch of 5+ companies | Extract company data + note connected persons, don't trace further |
| **Deep** (follow chains) | Single company investigation, suspicious findings | Trace all persons to their other companies, follow ownership chains, build full matrix |

Default to **shallow** for batch lookups, **deep** for single-company investigations.

## Key patterns to detect

| Pattern | What it means |
|---|---|
| **Identical boards across companies** | Same persons, same roles = shell company network |
| **Same registered address** | Multiple entities at one location |
| **Family clusters** | Shared surnames (e.g., Kovacic + Kovacicova) |
| **Recently appointed boards** | All members appointed on same date shortly before contracts |
| **Ownership chains** | Company A owns B owns C — trace to ultimate controller |
| **Cross-entity board overlap** | Same person on boards of companies contracting with same buyer |

## Zlte stopy

| Zlta stopa | Severity | Condition |
|---|---|---|
| **Same person in multiple supplier companies** | DANGER | Companies contract with the same buyer |
| **Recently appointed board members** | WARNING | Installed shortly before large contracts |
| **Sole shareholder chain** | WARNING | Opaque ownership through holding companies |
| **Dlhy a nedoplatky flagged** | DANGER | Confirms known debts/arrears |
| **Family connections in multiple roles** | WARNING | Family-controlled structure across suppliers |
| **Same address, different companies** | WARNING | Possible shell company cluster |

## Limitations

Foaf.sk has a premium paywall for some features (e.g., "zobrazit firmy kde
ma funkcie"). The free tier provides company profiles, persons in company,
connections, and basic financial indicators. If blocked by paywall, work
with available data and note the limitation.

## Output template

```markdown
# Foaf.sk network mapping: {target}

## Sumar
- Firmy preskumane: {N}
- Osoby identifikovane: {M}
- Prekryv osob medzi firmami: {ziadny / najdeny}
- Zlte stopy: {Z}

---

## Firma 1: {nazov} (ICO {ico})

### Osoby vo firme
| Meno | Funkcia | Od | Dalsie firmy |
|---|---|---|---|
| {meno} | {konatel/spolocnik/...} | {datum} | {pocet} |

### Prepojene spolocnosti
| Firma | ICO | Vztah | CRZ kontrakty |
|---|---|---|---|
| {nazov} | {ico} | {spolocny konatel / dcerska spolocnost / ...} | {ano/nie, suma} |

### Vlastnicka struktura
{ownership chain if applicable}

### Dlhy a nedoplatky
{status}

### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| {flag} | {severity} | {detail} |

---

## Person-to-company matrix (ak viacero firiem)
| Funkcia | Firma A | Firma B | Firma C |
|---|---|---|---|
| {role} | {name} | {name} | - |

---

**Lookup ukonceny.** {summary}
```
