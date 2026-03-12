---
name: uvo-procurement
description: Look up public procurement data from UVO (Urad pre verejne obstaravanie) via browser automation. Cross-reference CRZ contracts with vestnik announcements, procurement results, bid counts, competitor rankings, and evaluation records. Use when investigating whether a CRZ contract went through proper procurement, who else bid, what the winning price was, or to find procurement irregularities.
---

# UVO Procurement Lookup

Cross-reference CRZ contracts with public procurement data from UVO
(Urad pre verejne obstaravanie — Slovak Public Procurement Office).

This is critical for answering: **Was there real competition?**

## Why UVO matters for investigations

A CRZ contract shows the result (who got the money). UVO shows the process
(was there competition, how many bids, who else competed, was the price fair).
Comparing both reveals:
- Contracts that bypassed procurement entirely
- Procurements with suspiciously few bidders
- Winners whose price was far from second place
- Repeated sole-source awards to the same supplier

## Data sources

### 1. Vestnik verejneho obstaravania (UVO Bulletin)

Official announcements of public procurement.

**Base URL:** `https://www.uvo.gov.sk`

**Key URL patterns:**
- Vestnik announcement: `https://www.uvo.gov.sk/vestnik/oznamenie/detail/{id}`
- Procurement search: `https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek`
- Procurement detail: `https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek/detail/{id}`
- Buyer profile: `https://www.uvo.gov.sk/vyhladavanie-profilov/zakazky/{profile_id}`

**What you find in Vestnik:**
| Data | Where |
|---|---|
| Oznamenie o vyhlaseni sutaze | Announcement that procurement was launched |
| Oznamenie o vysledku | Who won, final price |
| Vitazna ponuka (cena) | Winning bid price |
| Pocet predlozenych ponuk | Number of bids received |
| Nazov vitaza | Winner name and ICO |
| Niekedy poradie uchadzacov | Ranking of bidders (not always) |

### 2. Profil verejneho obstaravatela (Buyer Profile)

Each contracting authority has a public profile on UVO or their own website.

**What you find in the profile:**
| Data | Where |
|---|---|
| Zapisnica z vyhodnotenia ponuk | Bid evaluation minutes |
| Poradie uchadzacov | Full ranking of all bidders |
| Bodove hodnotenie | Point scoring of each bid |
| Odovodnenie vyberu | Reasoning for selecting the winner |
| Zoznam vylucenych | Excluded bidders and why |

This is the **best source** for seeing who finished second, third, and why.

### 3. Electronic procurement systems

Many procurements run through electronic platforms:

| System | URL | Notes |
|---|---|---|
| **EVO / IS EVO** | `https://www.isepvo.sk` | State e-procurement system |
| **Josephine** | `https://josephine.proebiz.com` | Popular private platform |
| **Tendernet** | `https://www.tendernet.sk` | Another private platform |

If you know the procurement name, search directly in these systems.

## Step 1: Check if CRZ contract has a UVO link

Many CRZ contracts already have a `uvo_url` field:

```sql
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
       printf('%.2f', z.suma) as suma, z.uvo_url
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '{ico}'
  AND z.uvo_url IS NOT NULL AND z.uvo_url <> ''
ORDER BY z.suma DESC;
```

~3,300 contracts have UVO URLs. Sources include uvo.gov.sk (~1,770),
Josephine (~230), IS EVO (~120), and others.

## Step 2: Search UVO by buyer or supplier (Playwright browser)

If no `uvo_url` exists, search UVO directly.

### Search by buyer (objednavatel):

```
mcp__plugin_playwright_playwright__browser_navigate ->
  https://www.uvo.gov.sk/vyhladavanie/vyhladavanie-zakaziek
```

Fill the search form:
- **Nazov zakazky** — contract title or keywords
- **Obstaravatel** — buyer name or ICO
- **Dodavatel** — supplier name or ICO
- **CPV kod** — Common Procurement Vocabulary code (if known)
- **Datum od / do** — date range

Click "Vyhladat" to search.

### Search by supplier:

You can also search by supplier (dodavatel) name or ICO to find all
procurements a company has participated in — not just won.

### Direct Vestnik search:

```
mcp__plugin_playwright_playwright__browser_navigate ->
  https://www.uvo.gov.sk/vestnik
```

Search vestnik announcements by keyword, ICO, or announcement number.

## Step 3: Extract from procurement detail page

Navigate to the detail page (from search results or `uvo_url`).

### Key sections to extract:

| Section | What to look for |
|---|---|
| **Zakladne udaje** | Nazov zakazky, typ postupu (open/restricted/negotiated), predpokladana hodnota |
| **Obstaravatel** | Buyer name, ICO, address |
| **Predmet zakazky** | CPV codes, description, lots (casti) |
| **Vysledok** | Vitaz (winner), konecna cena, pocet ponuk |
| **Uchadzaci** | List of all bidders (if published) |
| **Dokumenty** | Zapisnica, vyhodnotenie, zmluva |

### Key fields to record:

```
Nazov zakazky: ...
Typ postupu: priame rokovacie konanie / sutaz / uzsia sutaz / ...
Predpokladana hodnota: ... EUR (bez DPH)
Pocet predlozenych ponuk: N
Vitaz: {name} (ICO: {ico})
Vitazna cena: ... EUR (bez DPH)
Druhy v poradi: {name} — cena: ... EUR (ak je zverejnene)
```

## Step 4: Check the buyer profile for evaluation details

Navigate to the buyer's profile:
```
mcp__plugin_playwright_playwright__browser_navigate ->
  https://www.uvo.gov.sk/vyhladavanie-profilov/zakazky/{profile_id}
```

Or find it by searching for the buyer on UVO. The profile page contains
procurement documents including:
- **Zapisnica z otvarania ponuk** — bid opening minutes (lists all bidders and prices)
- **Zapisnica z vyhodnotenia** — evaluation record (scoring, ranking)
- **Sprava o zakazke** — procurement report (reasoning)

These are often PDF documents. Download and review them for full bidder lists.

## Step 5: Check electronic systems (if applicable)

### Josephine
```
mcp__plugin_playwright_playwright__browser_navigate ->
  https://josephine.proebiz.com/sk/tender/{tender_id}/summary
```

Josephine tender pages show:
- Tender summary and timeline
- Participating bidders
- Evaluation results
- Documents

### IS EVO
```
mcp__plugin_playwright_playwright__browser_navigate ->
  https://www.isepvo.sk
```

Search by procurement name or reference number.

## Zlte stopy from UVO data

| Zlta stopa | Severity | When |
|---|---|---|
| **No UVO record for large contract** | danger | Contract >15K (goods/services) or >50K (works) with no procurement record |
| **Single bidder** | warning | Pocet ponuk = 1 — no competition |
| **Priame rokovacie konanie** | warning | Direct negotiation instead of open competition — check justification |
| **Winning price = predpokladana hodnota** | warning | Winner bid exactly matches the estimated value (information leak?) |
| **Repeated sole-source** | danger | Same supplier wins multiple direct negotiations from same buyer |
| **Large gap to second bidder** | info | Winner's price significantly lower than #2 — check if realistic |
| **Excluded bidders** | warning | Multiple bidders excluded on technicalities — possible manipulation |
| **Price above estimate** | warning | Winning price exceeds predpokladana hodnota significantly |
| **Contract value differs from UVO** | warning | CRZ suma differs significantly from UVO vitazna cena |

## Cross-referencing UVO with CRZ

### Find CRZ contracts without procurement record:
```sql
-- Large contracts with no UVO link (potential bypassed procurement)
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.dodavatel_ico,
       printf('%.2f', z.suma) as suma, z.datum_zverejnenia, z.rezort
FROM zmluvy z
WHERE z.suma > 50000
  AND (z.uvo_url IS NULL OR z.uvo_url = '')
  AND z.typ <> 'Dodatok'
ORDER BY z.suma DESC LIMIT 50;
```

### Find all procurements for a supplier:
```sql
-- Contracts with UVO links for a specific supplier
SELECT z.id, z.nazov_zmluvy, printf('%.2f', z.suma) as suma,
       z.uvo_url, z.datum_podpisu
FROM zmluvy z
WHERE replace(z.dodavatel_ico, ' ', '') = '{ico}'
  AND z.uvo_url IS NOT NULL AND z.uvo_url <> ''
ORDER BY z.suma DESC;
```

### Compare CRZ contract value to UVO winning price:
After extracting the winning price from UVO, compare with the CRZ contract
amount. Significant differences may indicate contract modifications, hidden
costs, or data discrepancies.

## Output

For each contract/procurement checked, report:
- Whether a UVO procurement record exists
- Procurement type (open competition / direct negotiation / restricted)
- Number of bidders
- Winner and winning price
- Comparison with CRZ contract value
- Any zlte stopy detected
- Links to source documents (zapisnica, vyhodnotenie)
