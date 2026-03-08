"""Experiment: extract parent contract references from amendment texts
and try matching them to contracts in the database.

Uses a simple LLM call to extract the parent contract number from each
amendment text, then attempts to match it against cislo_zmluvy in zmluvy.

Finds amendment texts via the manifest.csv mapping and prilohy attachment IDs.
"""
import confpath  # noqa: F401

import json
import os
import re
import csv
import sqlite3
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
from tqdm import tqdm

from settings import get_env, get_path
from openrouter_utils import OPENROUTER_BASE, load_openrouter_api_key

MODEL = get_env("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")

EXTRACT_PARENT_PROMPT = """You are given the text of a Slovak government contract amendment (dodatok).
Your job is to find the reference to the PARENT contract that this amendment modifies.

Return ONLY valid JSON with these fields:
{
  "parent_contract_number": "the contract number/reference of the original contract this amends (e.g. '2022-0178-1180530', '20242555'), or null if not found",
  "amendment_number": integer (which amendment is this - 1, 2, 3... or null if unclear),
  "parent_title": "short title/subject of the parent contract if mentioned (e.g. 'Zmluva o dielo'), or null",
  "confidence": "high" or "medium" or "low"
}

Look for patterns like:
- "Dodatok č. X k Zmluve č. YYYY"
- "Dodatok č. X k Zmluve o dielo č. YYYY"
- "k zmluve číslo YYYY"
- Contract number headers at the top of the document (e.g. "číslo zmluvy objednávateľa: YYYY")
- Any reference to an original/parent contract number

Important:
- Do NOT confuse the amendment's own number with the parent contract number.
- The parent contract number is the number of the ORIGINAL contract being amended, not the dodatok number.
- If the text is clearly garbled OCR with unreadable characters, try your best but set confidence to "low".
- Return ONLY JSON, no markdown."""


def extract_parent_ref(client, api_key, text, model=MODEL):
    """Ask LLM to extract parent contract reference from amendment text."""
    # Use first 4000 chars - parent ref is almost always in the header
    truncated = text[:4000]

    resp = client.post(
        f"{OPENROUTER_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": EXTRACT_PARENT_PROMPT},
                {"role": "user", "content": f"Amendment text:\n---\n{truncated}\n---"},
            ],
            "temperature": 0.0,
            "max_tokens": 500,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]
    return json.loads(content.strip())


def try_match_parent(db, parent_number, amendment_row):
    """Try to find the parent contract in the DB by cislo_zmluvy match.

    Excludes self-matches and prefers typ='zmluva' parents.
    """
    if not parent_number:
        return None, "no_parent_number"

    amendment_id = amendment_row["id"]

    # Exact match on cislo_zmluvy, excluding the amendment itself
    matches = db.execute(
        "SELECT id, cislo_zmluvy, nazov_zmluvy, typ, dodavatel_ico, objednavatel_ico "
        "FROM zmluvy WHERE cislo_zmluvy = ? AND id != ?",
        [parent_number, amendment_id],
    ).fetchall()

    # Prefer zmluva over dodatok matches
    zmluva_matches = [m for m in matches if m[3] == "zmluva"]
    if zmluva_matches:
        matches = zmluva_matches

    if len(matches) == 1:
        return matches[0], "exact_unique"

    if len(matches) > 1:
        # Disambiguate by matching ICOs
        a_dico = amendment_row["dodavatel_ico"] or ""
        a_oico = amendment_row["objednavatel_ico"] or ""
        ico_matches = [
            m for m in matches
            if (m[4] == a_dico and len(a_dico) > 2) or (m[5] == a_oico and len(a_oico) > 2)
        ]
        if len(ico_matches) == 1:
            return ico_matches[0], "exact_ico_disambig"
        if len(ico_matches) > 1:
            # Among ICO matches, prefer zmluva type
            zmluva_ico = [m for m in ico_matches if m[3] == "zmluva"]
            if len(zmluva_ico) == 1:
                return zmluva_ico[0], "exact_ico_typ_disambig"
            return ico_matches[0], f"exact_ico_multi({len(ico_matches)})"
        return None, f"exact_ambiguous({len(matches)})"

    # Try LIKE match (parent_number might be a substring)
    if len(parent_number) >= 6:  # avoid overly broad LIKE matches
        matches = db.execute(
            "SELECT id, cislo_zmluvy, nazov_zmluvy, typ, dodavatel_ico, objednavatel_ico "
            "FROM zmluvy WHERE cislo_zmluvy LIKE ? AND id != ?",
            [f"%{parent_number}%", amendment_id],
        ).fetchall()

        zmluva_matches = [m for m in matches if m[3] == "zmluva"]
        if zmluva_matches:
            matches = zmluva_matches

        if len(matches) == 1:
            return matches[0], "like_unique"
        if len(matches) > 1:
            a_dico = amendment_row["dodavatel_ico"] or ""
            a_oico = amendment_row["objednavatel_ico"] or ""
            ico_matches = [
                m for m in matches
                if (m[4] == a_dico and len(a_dico) > 2) or (m[5] == a_oico and len(a_oico) > 2)
            ]
            if len(ico_matches) == 1:
                return ico_matches[0], "like_ico_disambig"
            if ico_matches:
                return ico_matches[0], f"like_ico_multi({len(ico_matches)})"
            return None, f"like_ambiguous({len(matches)})"

    return None, "no_match"


def find_amendment_texts(db, texts_dir):
    """Find all amendments that have text files, via manifest or attachment IDs."""
    # Load manifest: maps txt_file -> metadata (including zmluva_id)
    manifest = {}
    manifest_path = os.path.join(texts_dir, "manifest.csv")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            for row in csv.DictReader(f):
                manifest[row.get("zmluva_id", "")] = row

    # Build a set of available text file stems
    available_texts = {f[:-4] for f in os.listdir(texts_dir) if f.endswith(".txt")}

    # Get all amendments
    amendments = db.execute("""
        SELECT z.id, z.cislo_zmluvy, z.nazov_zmluvy, z.typ,
               z.dodavatel_ico, z.objednavatel_ico, z.dodavatel, z.objednavatel
        FROM zmluvy z
        WHERE z.typ = 'dodatok'
    """).fetchall()

    processable = []
    for a in amendments:
        aid = str(a["id"])
        text_file = None

        # Method 1: check manifest by zmluva_id
        if aid in manifest:
            txt = manifest[aid].get("txt_file", "")
            if txt and txt[:-4] in available_texts:
                text_file = txt

        # Method 2: check attachment IDs
        if not text_file:
            attachments = db.execute(
                "SELECT id FROM prilohy WHERE zmluva_id = ?", [a["id"]]
            ).fetchall()
            for att in attachments:
                att_stem = str(att[0])
                if att_stem in available_texts:
                    text_file = att_stem + ".txt"
                    break

        if text_file:
            processable.append((a, text_file))

    return processable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Max amendments to process")
    parser.add_argument("--model", type=str, default=MODEL)
    parser.add_argument("--workers", type=int, default=8, help="Parallel workers")
    parser.add_argument("--dry-run", action="store_true", help="Just show which texts we'd process")
    args = parser.parse_args()

    api_key = load_openrouter_api_key()
    db = sqlite3.connect(get_path("CRZ_DB_PATH", "crz.db"))
    db.row_factory = sqlite3.Row
    texts_dir = get_path("CRZ_TEXT_DIR", "data/texts")

    processable = find_amendment_texts(db, texts_dir)
    print(f"Total amendments: {db.execute('SELECT COUNT(*) FROM zmluvy WHERE typ=\"dodatok\"').fetchone()[0]}")
    print(f"With text files available: {len(processable)}")

    if args.limit:
        processable = processable[: args.limit]

    if args.dry_run:
        for a, tf in processable:
            print(f"  {a['id']} | {tf} | {a['cislo_zmluvy']} | {a['nazov_zmluvy'][:50]}")
        return

    if not processable:
        print("Nothing to process.")
        return

    stats = {
        "extracted": 0,
        "matched_real": 0,
        "matched_self": 0,
        "no_parent": 0,
        "no_match_in_db": 0,
        "error": 0,
    }
    results = []

    def process_one(amendment_row, text_file, client):
        text = open(os.path.join(texts_dir, text_file)).read()
        ref = extract_parent_ref(client, api_key, text, model=args.model)
        return ref

    pbar = tqdm(total=len(processable), desc="Extracting parent refs", unit="doc")

    with httpx.Client(timeout=30) as client:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {}
            for a, tf in processable:
                fut = pool.submit(process_one, a, tf, client)
                futures[fut] = (a, tf)

            for future in as_completed(futures):
                a, tf = futures[future]
                pbar.update(1)

                try:
                    ref = future.result()
                    stats["extracted"] += 1
                except Exception as e:
                    pbar.write(f"  ERROR {a['id']}: {e}")
                    stats["error"] += 1
                    continue

                parent_number = ref.get("parent_contract_number")
                match, match_type = try_match_parent(db, parent_number, a)

                is_self = match and match[0] == a["id"]

                result = {
                    "amendment_id": a["id"],
                    "amendment_cislo": a["cislo_zmluvy"],
                    "amendment_nazov": a["nazov_zmluvy"],
                    "dodavatel_ico": a["dodavatel_ico"],
                    "objednavatel_ico": a["objednavatel_ico"],
                    "text_file": tf,
                    "llm_parent_number": parent_number,
                    "llm_amendment_number": ref.get("amendment_number"),
                    "llm_parent_title": ref.get("parent_title"),
                    "llm_confidence": ref.get("confidence"),
                    "match_type": match_type,
                    "is_self_match": is_self,
                    "matched_parent_id": match[0] if match else None,
                    "matched_parent_cislo": match[1] if match else None,
                    "matched_parent_nazov": match[2] if match else None,
                    "matched_parent_typ": match[3] if match else None,
                }
                results.append(result)

                if match and not is_self:
                    stats["matched_real"] += 1
                    icon = "✓"
                elif is_self:
                    stats["matched_self"] += 1
                    icon = "≡"
                elif not parent_number:
                    stats["no_parent"] += 1
                    icon = "?"
                else:
                    stats["no_match_in_db"] += 1
                    icon = "✗"

                pbar.write(
                    f"  {icon} {a['id']} | ref={parent_number} | "
                    f"match={match_type} | "
                    f"parent={'SELF' if is_self else (match[0] if match else '-')}"
                )

    pbar.close()

    print(f"\n{'='*60}")
    print(f"Stats: {json.dumps(stats, indent=2)}")
    total_with_ref = stats["extracted"] - stats["no_parent"]
    total_matched = stats["matched_real"] + stats["matched_self"]
    print(f"\nLLM extracted a parent ref: {total_with_ref}/{stats['extracted']} "
          f"({100*total_with_ref/max(stats['extracted'],1):.0f}%)")
    print(f"Matched in DB (real + self): {total_matched}/{stats['extracted']} "
          f"({100*total_matched/max(stats['extracted'],1):.0f}%)")
    print(f"  Real matches (different contract): {stats['matched_real']}")
    print(f"  Self matches (same cislo):         {stats['matched_self']}")
    print(f"Parent ref found but not in DB:      {stats['no_match_in_db']}")

    # Save detailed results
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(repo_root, "data", "amendment_linking_experiment.json")
    with open(out_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nDetailed results saved to {out_path}")


if __name__ == "__main__":
    main()
