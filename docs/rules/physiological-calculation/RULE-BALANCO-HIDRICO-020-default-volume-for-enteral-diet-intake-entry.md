# RULE-BALANCO-HIDRICO-020 — Default volume for enteral diet intake entry

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | threshold |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
When creating a fluid-balance "entrada" (intake) record of type "dieta_enteral" (enteral tube feeding) without an explicit quantity, the system defaults the volume to 200 (presumably mL).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | — | — | — |
| quantidade | mL (assumed) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| quantidade | mL (assumed) | — |

## Logic
```text
if validated_data.tipo == "dieta_enteral" and not validated_data.quantidade:
    validated_data.quantidade = 200
```

## Edge cases (as implemented)
Only triggers when quantidade is falsy (None, 0, "", missing) AND tipo is exactly "dieta_enteral"; any other tipo without a quantidade falls through to the generic zero-fallback (RULE-balanco-BE-07-002).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Internal serializer default: entrada tipo=='dieta_enteral' with falsy quantidade -> quantidade=200 (assumed mL). No clinical guideline (e.g. ASPEN enteral nutrition) prescribes a fixed 200 mL charting default; this is a data-entry convenience value. (n/a)
- Test vectors: 4/4 match
- Internal business rule (default charting volume) with no published clinical source to verify; flag for internal
review, not treated as wrong. Only fires when quantidade is falsy AND tipo is exactly 'dieta_enteral'. Unit (mL)
is assumed, not asserted in code. Mirrors the presenca_espontanea=='presente' -> 200 default on Saida (RULE-...-021).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/entradas.py | 88-91 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-07-001
- Related rules: RULE-BALANCO-HIDRICO-021, RULE-BALANCO-HIDRICO-022, RULE-BALANCO-HIDRICO-029, RULE-BALANCO-HIDRICO-048

## Notes
Mirrors the "presenca_espontanea" default in Saida (RULE-balanco-BE-07-008), i.e. both intake and output serializers hardcode default volumes for specific entry subtypes.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
