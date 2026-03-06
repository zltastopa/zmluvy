# CRZ Hackathon Suggestions — Final Version

**For**: Open Data Heroes Hackathon (March 7-8, 2026, The Spot, Bratislava)
**Challenge by**: 360ka | 360tka.sk (Michal, Barbora)
**Core need**: Intelligent search and classification of 5.5M+ Slovak government contracts

---

## Data Access — Three Options (Pick One)

| Method | URL | Format | Best for |
|--------|-----|--------|----------|
| **Daily XML exports** (official) | `https://www.crz.gov.sk/export/YYYY-MM-DD.zip` | ZIP → XML | Bulk historical data, no auth |
| **Ekosystem JSON API** (community) | `https://datahub.ekosystem.slovensko.digital/api/data/crz/contracts/sync?since=2026-01-01T00:00:00Z` | JSON | Real-time access, clean structured data, 60 req/min |
| **RSS feed** | `https://www.crz.gov.sk/data/static/rss.xml` | RSS 2.0 | Monitoring new publications |

The **Ekosystem API** by slovensko.digital is a game-changer for the hackathon — it gives you clean JSON with no XML parsing needed:

```bash
# Get contracts changed since a date (paginated, 100 per page)
curl "https://datahub.ekosystem.slovensko.digital/api/data/crz/contracts/sync?since=2026-03-01T00:00:00Z"

# Get a single contract by ID
curl "https://datahub.ekosystem.slovensko.digital/api/data/crz/contracts/12075397"
```

JSON fields include: `subject`, `supplier_name`, `supplier_cin`, `contracting_authority_name`, `contract_price_amount`, `published_at`, `attachments[]`, and more. No auth needed. 60 requests/minute rate limit.

**Recommendation**: Use the Ekosystem API for rapid prototyping during the hackathon. Use daily XML exports for bulk historical analysis (pre-download Friday night).

---

## Pre-Hackathon Checklist (Do This Friday Night!)

```bash
# 1. Download 6 months of CRZ daily XML exports (~180 files, ~70MB total)
mkdir -p data && cd data
for i in $(seq 0 180); do
  date=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "-${i} days" +%Y-%m-%d)
  curl -s -o "${date}.zip" "https://www.crz.gov.sk/export/${date}.zip"
  sleep 0.5
done
# Unzip all
for f in *.zip; do unzip -o "$f" 2>/dev/null; done

# 2. Install dependencies
pip install anthropic streamlit pandas lxml

# 3. Set up Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 4. Optional: submit Batch API classification job Friday night
#    Results ready Saturday morning (24h turnaround, 50% cheaper)
```

**Have a backup**: If CRZ is down, you can still work with already-downloaded XML files.

---

## Data Quality Cheat Sheet

Know this before writing any code:

| Gotcha | What you'll see | How to handle |
|--------|----------------|---------------|
| `suma_zmluva = 0` | 40% of contracts | Means "unknown", NOT free. Use `None`/`NULL`. |
| Empty `ico` (supplier) | 26% of contracts | Natural persons or foreign entities. Skip for ICO-based analysis. |
| `datum_platnost_do = 0000-00-00` | 70% of contracts | Means "indefinite". Convert to `None`. |
| Dual attachment fields | 50/50 split | Check BOTH `dokument` AND `dokument1` — only one is populated per attachment. |
| `predmet` is generic | Very common | "Zmluva o dielo" = anything. This is THE problem we're solving. |
| XML field access | `element.find('X')` can return `None` | Always use safe access (see code below). |

```python
def get_text(el, tag, default=''):
    """Safe XML text extraction — prevents NoneType crashes."""
    node = el.find(tag)
    return node.text.strip() if node is not None and node.text else default

def get_amount(el, tag):
    """Parse amount, treating 0 as None (unknown)."""
    val = get_text(el, tag, '0')
    try:
        amount = float(val)
        return amount if amount > 0 else None
    except ValueError:
        return None
```

---

## The 7 Suggestions

### Suggestion 1: "CRZ Classifier" — LLM Contract Categorization

**Effort**: 4-6 hours | **Impact**: Foundational — everything else builds on this

Classify each contract by service type (legal, IT, marketing, construction, consulting...) using LLM on metadata alone.

**Build**:
1. Parse XML exports → list of contract dicts
2. Classify with Claude Haiku (~$0.00014/contract = under $1 for 5,000 contracts)
3. Store in SQLite with category columns
4. Streamlit UI: filter by category, institution, supplier, amount, date
5. Every result links to `https://www.crz.gov.sk/zmluva/{id}/` for verification

**Demo**: "Show me all marketing contracts from Ministry of Agriculture over €10,000" — impossible on CRZ today, instant with our tool.

**Tips**:
- Pre-classify Friday night using Batch API (50% cheaper, results Saturday morning)
- Or use `asyncio` + `anthropic.AsyncAnthropic` to parallelize during hackathon
- Include `poznamka` (notes field, 6% populated) in prompt — it has high classification signal
- Use at least 3-6 months of data for a meaningful demo

---

### Suggestion 2: "Amendment Tracker" — Follow the Money Through Contract Changes

**Effort**: 3-4 hours | **Impact**: Very high — surfaces a common fraud pattern

Find contracts where the final amount (`suma_spolu`) is dramatically higher than the original (`suma_zmluva`), indicating repeated amendments that bypass procurement thresholds.

**Why this matters**: A ministry signs a contract for €45K (just under the €50K tender threshold). Then adds €20K. Then another €30K. Final: €95K — nearly double, no public tender.

**Build**:
1. Parse XML exports
2. Compute `inflation_ratio = suma_spolu / suma_zmluva` for each contract
3. Filter: `inflation_ratio > 2.0` AND `suma_spolu > 50000`
4. Link amendments to parent contracts via the `ref` field (2.3% populated) and `typ=2` (amendment) flag
5. Rank by inflation ratio, display in table with CRZ links

**Demo**: "Here are the top 20 contracts where the final amount is 3x+ the original value. This one started at €40K and ended at €340K with no new tender."

**No LLM needed** — pure data analysis. Pairs perfectly with Suggestion 1.

```python
# Core logic
for contract in contracts:
    original = get_amount(contract, 'suma_zmluva')
    total = get_amount(contract, 'suma_spolu')
    if original and total and original > 0 and total > original * 2:
        inflation = total / original
        results.append({
            'id': get_text(contract, 'ID'),
            'subject': get_text(contract, 'predmet'),
            'buyer': get_text(contract, 'zs1'),
            'supplier': get_text(contract, 'zs2'),
            'original': original,
            'final': total,
            'inflation_ratio': round(inflation, 1),
            'crz_link': f"https://www.crz.gov.sk/zmluva/{get_text(contract, 'ID')}/"
        })
```

---

### Suggestion 3: "Splitting Detector" — Find Contract Splitting

**Effort**: 4-6 hours | **Impact**: High — detects a specific procurement fraud pattern

Detect cases where a buyer splits a large purchase into multiple smaller contracts to avoid procurement thresholds.

**Build**:
1. Parse XML exports (need 6+ months of data for meaningful results)
2. Group contracts by buyer_ico + supplier_ico within 90-day windows
3. Flag clusters where: individual amounts < €50K, but combined total > €50K
4. Score by: number of contracts, total amount, time clustering
5. Results table with drill-down to individual contracts

**Demo**: "Here are 47 suspicious clusters. This ministry signed 4 contracts with the same IT company in 2 months, each for €48K. Total: €192K with no public tender."

**Tips**:
- Expect false positives (recurring service contracts). Consult with 360ka journalists during hackathon to filter
- Current Slovak thresholds: ~€50K goods/services, ~€180K construction (verify with UVO)

---

### Suggestion 4: "Supplier X-Ray" — Who Gets the Money?

**Effort**: 6-8 hours | **Impact**: High for investigative journalism

Build supplier profiles from CRZ data: total contract value, which institutions, what categories, anomaly flags.

**Build**:
1. Aggregate contracts by supplier ICO (skip the 26% with no ICO)
2. For each supplier: count contracts, sum amounts, list institutions
3. Flag anomalies: new companies with big contracts, companies spanning many unrelated ministries
4. Optional stretch: ORSR enrichment for NACE codes (if API available)

**Demo**: Enter company ICO → see full government contract history, total amounts, institutional spread, red flags.

---

### Suggestion 5: "PDF Decoder" — Search Inside Contracts

**Effort**: 6-10 hours | **Impact**: Medium-high (long-term transformative)

Extract text from contract PDFs and make content searchable.

**Build**:
1. Download PDFs for target set (start Friday night! Rate limit: 1 req/2s)
2. Run `pdftotext` — if >100 chars, it's born-digital (~30% of PDFs)
3. Index extracted text in SQLite FTS
4. Keyword search across contract content

**Demo**: Search "upratovanie" (cleaning) → find cleaning contracts hidden as generic "Zmluva o poskytovaní služieb".

**Critical**: Pre-download PDFs before the hackathon. At 1 req/2s, you get ~1,800/hour.

---

### Suggestion 6: "Ministry Budget Tracker" — Spending Dashboard

**Effort**: 4-6 hours (on top of Suggestion 1) | **Impact**: Medium

Visualize spending by category per ministry, with year-over-year trends.

**Build**: Aggregation + charts on top of classified data from Suggestion 1. Use Streamlit + Plotly.

**Demo**: Side-by-side comparison of Ministry of Interior vs. Ministry of Agriculture spending on marketing, legal, IT.

**Best as an extension of S1**, not standalone.

---

### Suggestion 7: "Contract Companion" — AI Agent for Journalists

**Effort**: 8-14 hours | **Impact**: Medium (impressive demo, limited practical value today)

Conversational AI that answers journalist queries about contracts in Slovak.

**Build**: Claude Sonnet with tool-use → queries the classified contract database.

**WARNING — HIGH RISK for hackathon demo**:
- Agent hallucination in front of investigative journalists = credibility disaster
- Multi-step tool use adds 10-20 second latency per query
- If you build this, have 3-5 pre-tested "golden path" queries. Never demo cold.

---

## Recommended Combinations

### Best for ONE team (highest impact, lowest risk):

**S1 (Classifier) + S2 (Amendment Tracker)**

- Saturday morning: Parse XML, build classification pipeline
- Saturday afternoon: Run classification, build amendment analysis
- Sunday morning: Build Streamlit UI with both features
- Sunday afternoon: Polish, find concrete investigative findings for demo

**Demo story**: "We classified 100,000 contracts so you can search by category. And we found 35 contracts where the final amount is 5x the original — here are the most suspicious ones." [Click through to CRZ to verify]

### If you have sub-teams:

| Team | Suggestion | Dependency |
|------|-----------|------------|
| A (backend) | S1: Data pipeline + classification | None |
| B (analysis) | S2 + S3: Amendment tracker + splitting detector | Uses Team A's data |
| C (frontend) | S6: Dashboard + search UI | Uses Team A's data |

### Strongest demo formula:

1. Open with a question CRZ can't answer today
2. Show the answer in your tool (< 2 seconds)
3. Reveal a concrete investigative finding (amendment inflation, splitting)
4. Click through to the official CRZ page to verify
5. "This runs daily — it can alert you about new suspicious patterns"

---

## Technical Quick-Start

```python
import xml.etree.ElementTree as ET

def get_text(el, tag, default=''):
    node = el.find(tag)
    return node.text.strip() if node is not None and node.text else default

def get_amount(el, tag):
    val = get_text(el, tag, '0')
    try:
        a = float(val)
        return a if a > 0 else None
    except ValueError:
        return None

def get_attachment(priloha):
    """Handle dual storage fields — check both."""
    for field in ['dokument1', 'dokument']:
        name = get_text(priloha, field)
        if name:
            return name, f"https://www.crz.gov.sk/data/att/{name}"
    return None, None

def parse_export(xml_path):
    tree = ET.parse(xml_path)
    contracts = []
    for z in tree.getroot():
        contracts.append({
            'id': get_text(z, 'ID'),
            'subject': get_text(z, 'predmet'),
            'buyer': get_text(z, 'zs1'),
            'buyer_ico': get_text(z, 'ico1'),
            'supplier': get_text(z, 'zs2'),
            'supplier_ico': get_text(z, 'ico'),
            'amount': get_amount(z, 'suma_zmluva'),
            'total_amount': get_amount(z, 'suma_spolu'),
            'notes': get_text(z, 'poznamka'),
            'date_published': get_text(z, 'datum_zverejnene'),
            'contract_type': get_text(z, 'typ'),  # 1=contract, 2=amendment
            'parent_ref': get_text(z, 'ref'),
            'crz_link': f"https://www.crz.gov.sk/zmluva/{get_text(z, 'ID')}/",
        })
    return contracts
```

**Classification call** (async for speed):

```python
import anthropic, asyncio, json

client = anthropic.AsyncAnthropic()

async def classify(contract, semaphore):
    async with semaphore:  # Rate limiting
        resp = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{"role": "user", "content": f"""Classify this Slovak government contract.
Subject: {contract['subject']}
Supplier: {contract['supplier']}
Buyer: {contract['buyer']}
Amount: {contract['amount'] or 'unknown'} EUR
Notes: {contract['notes']}

Categories: legal, consulting, IT, marketing, construction, healthcare,
education, transport, facilities, real_estate, financial, HR, grants, other

Return JSON only: {{"category": "...", "subcategory": "...", "confidence": 0.X, "reasoning": "..."}}"""}]
        )
        try:
            return json.loads(resp.content[0].text)
        except json.JSONDecodeError:
            return {"category": "other", "confidence": 0.0, "reasoning": "parse_error"}

async def classify_batch(contracts, max_concurrent=10):
    sem = asyncio.Semaphore(max_concurrent)
    tasks = [classify(c, sem) for c in contracts]
    return await asyncio.gather(*tasks)
```

---

## Alternative: Quick-Start with Ekosystem JSON API

If you don't want to parse XML at all, use the slovensko.digital API directly:

```python
import requests, time

def fetch_contracts(since="2026-01-01T00:00:00Z", max_pages=10):
    """Fetch contracts from Ekosystem API (JSON, no XML parsing)."""
    contracts = []
    last_id = None
    for _ in range(max_pages):
        url = f"https://datahub.ekosystem.slovensko.digital/api/data/crz/contracts/sync?since={since}"
        if last_id:
            url += f"&last_id={last_id}"
        resp = requests.get(url)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        contracts.extend(batch)
        last_id = batch[-1]['id']
        time.sleep(1)  # Respect 60 req/min limit
    return contracts

# Fetch recent contracts
contracts = fetch_contracts(since="2026-01-01T00:00:00Z", max_pages=50)
print(f"Fetched {len(contracts)} contracts")
# Each has: subject, supplier_name, supplier_cin, contracting_authority_name,
#           contract_price_amount, published_at, attachments, etc.
```

---

## Cost Reference

| What | Cost | Notes |
|------|------|-------|
| Classify 1,000 contracts (Haiku) | ~$0.14 | Hackathon budget: trivial |
| Classify 100,000 contracts (Haiku, Batch API) | ~$7 | Good demo dataset |
| Classify 5.5M contracts (Haiku, Batch API) | ~$380 | Full backfill |
| Agent query (Sonnet) | ~$0.045 | Per conversation turn |
| Daily incremental classification | ~$0.39/day | ~$12/month |

---

## Files in This Repo

| File | What |
|------|------|
| `docs/plans/2026-03-06-crz-smart-contracts-design-v2.md` | Full technical design (architecture, schema, costs) |
| `docs/plans/2026-03-06-crz-design-review.md` | Review of v1 design |
| `docs/plans/2026-03-06-crz-design-v2-review.md` | Review of v2 design |
| `docs/plans/2026-03-06-hackathon-suggestions-review.md` | Review of hackathon suggestions |
| `tmp/2026-03-04.xml` | Sample daily XML export (2,794 contracts) |
| `tmp/*.png` | Screenshots of CRZ website |
