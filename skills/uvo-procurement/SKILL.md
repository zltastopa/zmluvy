---
name: uvo-procurement
description: Look up public procurement data from UVO (Urad pre verejne obstaravanie) and cross-reference with CRZ contracts. Check whether contracts went through proper procurement, how many bids were received, who else competed, and detect procurement irregularities. Use this skill whenever you need to verify procurement for a CRZ contract, when finstat-enrichment or critical-validation flags a large contract for UVO verification, when the user asks about public procurement, bidding, competition, or obstaravanie, or when investigating whether a supplier repeatedly wins without competition.
---

# UVO Procurement Lookup

Cross-reference CRZ contracts with public procurement data from UVO
(Urad pre verejne obstaravanie). This answers the critical question:
**Was there real competition?**

A CRZ contract shows the result (who got the money). UVO shows the process
(how many bids, who else competed, was the price fair).

## Input

| Field | Description | Example |
|-------|-------------|---------|
| `target` | What to look up | ICO, contract ID, or company name |
| `ico` | Supplier ICO | 44965257 |
| `contract_ids` | CRZ contract IDs | 12012856 |
| `context` | Why this matters | CONFIRMED 145M framework, triple debtor |

## Execution strategy: DB-first, browser-second

Browser automation is slow. Minimize it by checking the local DB first.

### Step 1: Check CRZ for existing UVO links (fast, no browser)

~3,300 contracts already have `uvo_url` populated. Check this first:

```sql
-- Check if contract already has UVO link
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
       printf('%.2f', z.suma) as suma, z.uvo_url
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '{ico}'
  AND z.uvo_url IS NOT NULL AND z.uvo_url <> ''
ORDER BY z.suma DESC;
```

If a `uvo_url` exists, navigate directly to it — skip the search step.

### Step 2: Find contracts WITHOUT procurement record

For contracts lacking UVO links, flag them:

```sql
-- Large contracts with no UVO link (potential bypassed procurement)
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
       printf('%.2f', z.suma) as suma, z.datum_zverejnenia, z.rezort
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '{ico}'
  AND z.suma > 50000
  AND (z.uvo_url IS NULL OR z.uvo_url = '')
  AND z.typ <> 'Dodatok'
ORDER BY z.suma DESC;
```

Contracts >15K EUR (goods/services) or >50K EUR (works) without a UVO
record are a procurement red flag.

### Step 3: Search UVO by browser (only if needed)

If Step 1 found no links and Step 2 found large contracts, search UVO:

**Search URL:** `https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek`

Fill the search form with:
- **Obstaravatel** — buyer name or ICO
- **Dodavatel** — supplier name or ICO
- **Nazov zakazky** — contract title keywords
- **Datum od / do** — date range

Or search the Vestnik directly:
`https://www.uvo.gov.sk/vestnik`

### Step 4: Extract from procurement detail page

Navigate to the detail page and extract:

| Section | What to look for |
|---|---|
| **Zakladne udaje** | Nazov zakazky, typ postupu (open/restricted/negotiated), predpokladana hodnota |
| **Obstaravatel** | Buyer name, ICO |
| **Vysledok** | Vitaz (winner), konecna cena, pocet ponuk |
| **Uchadzaci** | List of all bidders (if published) |
| **Dokumenty** | Zapisnica z vyhodnotenia, sprava o zakazke |

### Step 5: Check buyer profile for evaluation details

Navigate to buyer's profile for procurement documents:
`https://www.uvo.gov.sk/vyhladavanie-profilov/zakazky/{profile_id}`

Documents include:
- **Zapisnica z otvarania ponuk** — bid opening minutes (all bidders and prices)
- **Zapisnica z vyhodnotenia** — evaluation scoring and ranking
- **Sprava o zakazke** — procurement report with reasoning

### Step 6: Check electronic systems (if applicable)

| System | URL | Notes |
|---|---|---|
| **Josephine** | `https://josephine.proebiz.com` | Popular private platform |
| **IS EVO** | `https://www.isepvo.sk` | State e-procurement |
| **Tendernet** | `https://www.tendernet.sk` | Private platform |

## Zlte stopy from procurement data

| Zlta stopa | Severity | Condition |
|---|---|---|
| **No UVO record** | DANGER | Contract >15K (goods) or >50K (works) with no procurement |
| **Single bidder** | WARNING | Pocet ponuk = 1, no competition |
| **Priame rokovacie konanie** | WARNING | Direct negotiation — check justification |
| **Price = predpokladana hodnota** | WARNING | Winning bid exactly matches estimate (information leak?) |
| **Repeated sole-source** | DANGER | Same supplier wins multiple direct negotiations from same buyer |
| **Large gap to second bidder** | INFO | Winner significantly lower than #2 — check if realistic |
| **Excluded bidders** | WARNING | Multiple bidders excluded on technicalities |
| **Price above estimate** | WARNING | Winning price > predpokladana hodnota |
| **CRZ vs UVO price mismatch** | WARNING | CRZ suma differs significantly from UVO vitazna cena |

## Output template

```markdown
# UVO procurement lookup: {target}

## Sumar
- Kontrakty s UVO odkazom: {X} z {N}
- Kontrakty BEZ obstaravania: {Y} (>{threshold} EUR)
- Zlte stopy: {Z}

---

## Kontrakt 1: {nazov_zmluvy} ({suma} EUR)

### CRZ data
| Pole | Hodnota |
|---|---|
| ID | {crz_id} |
| Dodavatel | {dodavatel} (ICO {ico}) |
| Objednavatel | {objednavatel} |
| Suma | {suma} EUR |
| UVO URL | {uvo_url alebo "NENAJDENY"} |

### UVO data (ak najdene)
| Pole | Hodnota |
|---|---|
| Typ postupu | {open / restricted / priame rokovacie konanie} |
| Predpokladana hodnota | {predpokladana} EUR |
| Pocet ponuk | {pocet} |
| Vitazna cena | {cena} EUR |
| Druhy v poradi | {name} — {cena2} EUR |

### Zlte stopy
| Zlta stopa | Severity | Detail |
|---|---|---|
| {flag} | {severity} | {detail} |

### Hodnotenie
{1-2 sentences: was this procurement competitive? Any concerns?}

---

[...repeat for each contract...]

---

**Lookup ukonceny.** {summary}
```
