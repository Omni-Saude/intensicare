# RULE-BALANCO-HIDRICO-022 — Presence-level to volume mapping for evacuacao/vomito outputs

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: none |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
For evacuation or gastric-tube vomit/return outputs, the recorded "presenca" qualitative level ("presente+" / "presente++" / "presente+++") is converted to a fixed default volume of 100 / 200 / 300 respectively — but the guarding condition has an operator-precedence bug that changes which tipos are gated by "presenca" being truthy.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | — | — | — |
| presenca | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| quantidade | mL (assumed) | — |

## Logic
```text
presenca = validated_data.presenca
# AS WRITTEN (Python operator precedence: `and` binds tighter than `or`):
#   condition = (presenca AND tipo == "evacuacao") OR (tipo == "vomito_retorno_sonda")
if presenca and tipo == "evacuacao" or tipo == "vomito_retorno_sonda":
    if presenca == "presente+":
        quantidade = 100
    elif presenca == "presente++":
        quantidade = 200
    elif presenca == "presente+++":
        quantidade = 300
```

## Edge cases (as implemented)
Because of the precedence bug, any record with tipo == "vomito_retorno_sonda" enters the mapping block even when presenca is null/blank (falling through all elif branches with no quantidade change), while an "evacuacao" record with a falsy presenca never enters the block at all — even though the evident intent (given the identical presenca choices apply to both tipos) was likely `presenca and (tipo == "evacuacao" or tipo == "vomito_retorno_sonda")`.

## Divergence
Operator-precedence: `if presenca and tipo == 'evacuacao' or tipo == 'vomito_retorno_sonda'` parses (Python: and binds tighter than or) as (presenca AND tipo=='evacuacao') OR (tipo=='vomito_retorno_sonda'). Consequence: a vomito_retorno_sonda record enters the presente+/++/+++ -> 100/200/300 mapping block even when presenca is null/blank (falls through all elif with no change), while an evacuacao record with falsy presenca never enters the block. Evident intent was `presenca and (tipo == 'evacuacao' or tipo == 'vomito_retorno_sonda')`. Recorded verbatim, not corrected.

## Verification
- Verdict: DISCREPANCY (impact: none)
- Reference: No authoritative published source for the presente+/++/+++ -> 100/200/300 mL volume mapping (arbitrary institutional semiquantitative estimate). The extraction-flagged defect is an internal code-vs-intent operator-precedence issue, verifiable by hand-tracing the Python logic itself. (n/a)
- Test vectors: 4/4 match
- Extraction status DISCREPANCY confirmed as a genuine operator-precedence defect in the guard expression (characterized, not dismissed, per instructions). HOWEVER hand-tracing every branch shows the defect is BENIGN for the computed volume: quantidade is only ever assigned inside the `elif presenca=='presente+/++/+++'` branches, which require presenca to be truthy; entering the outer block spuriously (a vomito_retorno_sonda with falsy presenca) matches no elif and changes nothing. Thus in every input case the emitted volume is identical to the evident-intent parse `presenca and (tipo=='evacuacao' or tipo=='vomito_retorno_sonda')`. Latent/cosmetic code smell, no observed output divergence -> clinical impact none. Separately, the 100/200/300 mL constants themselves have no authoritative clinical source (institutional semiquantitative estimate) and are UNVERIFIABLE clinically.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/saidas.py | 96-103 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-07-009
- Related rules: RULE-BALANCO-HIDRICO-021, RULE-BALANCO-HIDRICO-031

## Notes
Recorded verbatim per instructions — the discrepancy is the exact operator precedence of `presenca and tipo == "evacuacao" or tipo == "vomito_retorno_sonda"`, which a naive reading might assume applies the `presenca` gate to both tipos.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
