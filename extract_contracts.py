"""Extract structured data from CRZ contract text files using LLM.

Uses OpenRouter API (OpenAI-compatible) to classify and extract
key fields from Slovak government contract PDFs.

Usage:
    python extract_contracts.py                    # extract all unprocessed texts
    python extract_contracts.py --limit 10         # extract 10 contracts
    python extract_contracts.py --file 6578512.txt # extract one specific file
    python extract_contracts.py --dry-run          # show what would be processed
"""
import json
import os
import sys
import csv
import time
import argparse
import sqlite_utils
import httpx


OPENROUTER_BASE = "https://openrouter.ai/api/v1"
MODEL = "google/gemini-2.5-flash-lite"

SYSTEM_PROMPT = """You are a structured data extractor for Slovak government contracts from the Central Register of Contracts (CRZ). You receive the text of a contract and extract key fields.

Respond ONLY with valid JSON matching this schema — no markdown, no explanation:

{
  "service_category": one of: "construction_renovation", "software_it", "cultural_event_production", "utilities", "insurance", "professional_consulting", "media_marketing", "grant_subsidy", "property_lease", "cemetery", "asset_transfer", "employment_social", "legal_services", "cleaning_facility", "digital_certification", "hr_payroll_outsourcing", "pharmaceutical_clinical", "other",
  "actual_subject": short description of what the contract is actually about (1-2 sentences, in Slovak),
  "hidden_entities": [{"name": "...", "ico": "...", "role": one of "authorized_representative", "manager_operator", "previous_operator", "co_user", "consortium_member", "subcontractor", "associated_entity"}],
  "penalties": [{"payer": "supplier" or "buyer", "trigger": "...", "amount": "..."}],
  "penalty_asymmetry": one of "strong_buyer_advantage", "moderate_buyer_advantage", "balanced", "supplier_advantage", "none_found",
  "termination": {"buyer_can_terminate_without_cause": bool, "supplier_can_terminate_without_cause": bool, "notice_period": "..." or null},
  "funding_source": {"type": one of "eu_recovery_plan", "eu_structural_funds", "erasmus", "de_minimis", "state_budget", "municipal_budget", "other_eu", "none" , "scheme_reference": "..." or null, "grant_amount": number or null},
  "bank_accounts": [{"party": "supplier" or "buyer", "iban": "SK..."}],
  "auto_renewal": bool,
  "bezodplatne": bool
}

Rules:
- hidden_entities: only include entities NOT already the two main contracting parties. Look for IČO numbers paired with org names that appear as subcontractors, consortium members, authorized representatives, managers, etc.
- penalties: extract only explicit contractual penalties (zmluvná pokuta, úroky z omeškania with specific rates). Skip generic legal references.
- bank_accounts: extract IBAN numbers (SK format).
- If a field has no data, use empty array [] for arrays, null for optional strings/numbers, false for booleans, "none_found" or "none" for enums.
- Keep actual_subject concise but specific — it should disambiguate generic titles like "Zmluva o dielo"."""

USER_PROMPT_TEMPLATE = """Extract structured data from this Slovak government contract text.

Contract text:
---
{text}
---"""


def load_api_key():
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        key_file = os.path.join(os.path.dirname(__file__), ".openrouter_key")
        if os.path.exists(key_file):
            key = open(key_file).read().strip()
    if not key:
        print("Error: Set OPENROUTER_API_KEY env var or create .openrouter_key file")
        sys.exit(1)
    return key


import re

# Section headers that signal high-value content for extraction
SECTION_PATTERNS = [
    r'(?i)zmluvn[áé]\s*pokut',      # penalties
    r'(?i)sankci[eí]',               # sanctions
    r'(?i)úrok.*z\s*omeškani',       # late payment interest
    r'(?i)odstúpeni[ea]',            # withdrawal
    r'(?i)výpoveď|ukončeni[ea]',     # termination
    r'(?i)subdodávate',              # subcontractor
    r'(?i)konzorci',                 # consortium
    r'(?i)IBAN|SK\d{2}\s?\d{4}',    # bank accounts
    r'(?i)de\s*minimis|štátna\s*pomoc',  # state aid
    r'(?i)plán\s*obnovy|mechanizm',  # recovery plan
]


def smart_truncate(text, max_total=12000):
    """Extract head + key middle sections + tail from long contract text."""
    if len(text) <= max_total:
        return text

    head_size = 4000
    tail_size = 3000
    middle_budget = max_total - head_size - tail_size

    head = text[:head_size]
    tail = text[-tail_size:]

    # Find key sections in the middle
    middle = text[head_size:-tail_size]
    snippets = []
    for pattern in SECTION_PATTERNS:
        for m in re.finditer(pattern, middle):
            # Grab 400 chars around each match
            start = max(0, m.start() - 200)
            end = min(len(middle), m.end() + 200)
            snippets.append((start, middle[start:end]))

    # Deduplicate overlapping snippets, keep unique
    snippets.sort(key=lambda x: x[0])
    merged = []
    for pos, snip in snippets:
        if merged and pos < merged[-1][0] + len(merged[-1][1]):
            # Overlapping — extend previous
            prev_pos, prev_snip = merged[-1]
            new_end = max(prev_pos + len(prev_snip), pos + len(snip))
            merged[-1] = (prev_pos, middle[prev_pos:new_end])
        else:
            merged.append((pos, snip))

    # Collect middle text within budget
    middle_parts = []
    budget_left = middle_budget
    for _, snip in merged:
        if budget_left <= 0:
            break
        chunk = snip[:budget_left]
        middle_parts.append(chunk)
        budget_left -= len(chunk)

    if middle_parts:
        middle_text = "\n[...]\n".join(middle_parts)
        return head + "\n\n[...contract middle — key sections...]\n\n" + middle_text + "\n\n[...]\n\n" + tail
    else:
        return head + "\n\n[...middle omitted...]\n\n" + tail


def extract_one(client, api_key, text, model=MODEL):
    """Send text to LLM and return parsed JSON extraction."""
    # Smart truncation: head (parties/subject) + key middle sections + tail (signatures)
    truncated = smart_truncate(text, max_total=12000)

    resp = client.post(
        f"{OPENROUTER_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=truncated)},
            ],
            "temperature": 0.0,
            "max_tokens": 2000,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    # Strip markdown fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]
    content = content.strip()

    usage = data.get("usage", {})
    return json.loads(content), usage


def get_manifest(texts_dir):
    """Load manifest mapping text files to contract metadata."""
    manifest_path = os.path.join(texts_dir, "manifest.csv")
    if not os.path.exists(manifest_path):
        return {}
    mapping = {}
    with open(manifest_path) as f:
        for row in csv.DictReader(f):
            mapping[row["txt_file"]] = row
    return mapping


def main():
    parser = argparse.ArgumentParser(description="Extract structured data from CRZ contract texts")
    parser.add_argument("--limit", type=int, default=0, help="Max contracts to process (0=all)")
    parser.add_argument("--file", type=str, help="Process a single text file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    parser.add_argument("--model", type=str, default=MODEL, help=f"OpenRouter model (default: {MODEL})")
    parser.add_argument("--texts-dir", type=str, default="data/texts", help="Directory with text files")
    parser.add_argument("--output-dir", type=str, default="data/extractions", help="Directory for JSON outputs")
    args = parser.parse_args()

    api_key = load_api_key()
    texts_dir = args.texts_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Determine which files to process
    if args.file:
        files = [args.file]
    else:
        files = sorted(f for f in os.listdir(texts_dir) if f.endswith(".txt"))

    # Skip already-extracted files
    already_done = set(f.replace(".json", ".txt") for f in os.listdir(output_dir) if f.endswith(".json"))
    to_process = [f for f in files if f not in already_done]

    if args.limit > 0:
        to_process = to_process[:args.limit]

    print(f"Text files: {len(files)}, already extracted: {len(already_done)}, to process: {len(to_process)}")

    if args.dry_run:
        for f in to_process[:20]:
            print(f"  would process: {f}")
        if len(to_process) > 20:
            print(f"  ... and {len(to_process) - 20} more")
        return

    if not to_process:
        print("Nothing to process.")
        return

    # Load manifest for metadata
    manifest = get_manifest(texts_dir)

    # Set up DB for storing extractions
    db = sqlite_utils.Database("crz.db")

    total_tokens = 0
    ok, fail = 0, 0

    with httpx.Client(timeout=60) as client:
        for i, fname in enumerate(to_process):
            txt_path = os.path.join(texts_dir, fname)
            if not os.path.exists(txt_path):
                print(f"  [{i+1}/{len(to_process)}] SKIP {fname} (file not found)")
                continue

            text = open(txt_path).read()
            if len(text.strip()) < 50:
                print(f"  [{i+1}/{len(to_process)}] SKIP {fname} (too short, likely OCR failure)")
                continue

            try:
                extraction, usage = extract_one(client, api_key, text, model=args.model)
                tokens = usage.get("total_tokens", 0)
                total_tokens += tokens

                # Add metadata
                meta = manifest.get(fname, {})
                extraction["_source_file"] = fname
                extraction["_zmluva_id"] = meta.get("zmluva_id", fname.replace(".txt", ""))
                extraction["_model"] = args.model

                # Save JSON
                out_path = os.path.join(output_dir, fname.replace(".txt", ".json"))
                with open(out_path, "w") as f:
                    json.dump(extraction, f, ensure_ascii=False, indent=2)

                # Upsert into DB
                zmluva_id = extraction["_zmluva_id"]
                db_row = {
                    "zmluva_id": int(zmluva_id) if str(zmluva_id).isdigit() else zmluva_id,
                    "service_category": extraction.get("service_category"),
                    "actual_subject": extraction.get("actual_subject"),
                    "penalty_asymmetry": extraction.get("penalty_asymmetry"),
                    "auto_renewal": extraction.get("auto_renewal", False),
                    "bezodplatne": extraction.get("bezodplatne", False),
                    "funding_type": extraction.get("funding_source", {}).get("type"),
                    "grant_amount": extraction.get("funding_source", {}).get("grant_amount"),
                    "hidden_entity_count": len(extraction.get("hidden_entities", [])),
                    "penalty_count": len(extraction.get("penalties", [])),
                    "iban_count": len(extraction.get("bank_accounts", [])),
                    "extraction_json": json.dumps(extraction, ensure_ascii=False),
                    "model": args.model,
                }
                db["extractions"].insert(db_row, pk="zmluva_id", replace=True)

                cat = extraction.get("service_category", "?")
                subj = (extraction.get("actual_subject") or "")[:60]
                print(f"  [{i+1}/{len(to_process)}] {fname} -> {cat} | {subj} ({tokens} tok)")
                ok += 1

            except json.JSONDecodeError as e:
                print(f"  [{i+1}/{len(to_process)}] FAIL {fname}: bad JSON: {e}")
                fail += 1
            except httpx.HTTPStatusError as e:
                print(f"  [{i+1}/{len(to_process)}] FAIL {fname}: HTTP {e.response.status_code}")
                fail += 1
                if e.response.status_code == 429:
                    print("    Rate limited, waiting 10s...")
                    time.sleep(10)
            except Exception as e:
                print(f"  [{i+1}/{len(to_process)}] FAIL {fname}: {e}")
                fail += 1

            # Small delay to avoid rate limits
            if (i + 1) % 20 == 0:
                time.sleep(1)

    print(f"\nDone: {ok} extracted, {fail} failed, {total_tokens} total tokens")
    print(f"Extractions in {output_dir}/ and crz.db:extractions table")


if __name__ == "__main__":
    main()
