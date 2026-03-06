# CRZ Hackathon Suggestions — Open Data Heroes (March 7-8, 2026)

**Challenge by**: 360ka | 360tka.sk (Michal, Barbora)
**Core need**: Intelligently search and classify 5.5M+ Slovak government contracts

Based on deep exploration of crz.gov.sk, its data exports, and actual contract data.

---

## The Key Insight

CRZ provides **daily XML exports** with full metadata for every contract:
`https://www.crz.gov.sk/export/YYYY-MM-DD.zip` — one XML file per day, ~2,800 contracts.

PDF attachments are downloadable at: `https://www.crz.gov.sk/data/att/{filename}`

The metadata includes: contract title, buyer, supplier, ICO numbers, amounts, dates, notes — but **no semantic categorization**. A "Zmluva o dielo" could be anything.

---

## Suggestion 1: "CRZ Classifier" — LLM-Powered Contract Categorization

**Build in a weekend. Impact: transforms how journalists search CRZ.**

### What it does
Take CRZ contract metadata and use an LLM (Claude Haiku) to classify each contract into service categories: legal, IT, marketing, construction, consulting, facilities, etc.

### Why it works
Even without opening PDFs, the combination of contract title + supplier name + buyer name + notes field carries enough signal for ~75%+ accuracy. "Zmluva o dielo" + supplier "Advokátska kancelária Novák" = legal services.

### Weekend build
1. Download a few days of XML exports (instant, no scraping needed)
2. Parse XML → structured records (~50 lines of Python)
3. Send metadata to Claude Haiku for classification (~$0.00014/contract)
4. Store results in SQLite
5. Simple search UI (Streamlit or similar): filter by category, institution, amount, date

### Hackathon demo
"Show me all marketing contracts from Ministry of Agriculture over €10,000 in 2025" — a query that's impossible on crz.gov.sk today.

### Long-term impact
- Full backfill of 5.5M contracts costs ~$380 via Batch API
- Daily incremental costs ~$12/month
- Becomes the missing "category" layer on top of CRZ

### Code sketch
```python
import xml.etree.ElementTree as ET
import anthropic, sqlite3

client = anthropic.Anthropic()

def classify(contract):
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{"role": "user", "content": f"""Classify this Slovak government contract.
Subject: {contract['predmet']}
Supplier: {contract['zs2']}
Buyer: {contract['zs1']}
Amount: {contract['suma']} EUR
Notes: {contract['poznamka']}

Categories: legal, consulting, IT, marketing, construction, healthcare,
education, transport, facilities, real_estate, financial, HR, grants, other

Return JSON: {{"category": "...", "confidence": 0.X, "reasoning": "..."}}"""}]
    )
    return resp.content[0].text
```

---

## Suggestion 2: "Supplier X-Ray" — Who Gets the Money?

**Build in a weekend. Impact: exposes supplier networks and concentration.**

### What it does
Aggregate all CRZ contracts by supplier ICO. For each supplier, show: total contract value, number of contracts, which institutions they work with, what categories of work they do, how they compare to peers.

### Why it matters
Right now, to see a company's full government contract history, you'd need to manually search CRZ by name. This tool builds a complete supplier profile from the XML exports.

### Weekend build
1. Parse XML exports → aggregate by supplier ICO
2. Enrich with ORSR (business register) data: NACE codes, establishment date, legal form
3. Flag anomalies:
   - New company (< 1 year old) with large contracts
   - Company NACE codes don't match contract categories (car repair shop winning IT consulting)
   - Single supplier dominates a ministry's spending
4. Simple dashboard showing top suppliers per ministry

### Hackathon demo
Enter a company ICO → see their full government contract history, total amounts, which ministries, anomaly flags.

### Long-term impact
- Foundation for investigative journalism: "This company was registered 3 months ago and already won €500K in contracts"
- Network analysis: shared addresses, shared directors between suppliers
- The NACE mismatch detection alone could surface stories

---

## Suggestion 3: "Contract Companion" — AI Agent for Journalists

**Build in a weekend. Impact: natural language access to public spending data.**

### What it does
A conversational AI agent (Claude) that can answer journalist questions about government contracts in Slovak. Backed by a database of classified CRZ contracts.

### Why it matters
Journalists don't want to write SQL queries or learn filter UIs. They want to ask: "Koľko ministerstvo vnútra zaplatilo za právne služby v roku 2025?" and get an answer.

### Weekend build
1. Ingest a subset of CRZ data (e.g., last 2 years) into SQLite/PostgreSQL
2. Run LLM classification (Suggestion 1)
3. Build Claude agent with tool-use: `search_contracts`, `get_supplier_profile`, `get_statistics`
4. Simple chat UI (Streamlit, or even a CLI)

### Hackathon demo
Live conversation with the agent:
- "Nájdi všetky zmluvy na marketing z Ministerstva pôdohospodárstva"
- "Kto je najväčší dodávateľ IT služieb pre vládu?"
- "Porovnaj výdavky na konzulting naprieč ministerstvami za posledné 3 roky"

### Long-term impact
- Democratizes access to public contract data
- Can be extended with anomaly alerts: "Agent, upozorni ma keď niektoré ministerstvo uzavrie zmluvu nad 100K€ s novým dodávateľom"

---

## Suggestion 4: "PDF Decoder" — Read What's Inside the Contracts

**Build in a weekend. Impact: unlocks the 70% of contracts that are opaque.**

### What it does
Download contract PDFs, extract text (pdftotext for digital, OCR for scans), and make the actual contract content searchable.

### Why it matters
CRZ only indexes metadata. The actual contract text — scope of work, payment terms, deliverables — is locked inside PDFs. ~30% are born-digital (instant text extraction), ~70% are scans (need OCR).

### Weekend build
1. Focus on born-digital PDFs only (no OCR needed — that's Phase 2)
2. Download PDFs for a target set (e.g., all contracts > €50K from last year)
3. Run `pdftotext` — if text comes out, index it
4. Use LLM to extract structured info: scope of work, payment terms, duration
5. Full-text search over contract content

### Hackathon demo
Search for "upratovanie" (cleaning) inside contract text — find all cleaning service contracts even when the metadata says "Zmluva o poskytovaní služieb".

### Long-term impact
- Full-text search across contract content (doesn't exist anywhere today)
- Combined with classification, gets accuracy from ~75% to ~95%
- Key clause extraction: payment terms, penalties, scope

### Rate limit note
CRZ rate limits: 1 req/2s daytime, 3 req/s nighttime. For a hackathon demo, downloading 100-500 PDFs is fine. Full backfill takes ~2 months.

---

## Suggestion 5: "Splitting Detector" — Find Contract Splitting

**Build in a weekend. Impact: detects a specific, common procurement fraud pattern.**

### What it does
Detect cases where a buyer splits a large purchase into multiple smaller contracts to avoid procurement thresholds (€50K for goods/services, €180K for construction).

### Why it matters
Contract splitting is one of the most common procurement fraud patterns. A ministry needs €120K of IT consulting, but instead of running a public tender, they sign three "Zmluvy o dielo" for €39K each with the same supplier.

### Weekend build
1. Parse CRZ XML exports
2. Group contracts by buyer+supplier pair within rolling time windows (e.g., 90 days)
3. Flag clusters where: same parties, multiple contracts, individual amounts just below threshold, total exceeds threshold
4. Rank by suspiciousness score
5. Simple results table with links to original CRZ contracts

### Hackathon demo
"Here are the top 50 most suspicious contract clusters that look like splitting — click through to verify."

### Long-term impact
- Automatable: run daily on new contracts, flag suspicious patterns
- Extensible: add more patterns (amendment inflation, concentration, revolving door)
- High journalistic value: each flagged cluster is a potential story

---

## Suggestion 6: "Ministry Budget Tracker" — Where Does the Money Go?

**Build in a weekend. Impact: a dashboard journalists can use daily.**

### What it does
For each ministry/institution, show a breakdown of spending by category over time. How much on legal, IT, marketing, construction? How does it compare to other ministries? How has it changed year over year?

### Why it matters
No such breakdown exists. CRZ shows individual contracts but no aggregate view. A journalist investigating Ministry X's spending has to manually add up contracts.

### Weekend build
1. Ingest CRZ data, classify contracts (Suggestion 1)
2. Aggregate: SUM(amount) GROUP BY rezort, category, year
3. Build a dashboard: bar charts by category, line charts over time, comparison across ministries
4. Drill-down: click a category → see individual contracts

### Hackathon demo
Side-by-side: Ministry of Interior vs. Ministry of Agriculture spending on marketing, legal, IT — with year-over-year trends.

### Long-term impact
- Journalists can monitor spending patterns over time
- Anomaly detection: "Marketing spending at Ministry X tripled in Q4 2025"
- Public accountability dashboard

---

## What to Build This Weekend — Recommendation

**If you're one team**: Combine Suggestions 1 + 3 + 6. Classify contracts → build agent + dashboard. This is the highest-impact combo and tells a complete story for the hackathon judges.

**If you want to split into sub-teams**:
- Team A: Data pipeline + classification (Suggestion 1)
- Team B: Agent interface (Suggestion 3) — uses Team A's data
- Team C: Anomaly detection (Suggestion 5) — uses Team A's data

**Quickest path to demo**: Suggestion 1 alone. Download XML, classify with LLM, show filtered results. Can be demoed in 4 hours.

---

## Technical Quick-Start

```bash
# Download yesterday's contracts
curl -o contracts.zip https://www.crz.gov.sk/export/2026-03-05.zip
unzip contracts.zip

# Parse and explore
python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('2026-03-05.xml')
root = tree.getroot()
print(f'{len(root)} contracts')
for z in root[:5]:
    print(f\"  {z.find('predmet').text} | {z.find('zs2').text} | {z.find('suma_zmluva').text} EUR\")
"
```

**Key fields for classification**: `predmet` (subject), `zs2` (supplier), `zs1` (buyer), `suma_zmluva` (amount), `poznamka` (notes — 6% populated but high signal).

**Attachment download**: `https://www.crz.gov.sk/data/att/{dokument1_value}` — check both `dokument` and `dokument1` fields in XML (50/50 split between old and new storage).

**Rate limits**: Be respectful. 1 request per 2 seconds daytime. The daily XML export has no rate limit (it's a single file download).
