# flag_rules & red_flags

Automated zlte stopy — 36 rules that check every contract against multiple
data sources and flag suspicious patterns.

- **Rows:** 36 rules, ~310K materialized flag hits
- **Browse rules:** [zmluvy.zltastopa.sk/data/crz/flag_rules](https://zmluvy.zltastopa.sk/data/crz/flag_rules)
- **Browse flags:** [zmluvy.zltastopa.sk/data/crz/red_flags](https://zmluvy.zltastopa.sk/data/crz/red_flags)
- **Evaluation script:** `pipeline/flag_contracts.py`

## flag_rules

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Rule slug (e.g. `fresh_company`, `negative_equity`) |
| `label` | TEXT | Human-readable name in Slovak |
| `description` | TEXT | What the rule checks |
| `severity` | TEXT | `danger`, `warning`, or `info` |
| `sql_condition` | TEXT | SQL WHERE clause or `__custom__` for programmatic rules |
| `needs_extraction` | INTEGER | 1 if rule requires LLM extraction data |
| `enabled` | INTEGER | 1 if active |
| `created_at` | TEXT | Creation timestamp |

## red_flags

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment |
| `zmluva_id` | INTEGER FK | References `zmluvy.id` |
| `flag_type` | TEXT FK | References `flag_rules.id` |
| `detail` | TEXT | Human-readable detail (e.g. supplier name, debt amount) |
| `created_at` | TEXT | Evaluation timestamp |

Unique constraint on `(zmluva_id, flag_type)` — each contract can have
at most one hit per rule.

## All 36 rules

### Danger (12)

| id | label | Data source |
|----|-------|-------------|
| `fresh_micro_large` | Nova mikro firma, velka zmluva | RUZ |
| `fs_tax_debtor` | Danovy dlznik FS | Financna sprava |
| `fs_vat_dereg_risk` | Dovody na zrusenie DPH | Financna sprava |
| `fs_vat_deregistered` | Vymazany z DPH registra | Financna sprava (cross-check s `fs_vat_dereg_reasons`; historicke pripady oznacene HISTORICKY) |
| `negative_equity` | Zaporne vlastne imanie | RUZ equity |
| `socpoist_debtor` | Dlznik Socialnej poistovne | Socialna poistovna |
| `supplier_advantage` | Pokuty zvyhodnuju dodavatela | LLM extraction |
| `tax_unreliable` | Danovo nespolahlivy dodavatel | Financna sprava |
| `tax_unreliable_entity` | Nespolahlivy subjekt v zmluve | Financna sprava + LLM |
| `terminated_company` | Zrusena firma | RUZ |
| `vszp_debtor` | Dlznik VSZP | VSZP |
| `vszp_debtor_entity` | Skryta entita dlznik VSZP | VSZP + LLM |

### Warning (17)

| id | label | Data source |
|----|-------|-------------|
| `amount_outlier` | Neobvykle vysoka suma | CRZ |
| `bezodplatne` | Bezodplatna zmluva | LLM extraction |
| `contract_splitting` | Delenie zakazky | CRZ |
| `dodatok_price_inflation` | Navysenie ceny dodatkami | CRZ |
| `dormant_then_active` | Spaca firma | RUZ + CRZ |
| `fresh_company` | Cerstve zalozena firma | RUZ |
| `hidden_entities` | Skryte entity | LLM extraction |
| `hidden_entity_is_supplier` | Skryta entita = dodavatel | LLM extraction |
| `hidden_price` | Skryta cena | CRZ |
| `high_subcontracting` | Vysoka miera subdodavok | LLM extraction |
| `micro_supplier_large_contract` | Mikro dodavatel, velka zmluva | RUZ + CRZ |
| `missing_attachment` | Chybajuca priloha | CRZ |
| `nace_mismatch` | Nesulad odvetvia ¹ | RUZ + LLM |
| `nonprofit_large_contract` | Neziskovka s velkou zmluvou | RUZ + CRZ |
| `rapid_succession` | Zmluvy v rychlom slede | CRZ |
| `signatory_overlap` | Zdielany podpisujuci | LLM extraction |
| `threshold_gaming` | Tesne pod limitom EU sutaze | CRZ |

### Info (7)

| id | label | Data source |
|----|-------|-------------|
| `excessive_penalties` | Nadmerny pocet pokut | LLM extraction |
| `foreign_supplier` | Zahranicny dodavatel | RUZ |
| `missing_expiry` | Neuvedena platnost | CRZ |
| `missing_ico` | Dodavatel bez ICO | CRZ |
| `not_in_ruz` | Dodavatel nie je v RUZ | RUZ |
| `supplier_monopoly` | Monopolny dodavatel | CRZ |
| `weekend_signing` | Podpis cez vikend | CRZ |

## Example queries

```sql
-- Contracts with the most zlte stopy
SELECT z.id, z.nazov_zmluvy, z.dodavatel, z.suma,
       count(rf.id) AS flag_count
FROM zmluvy z
JOIN red_flags rf ON rf.zmluva_id = z.id
GROUP BY z.id ORDER BY flag_count DESC LIMIT 20;

-- Danger flags for a specific contract
SELECT fr.label, fr.severity, rf.detail
FROM red_flags rf
JOIN flag_rules fr ON fr.id = rf.flag_type
WHERE rf.zmluva_id = 12345 AND fr.severity = 'danger';

-- Departments with most danger flags
SELECT z.rezort, count(*) AS cnt
FROM red_flags rf
JOIN flag_rules fr ON fr.id = rf.flag_type
JOIN zmluvy z ON z.id = rf.zmluva_id
WHERE fr.severity = 'danger'
GROUP BY z.rezort ORDER BY cnt DESC LIMIT 10;
```

## Notes

¹ **`nace_mismatch` — grant/dotácia exclusion:** Contracts whose name contains
grant-related keywords (`dotác`, `príspev`, `grant`, `NFP`, `nenávratn`,
`transferov`) are excluded from this flag. Grants and subsidies are received by
entities (sports clubs, municipalities, NGOs) that delegate actual work to
subcontractors — the recipient's NACE code is irrelevant to the contracted
activity. Without this exclusion the flag had a very high false positive rate
(e.g. a sports club receiving a grant for stadium reconstruction flagged because
NACE 93/sports doesn't match `construction_renovation`).
