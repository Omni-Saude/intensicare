# RULE-BALANCO-HIDRICO-021 — Default volume for spontaneous presence output

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | threshold |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
When creating a fluid-balance "saida" (output) record whose presenca_espontanea equals "presente" (spontaneous presence), the quantity is defaulted to 200.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| presenca_espontanea | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| quantidade | mL (assumed) | — |

## Logic
```text
if validated_data.presenca_espontanea == "presente":
    validated_data.quantidade = 200
```

## Edge cases (as implemented)
Applied unconditionally on tipo; overwrites any client-supplied quantidade.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published source. Internal business default: when a spontaneous output (presenca_espontanea=='presente') is recorded without measurement, volume is hard-coded to 200 mL. Arbitrary institutional estimate, not derived from any clinical guideline or validated calculator. (n/a)
- Test vectors: 3/3 match
- Internal default-volume business rule (saidas.py:94-95). Confirmed against legacy source: `if validated_data.get('presenca_espontanea')=='presente': validated_data['quantidade']=200`. It unconditionally overwrites any client-supplied quantidade (edge case worth internal review), but there is no external clinical reference against which 200 mL can be validated. Flag for internal/institutional review, not a clinical error.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/saidas.py | 94-95 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-07-008
- Related rules: RULE-BALANCO-HIDRICO-020, RULE-BALANCO-HIDRICO-022, RULE-BALANCO-HIDRICO-031

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
