"""Extract structured data from CRZ contract texts or PDFs using LLM.

Uses OpenRouter API (OpenAI-compatible) to classify and extract
key fields from Slovak government contract PDFs.

Usage:
    python extract_contracts.py                    # extract from texts, fallback to PDFs
    python extract_contracts.py --limit 10         # extract 10 contracts
    python extract_contracts.py --file 6578512.txt # extract one specific file
    python extract_contracts.py --dry-run          # show what would be processed
"""
import confpath  # noqa: F401

import json
import os
import csv
import time
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite_utils
import httpx
from tqdm import tqdm

from settings import get_env, get_path, normalize_company_name
from openrouter_utils import OPENROUTER_BASE, load_openrouter_api_key


MODEL = get_env("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")

SYSTEM_PROMPT = """You are a structured data extractor for Slovak government contracts from the Central Register of Contracts (CRZ). You receive the text of a contract and extract key fields.

Respond ONLY with valid JSON matching this schema — no markdown, no explanation:

{
  "service_category": one of the categories listed below,
  "actual_subject": short description of what the contract is actually about (1-2 sentences, in Slovak),
  "hidden_entities": [{"name": "...", "ico": "...", "role": one of the roles listed below, "percentage": number or null, "subcontract_subject": "..." or null}],
  "penalties": [{"penalized_party": "supplier" or "buyer", "trigger": "...", "amount": "..."}],
  "penalty_asymmetry": one of the asymmetry values listed below,
  "penalty_asymmetry_reason": short explanation (1 sentence) of why you chose this asymmetry value, referencing only the explicit penalties you extracted,
  "termination": {"buyer_can_terminate_without_cause": bool, "supplier_can_terminate_without_cause": bool, "notice_period": "..." or null},
  "funding_source": {"type": one of "eu_recovery_plan", "eu_structural_funds", "erasmus", "de_minimis", "state_budget", "municipal_budget", "other_eu", "none" , "scheme_reference": "..." or null, "grant_amount": number or null},
  "signatories": [{"party": "supplier" or "buyer", "name": "...", "role": "...", "delegation": "statutory" or "poverenie" or "plnomocenstvo" or "mandatna_zmluva" or null}],
  "duration_type": one of "fixed_term", "indefinite", "one_time",
  "duration_end_date": "YYYY-MM-DD" or null (only for fixed_term, extract from "do DD.MM.YYYY" or similar),
  "bank_accounts": [{"party": "supplier" or "buyer", "iban": "SK..."}],
  "auto_renewal": bool,
  "bezodplatne": bool,
  "subcontracting_mentioned": bool
}

Important output constraints:
- Return ALL top-level keys shown above on every response.
- Use ONLY the enum values explicitly listed in this prompt.
- Do NOT add extra keys anywhere in the JSON.
- Boolean fields must always be true or false, never null.
- If data is absent, use [] for arrays, null for optional strings/numbers, false for booleans, and the documented enum fallback values.

Service categories (pick the best match):
- construction_renovation — stavebné práce, rekonštrukcia, opravy budov, Zmluva o dielo on buildings/infrastructure
- software_it — softvér, IT systémy, licencie, hosting, údržba informačných systémov
- cultural_event_production — kultúrne podujatia, koncerty, festivaly, divadelné predstavenia
- utilities — energie, voda, plyn, elektrická energia, teplo, telekomunikácie
- insurance — poistenie majetku, zodpovednosti, vozidiel
- professional_consulting — poradenstvo, audity, štúdie, odborné posudky, expertízy
- media_marketing — reklama, propagácia, médiá, tlač, grafický dizajn
- grant_subsidy — dotácie, príspevky, nenávratné finančné príspevky (not Erasmus)
- property_lease — nájom nehnuteľností, pozemkov, priestorov
- cemetery — cintoríny, pohrebné služby, správa cintorínov
- asset_transfer — prevod majetku, kúpa/predaj nehnuteľností, pozemkov
- employment_social — dohody o práci, §59 aktivačné práce, sociálne služby, opatrovateľstvo
- legal_services — právne služby, advokátske zastúpenie, notárske služby
- cleaning_facility — upratovanie, čistenie, správa budov, facility management
- digital_certification — elektronický podpis, certifikáty, časové pečiatky
- hr_payroll_outsourcing — mzdové účtovníctvo, personalistika, outsourcing HR
- pharmaceutical_clinical — lieky, zdravotnícke pomôcky, klinické skúšky
- easement_encumbrance — vecné bremeno, záložné právo, ťarchy na nehnuteľnostiach
- procurement_purchase — kúpa tovaru/zariadení (nie nehnuteľnosti, nie stavba)
- vehicle_use — dohoda o použití súkromného motorového vozidla (SCMV)
- erasmus_academic_mobility — Erasmus+ granty, akademická mobilita, výmenné pobyty
- accommodation — ubytovanie, internáty, ubytovacie zariadenia
- waste_management — zber odpadu, zneškodnenie, kompostéry, triedenie
- renewable_energy_voucher — Zelená domácnostiam, poukážky na obnoviteľné zdroje
- donation — darovacia zmluva, bezodplatný dar (nie prevod majetku)
- copyright_royalty — autorské práva, vysporiadanie odmeny, SLOVGRAM, SOZA, licencie na diela
- competition_olympiad — súťaže, olympiády, školské/športové súťaže
- other — use only if none of the above fits

Category mapping guardrails:
- Never invent a new service_category label outside the list above.
- Transportation, logistics, passenger transport, and náhradná autobusová doprava -> procurement_purchase unless a better listed category clearly fits.
- Security guard / strážna služba / SBS contracts -> professional_consulting unless a better listed category clearly fits.
- Maintenance / servicing contracts for equipment or lifts -> procurement_purchase unless the contract is clearly about facility cleaning/management.
- Healthcare or social-care service provision agreements -> employment_social or pharmaceutical_clinical, whichever is clearly closer. Never emit labels such as healthcare_services or health_social_services.

Hidden entity roles (pick the best match):
- manager_operator — správca, prevádzkovateľ: company managing property/facility on behalf of a party (e.g. ByPo, TEZAR, Pohrebníctvo DVONČ managing cemetery for a city)
- subcontractor — subdodávateľ: entity performing work under the main contract, geodetic companies in property transfers (e.g. GEPRAMS, GEOmark doing surveys). For subcontractors, also extract "percentage" (their share of total contract value, 0-100, or null if not stated) and "subcontract_subject" (what they do, short phrase in Slovak, or null). Look for these in appendix tables ("Zoznam subdodávateľov"), inline text, or anywhere the percentage share is mentioned.
- consortium_member — člen konzorcia/združenia: member of a group bidding or performing together
- previous_operator — predchádzajúci prevádzkovateľ/dodávateľ: entity being replaced by this contract
- co_user — spoluužívateľ: additional authorized user of services/property beyond the main parties
- insurance_broker — poisťovací maklér/sprostredkovateľ: broker or intermediary in insurance contracts (e.g. Finportal, Brokeria, Respect Slovakia, MAXIMA BROKER, RENOMIA)
- authorized_representative — splnomocnený zástupca: legal representative acting on behalf of a party who is a SEPARATE ORGANIZATION (not an employee or signatory of the contracting parties)

Penalty asymmetry — determined by WHO gets penalized, not who benefits:
- strong_buyer_advantage — only the supplier (dodávateľ) faces penalties, or supplier penalties are much harsher (higher rates, more triggers). The buyer is protected.
- moderate_buyer_advantage — both sides have some penalties, but supplier faces more or harsher ones
- balanced — both sides face comparable penalties (similar rates, similar triggers)
- supplier_advantage — only the buyer (objednávateľ) faces penalties, or buyer penalties are much harsher. The supplier is protected. This is rare in government contracts.
- none_found — no explicit contractual penalties found

Key: "penalized_party" in the penalties array means the party who MUST PAY the penalty (the one being punished). If only the supplier is penalized, that is buyer_advantage. If only the buyer is penalized, that is supplier_advantage.

Duration type:
- fixed_term — na dobu určitú: contract has a specific end date or defined period
- indefinite — na dobu neurčitú: contract runs until terminated
- one_time — jednorazové plnenie: single delivery/event with no ongoing duration (e.g. kúpna zmluva, jednorazová služba)

Signatories — extract the people who actually signed, one per party:
- "role" = their title (e.g. starosta, konateľ, riaditeľ, generálny riaditeľ, predseda predstavenstva)
- "delegation" = how they got signing authority:
  - "statutory" — they ARE the štatutárny zástupca (starosta, konateľ, riaditeľ)
  - "poverenie" — acting na základe poverenia (internal delegation)
  - "plnomocenstvo" — acting na základe plnomocenstva (power of attorney)
  - "mandatna_zmluva" — acting under a mandátna zmluva (e.g. ByPo signing for Mesto Ružomberok)
  - null — delegation type not stated or unclear

Signatories:
- Extract all people who actually signed, not just one person per party.
- Use "buyer" for the first/main contracting side and "supplier" for the other side for schema purposes, even in non-procurement contracts.
- Do not put organizations into signatories unless the scan/text makes the person unreadable and only the organization name is visible.

Rules:
- hidden_entities: ONLY include organizations or persons that are NOT the two main contracting parties (dodávateľ/objednávateľ). Specifically:
  - Do NOT include the dodávateľ or objednávateľ themselves, even under a slightly different name or spelling. If an entity is one of the two main parties, SKIP it — even if it also plays another role (e.g. a dodávateľ who is also a consortium member). The main parties are already known.
  - If the contract is not a typical procurement contract (for example a kolektívna zmluva, dodatok ku kolektívnej zmluve, or another agreement with a union/association as a signatory party), treat those named signatory organizations as main contracting parties, not hidden entities. In such cases, `hidden_entities` will often correctly be [].
  - Do NOT include people who merely signed the contract (štatutárny zástupca, konateľ, starosta, riaditeľ) — these are signatories, not hidden entities.
  - Do NOT include bank account signatories (disponenti).
  - Do NOT include funding bodies, grant providers, host institutions, receiving institutions, property owners, or vehicle owners unless they clearly match one of the allowed hidden-entity roles.
  - Do NOT include generic collecting societies (SOZA, LITA, Literárny fond) unless they are a contractual party.
  - Only use roles from the list above. Never invent new roles like "supplier", "buyer", "owner", "organizer". If an entity does not fit any defined role, skip it.
  - When no hidden-entity role clearly applies, return an empty array [] instead of force-fitting a named organization into an approximate role such as consortium_member.
  - Example: in a collective agreement between a school and a union organization, the union organization is a main contracting party and MUST NOT appear in `hidden_entities`.
  - If an IČO looks like garbled text (OCR artifact), set it to null rather than including garbage.
  - "percentage" and "subcontract_subject" fields ONLY apply to entities with role "subcontractor". Set both to null for all other roles.
  - For "percentage", extract the numeric share of total contract value (0-100). Ignore percentages that refer to DPH/VAT rates, zmluvná pokuta rates, discount rates, co-financing shares, or Russian sanctions thresholds (Article 5k, Regulation 833/2014).
- subcontracting_mentioned: set to true if the contract text discusses subcontracting in any way (subdodávateľ, subdodávka, zoznam subdodávateľov), even if no named subcontractor is found. Set to false otherwise.
- penalties: extract only explicit contractual penalties or payment-default interest with a specific contractual or clearly stated rate/amount. Do NOT treat termination rights, odstúpenie, výpoveď, prerušenie plnenia, refund obligations, or generic return-of-funds clauses as penalties unless they are explicitly framed as zmluvná pokuta or a quantified sanction.
- `penalized_party` must be exactly "supplier" or "buyer". Do not use synonyms such as payer.
- penalty_asymmetry must be based only on the extracted `penalties` array, not on termination rights or general remedies.
- bank_accounts: extract IBAN numbers (SK format).
- funding_source.type uses its own enum and must never reuse service_category labels like grant_subsidy or erasmus_academic_mobility.
- For fixed_term contracts without a precise calendar date, keep duration_type="fixed_term" and set duration_end_date to null unless the end date is explicitly clear from the text.
- If a field has no data, use empty array [] for arrays, null for optional strings/numbers, false for booleans, "none_found" or "none" for enums.
- Keep actual_subject concise but specific — it should disambiguate generic titles like "Zmluva o dielo"."""

USER_PROMPT_TEMPLATE = """Extract structured data from this Slovak government contract text.

Contract text:
---
{text}
---"""

USER_PROMPT_INSTRUCTION = "Extract structured data from this Slovak government contract text."


import re


VALID_SERVICE_CATEGORIES = {
    "construction_renovation",
    "software_it",
    "cultural_event_production",
    "utilities",
    "insurance",
    "professional_consulting",
    "media_marketing",
    "grant_subsidy",
    "property_lease",
    "cemetery",
    "asset_transfer",
    "employment_social",
    "legal_services",
    "cleaning_facility",
    "digital_certification",
    "hr_payroll_outsourcing",
    "pharmaceutical_clinical",
    "easement_encumbrance",
    "procurement_purchase",
    "vehicle_use",
    "erasmus_academic_mobility",
    "accommodation",
    "waste_management",
    "renewable_energy_voucher",
    "donation",
    "copyright_royalty",
    "competition_olympiad",
    "other",
}

VALID_HIDDEN_ENTITY_ROLES = {
    "manager_operator",
    "subcontractor",
    "consortium_member",
    "previous_operator",
    "co_user",
    "insurance_broker",
    "authorized_representative",
}

VALID_FUNDING_TYPES = {
    "eu_recovery_plan",
    "eu_structural_funds",
    "erasmus",
    "de_minimis",
    "state_budget",
    "municipal_budget",
    "other_eu",
    "none",
}

VALID_PENALTY_ASYMMETRY = {
    "strong_buyer_advantage",
    "moderate_buyer_advantage",
    "balanced",
    "supplier_advantage",
    "none_found",
}

VALID_DURATION_TYPES = {"fixed_term", "indefinite", "one_time"}
VALID_DELEGATIONS = {"statutory", "poverenie", "plnomocenstvo", "mandatna_zmluva", None}

SERVICE_CATEGORY_ALIASES = {
    "transport": "procurement_purchase",
    "transportation": "procurement_purchase",
    "security_services": "professional_consulting",
    "maintenance": "procurement_purchase",
    "maintenance_repair": "procurement_purchase",
    "healthcare": "employment_social",
    "health_care": "employment_social",
    "healthcare_services": "employment_social",
    "health_care_services": "employment_social",
    "health_social_services": "employment_social",
    "health_and_social_services": "employment_social",
    "social_services": "employment_social",
}

FUNDING_TYPE_ALIASES = {
    "erasmus_academic_mobility": "erasmus",
    "grant_subsidy": "other_eu",
    "other": "none",
}

REMEDY_PATTERNS = [
    r"(?i)\bodstúpi",
    r"(?i)\bvýpove",
    r"(?i)\bpreruši",
    r"(?i)\bvráti",
    r"(?i)\bvráten",
    r"(?i)\bpozastav",
    r"(?i)\bneposkytne\b",
    r"(?i)nemá\s+nárok",
]

QUANTIFIED_PENALTY_PATTERNS = [
    r"(?i)zmluvn[áé]\s*pokut",
    r"(?i)\b\d+[,.]?\d*\s*%",
    r"(?i)\b\d+[,.]?\d*\s*eur\b",
]

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


def _clean_llm_json(raw: str) -> str:
    """Clean LLM output into valid JSON.

    Handles: markdown fences, trailing commas, truncated output (unclosed
    brackets/braces/strings).
    """
    import re

    s = raw.strip()

    # Strip markdown code fences
    if s.startswith("```"):
        # Remove opening fence (with optional language tag)
        s = re.sub(r"^```[a-zA-Z]*\s*\n?", "", s)
        # Remove closing fence
        s = re.sub(r"\n?```\s*$", "", s)
        s = s.strip()

    # Remove trailing commas before } or ]
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # Try parsing as-is first
    try:
        json.loads(s)
        return s
    except json.JSONDecodeError:
        pass

    # Truncated output repair: close unclosed strings, arrays, brackets
    # Close any unclosed string literal
    in_string = False
    escaped = False
    for ch in s:
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
    if in_string:
        s += '"'

    # Remove trailing incomplete key-value pairs (e.g. `"key": "val` or `"key":`)
    # after closing the string, strip trailing partial entries
    s = re.sub(r',\s*"[^"]*"\s*:\s*"?[^"}\]]*$', "", s)
    # Remove trailing commas again after surgery
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # Count open braces/brackets and close them
    opens = 0
    open_sq = 0
    in_str = False
    esc = False
    for ch in s:
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            opens += 1
        elif ch == "}":
            opens -= 1
        elif ch == "[":
            open_sq += 1
        elif ch == "]":
            open_sq -= 1

    s += "]" * max(open_sq, 0)
    s += "}" * max(opens, 0)

    return s


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
            "max_tokens": 4000,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    content = _clean_llm_json(content)

    usage = data.get("usage", {})
    return json.loads(content), usage


def extract_one_pdf(client, api_key, pdf_path, model=MODEL):
    """Send a PDF to the same extraction prompt and return parsed JSON."""
    with open(pdf_path, "rb") as f:
        pdf_data = base64.b64encode(f.read()).decode("utf-8")

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
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT_INSTRUCTION},
                        {
                            "type": "file",
                            "file": {
                                "filename": os.path.basename(pdf_path),
                                "file_data": f"data:application/pdf;base64,{pdf_data}",
                            },
                        },
                    ],
                },
            ],
            "temperature": 0.0,
            "max_tokens": 4000,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    content = _clean_llm_json(content)

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


def extract_main_party_names(meta: dict, text: str | None) -> set[str]:
    """Collect normalized names for the two main contracting parties."""
    names = set()

    for key in ("dodavatel", "objednavatel"):
        value = (meta or {}).get(key)
        if value:
            names.add(normalize_company_name(value))

    if text:
        patterns = [
            r"(?im)^\s*(?:dodávateľ|dodavatel|predávajúci|poskytovateľ|zhotoviteľ|zamestnávateľ|účastník)\s*[:]\s*(.+)$",
            r"(?im)^\s*(?:objednávateľ|objednavatel|kupujúci|klient|organizácia|úrad)\s*[:]\s*(.+)$",
        ]
        for pattern in patterns:
            for match in re.findall(pattern, text):
                head = match.split(",", 1)[0].strip()
                if head:
                    names.add(normalize_company_name(head))

    return {name for name in names if name}


def normalize_service_category(value: str | None, actual_subject: str | None) -> str:
    """Map invalid or drifted service categories onto the supported enum."""
    if value in VALID_SERVICE_CATEGORIES:
        return value

    if value in SERVICE_CATEGORY_ALIASES:
        return SERVICE_CATEGORY_ALIASES[value]

    subject = (actual_subject or "").lower()
    if "náhradn" in subject and "autobus" in subject:
        return "procurement_purchase"
    if "strážn" in subject or "bezpečnostn" in subject:
        return "professional_consulting"
    if "údržb" in subject or "servis" in subject:
        return "procurement_purchase"

    return "other"


def normalize_funding_type(value: str | None) -> str:
    """Map invalid funding types onto the supported enum."""
    if value in VALID_FUNDING_TYPES:
        return value
    if value in FUNDING_TYPE_ALIASES:
        return FUNDING_TYPE_ALIASES[value]
    return "none"


def normalize_hidden_entities(
    entities: list,
    main_party_names: set[str],
    service_category: str,
    actual_subject: str | None,
) -> list[dict]:
    """Drop invalid hidden entities and main-party leaks."""
    normalized = []
    subject = (actual_subject or "").lower()
    collective_context = "kolektívn" in subject
    erasmus_context = service_category == "erasmus_academic_mobility"

    for entity in entities or []:
        if not isinstance(entity, dict):
            continue
        name = (entity.get("name") or "").strip()
        role = entity.get("role")
        if not name or role not in VALID_HIDDEN_ENTITY_ROLES:
            continue

        normalized_name = normalize_company_name(name)
        if normalized_name and normalized_name in main_party_names:
            continue

        lowered = name.lower()
        if collective_context and ("odbor" in lowered or "zväz" in lowered):
            continue
        if erasmus_context and ("university" in lowered or "instit" in lowered or "erasmus" in lowered):
            continue

        cleaned = {
            "name": name,
            "ico": entity.get("ico"),
            "role": role,
            "percentage": entity.get("percentage") if role == "subcontractor" else None,
            "subcontract_subject": entity.get("subcontract_subject") if role == "subcontractor" else None,
        }
        normalized.append(cleaned)

    return normalized


def is_quantified_penalty(text: str) -> bool:
    """Return true when text looks like a quantified penalty or late-payment interest."""
    return any(re.search(pattern, text) for pattern in QUANTIFIED_PENALTY_PATTERNS)


def is_remedy_only(trigger: str, amount: str) -> bool:
    """Identify remedy-like clauses that should not be treated as penalties."""
    combined = f"{trigger} {amount}".strip()
    if not combined:
        return True
    if is_quantified_penalty(combined):
        return False
    return any(re.search(pattern, combined) for pattern in REMEDY_PATTERNS)


def normalize_penalties(penalties: list) -> list[dict]:
    """Keep only explicit penalties and normalize fields."""
    normalized = []
    for penalty in penalties or []:
        if not isinstance(penalty, dict):
            continue
        party = penalty.get("penalized_party")
        if party not in {"buyer", "supplier"}:
            party = None
        trigger = (penalty.get("trigger") or "").strip()
        amount = (penalty.get("amount") or "").strip()
        if not party or not trigger or not amount:
            continue
        if is_remedy_only(trigger, amount):
            continue
        normalized.append(
            {
                "penalized_party": party,
                "trigger": trigger,
                "amount": amount,
            }
        )
    return normalized


def derive_penalty_asymmetry(penalties: list[dict]) -> tuple[str, str | None]:
    """Recompute asymmetry from the normalized penalties array."""
    if not penalties:
        return "none_found", None

    buyer_count = sum(1 for penalty in penalties if penalty["penalized_party"] == "buyer")
    supplier_count = sum(1 for penalty in penalties if penalty["penalized_party"] == "supplier")

    if supplier_count and not buyer_count:
        return "strong_buyer_advantage", "Len dodávateľ čelí explicitným sankciám v extrahovaných ustanoveniach."
    if buyer_count and not supplier_count:
        return "supplier_advantage", "Len objednávateľ čelí explicitným sankciám v extrahovaných ustanoveniach."
    if supplier_count > buyer_count:
        return "moderate_buyer_advantage", "Dodávateľ čelí viac explicitným sankciám než objednávateľ."
    if buyer_count > supplier_count:
        return "supplier_advantage", "Objednávateľ čelí viac explicitným sankciám než dodávateľ."
    return "balanced", "Obe strany čelia porovnateľným explicitným sankciám."


def normalize_signatories(signatories: list) -> list[dict]:
    """Keep signatory records schema-conformant without inventing values."""
    normalized = []
    for signatory in signatories or []:
        if not isinstance(signatory, dict):
            continue
        party = signatory.get("party")
        if party not in {"buyer", "supplier"}:
            continue
        delegation = signatory.get("delegation")
        if delegation not in VALID_DELEGATIONS:
            delegation = None
        normalized.append(
            {
                "party": party,
                "name": signatory.get("name"),
                "role": signatory.get("role"),
                "delegation": delegation,
            }
        )
    return normalized


def sanitize_extraction(extraction: dict, meta: dict, text: str | None) -> dict:
    """Normalize model output into the expected schema and enums."""
    actual_subject = extraction.get("actual_subject")
    service_category = normalize_service_category(extraction.get("service_category"), actual_subject)
    funding_source = extraction.get("funding_source") or {}
    main_party_names = extract_main_party_names(meta, text)

    cleaned = {
        "service_category": service_category,
        "actual_subject": actual_subject,
        "hidden_entities": normalize_hidden_entities(
            extraction.get("hidden_entities", []),
            main_party_names,
            service_category,
            actual_subject,
        ),
        "penalties": normalize_penalties(extraction.get("penalties", [])),
        "termination": extraction.get("termination") or {},
        "funding_source": {
            "type": normalize_funding_type(funding_source.get("type")),
            "scheme_reference": funding_source.get("scheme_reference"),
            "grant_amount": funding_source.get("grant_amount"),
        },
        "signatories": normalize_signatories(extraction.get("signatories", [])),
        "duration_type": extraction.get("duration_type") if extraction.get("duration_type") in VALID_DURATION_TYPES else "one_time",
        "duration_end_date": extraction.get("duration_end_date"),
        "bank_accounts": extraction.get("bank_accounts", []),
        "auto_renewal": bool(extraction.get("auto_renewal", False)),
        "bezodplatne": bool(extraction.get("bezodplatne", False)),
        "subcontracting_mentioned": bool(extraction.get("subcontracting_mentioned", False)),
    }

    termination = cleaned["termination"]
    cleaned["termination"] = {
        "buyer_can_terminate_without_cause": bool(termination.get("buyer_can_terminate_without_cause", False)),
        "supplier_can_terminate_without_cause": bool(termination.get("supplier_can_terminate_without_cause", False)),
        "notice_period": termination.get("notice_period"),
    }

    if cleaned["duration_type"] != "fixed_term":
        cleaned["duration_end_date"] = None

    asymmetry, asymmetry_reason = derive_penalty_asymmetry(cleaned["penalties"])
    cleaned["penalty_asymmetry"] = asymmetry if asymmetry in VALID_PENALTY_ASYMMETRY else "none_found"
    cleaned["penalty_asymmetry_reason"] = asymmetry_reason

    return cleaned


def normalize_contract_arg(name: str) -> str:
    """Normalize --file input to the canonical .txt-based contract key."""
    if name.endswith(".txt"):
        return name
    if name.endswith(".pdf"):
        return name[:-4] + ".txt"
    return name + ".txt"


def main():
    parser = argparse.ArgumentParser(description="Extract structured data from CRZ contract texts or PDFs")
    parser.add_argument("--limit", type=int, default=0, help="Max contracts to process (0=all)")
    parser.add_argument("--file", type=str, help="Process a single text file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    parser.add_argument("--model", type=str, default=MODEL, help=f"OpenRouter model (default: {MODEL})")
    parser.add_argument(
        "--texts-dir",
        type=str,
        default=get_path("CRZ_TEXT_DIR", "data/texts"),
        help="Directory with text files",
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default=get_path("CRZ_PDF_DIR", "data/pdfs"),
        help="Directory with PDFs for direct extraction fallback",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=get_path("CRZ_EXTRACTIONS_DIR", "data/extractions"),
        help="Directory for JSON outputs",
    )
    parser.add_argument("--workers", type=int, default=8, help="Parallel workers (default: 8)")
    parser.add_argument("--force", action="store_true", help="Re-extract even if JSON already exists")
    parser.add_argument(
        "--from",
        type=str,
        dest="date_from",
        help="Start date (YYYY-MM-DD) or month (YYYY-MM). Only extract contracts from this date.",
    )
    parser.add_argument(
        "--to",
        type=str,
        dest="date_to",
        help="End date (YYYY-MM-DD) or month (YYYY-MM). Inclusive.",
    )
    args = parser.parse_args()

    api_key = load_openrouter_api_key()
    texts_dir = args.texts_dir
    pdf_dir = args.pdf_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Determine which files to process
    db = sqlite_utils.Database(get_path("CRZ_DB_PATH", "crz.db"))
    if args.file:
        files = [normalize_contract_arg(args.file)]
    elif args.date_from:
        # Query DB for attachments in the date range
        date_from = args.date_from + "-01" if len(args.date_from) == 7 else args.date_from
        if args.date_to:
            if len(args.date_to) == 7:
                date_to_exclusive = args.date_to + "-01"
                date_filter = "z.datum_zverejnenia >= ? AND z.datum_zverejnenia < date(?, '+1 month')"
            else:
                date_to_exclusive = args.date_to
                date_filter = "z.datum_zverejnenia >= ? AND z.datum_zverejnenia < date(?, '+1 day')"
        else:
            if len(args.date_from) == 7:
                date_to_exclusive = args.date_from + "-01"
                date_filter = "z.datum_zverejnenia >= ? AND z.datum_zverejnenia < date(?, '+1 month')"
            else:
                date_to_exclusive = args.date_from
                date_filter = "z.datum_zverejnenia >= ? AND z.datum_zverejnenia < date(?, '+1 day')"

        rows = db.execute(
            f"""
            SELECT p.subor FROM prilohy p
            JOIN zmluvy z ON p.zmluva_id = z.id
            WHERE p.subor LIKE '%.pdf' AND {date_filter}
            ORDER BY p.subor
            """,
            [date_from, date_to_exclusive],
        ).fetchall()
        stems = sorted(set(r[0][:-4] for r in rows))
        files = [f"{stem}.txt" for stem in stems]
        period = f"{args.date_from} to {args.date_to or args.date_from}"
        print(f"Date filter {period}: {len(files)} contracts matched")
    else:
        txt_stems = {f[:-4] for f in os.listdir(texts_dir) if f.endswith(".txt")}
        pdf_stems = {f[:-4] for f in os.listdir(pdf_dir) if f.endswith(".pdf")}
        files = [f"{stem}.txt" for stem in sorted(txt_stems | pdf_stems)]

    # Skip already-extracted files (unless --force)
    if args.force:
        already_done = set()
    else:
        already_done = set(f.replace(".json", ".txt") for f in os.listdir(output_dir) if f.endswith(".json"))
    to_process = [f for f in files if f not in already_done]

    if args.limit > 0:
        to_process = to_process[:args.limit]

    print(f"Contracts: {len(files)}, already extracted: {len(already_done)}, to process: {len(to_process)}")

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

    total_tokens = 0
    ok, fail = 0, 0

    def process_one(fname, client):
        """Call LLM and save JSON. Returns (fname, extraction, usage) or (fname, error_msg, None)."""
        txt_path = os.path.join(texts_dir, fname)
        pdf_name = fname.replace(".txt", ".pdf")
        pdf_path = os.path.join(pdf_dir, pdf_name)
        source_kind = None

        text = None
        if os.path.exists(txt_path):
            text = open(txt_path).read()
            if len(text.strip()) >= 50:
                source_kind = "text"

        if source_kind is None and os.path.exists(pdf_path):
            source_kind = "pdf"

        if source_kind is None:
            return (fname, "no usable text or pdf found", None)

        try:
            if source_kind == "text":
                extraction, usage = extract_one(client, api_key, text, model=args.model)
            else:
                extraction, usage = extract_one_pdf(client, api_key, pdf_path, model=args.model)

            # Add metadata
            meta = manifest.get(fname, {})
            extraction = sanitize_extraction(extraction, meta, text)
            extraction["_source_file"] = fname
            extraction["_source_kind"] = source_kind
            extraction["_zmluva_id"] = meta.get("zmluva_id", fname.replace(".txt", ""))
            extraction["_model"] = args.model

            # Save JSON (file I/O is safe across threads)
            out_path = os.path.join(output_dir, fname.replace(".txt", ".json"))
            with open(out_path, "w") as f:
                json.dump(extraction, f, ensure_ascii=False, indent=2)

            return (fname, extraction, usage)

        except json.JSONDecodeError as e:
            return (fname, f"bad JSON: {e}", None)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                time.sleep(10)
            return (fname, f"HTTP {e.response.status_code}", None)
        except Exception as e:
            return (fname, str(e), None)

    pbar = tqdm(total=len(to_process), desc="Extracting", unit="contract")

    with httpx.Client(timeout=60) as client:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(process_one, fname, client): fname for fname in to_process}
            for future in as_completed(futures):
                fname, result, usage = future.result()
                pbar.update(1)

                if usage is None:
                    # Error or skip
                    pbar.write(f"  FAIL {fname}: {result}")
                    fail += 1
                else:
                    extraction = result
                    tokens = usage.get("total_tokens", 0)
                    total_tokens += tokens

                    # DB upsert in main thread
                    subcontractors = [e for e in extraction.get("hidden_entities", []) if e.get("role") == "subcontractor"]
                    sub_pcts = [e["percentage"] for e in subcontractors if e.get("percentage") is not None]
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
                        "subcontracting_mentioned": extraction.get("subcontracting_mentioned", False),
                        "subcontractor_count": len(subcontractors),
                        "subcontractor_max_percentage": max(sub_pcts) if sub_pcts else None,
                        "extraction_json": json.dumps(extraction, ensure_ascii=False),
                        "model": args.model,
                    }
                    db["extractions"].insert(
                        db_row,
                        pk="zmluva_id",
                        foreign_keys=[("zmluva_id", "zmluvy", "id")],
                        alter=True,
                        replace=True,
                    )
                    ok += 1

                pbar.set_postfix(ok=ok, fail=fail)

    pbar.close()
    print(f"\nDone: {ok} extracted, {fail} failed, {total_tokens} total tokens")
    print(f"Extractions in {output_dir}/ and crz.db:extractions table")


if __name__ == "__main__":
    main()
