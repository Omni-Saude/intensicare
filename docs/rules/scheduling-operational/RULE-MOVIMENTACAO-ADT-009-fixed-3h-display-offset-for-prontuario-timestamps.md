# RULE-MOVIMENTACAO-ADT-009 — Fixed -3h display offset for prontuario timestamps

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Historical prontuario data timestamps are shifted by -3 hours before formatting for display.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dados.criado_em | datetime |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| data label | string, "%Y-%m-%d %H:%M" |  |

## Logic
```text
for each prior prontuario record: label = strftime(dados.criado_em - timedelta(hours=3), "%Y-%m-%d %H:%M")
```

## Edge cases (as implemented)
Hardcoded 3-hour subtraction (Brazil UTC-3) rather than a timezone conversion; would be wrong during daylight-saving periods or in other regions.

## Divergence
Naive fixed -3h offset vs proper tz-aware conversion (single-implementation defect). Recorded verbatim.

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: IANA tz database (America/Sao_Paulo) and Brazil DST law: DST permanently abolished 2019 (Decreto 9.772/2019, eff. Apr 2019); Brasilia Time = UTC-3 year-round since 2019, previously UTC-2 during summer DST (mid-Oct to mid-Feb).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/movimentacao.py | 105-119 | 8166c07e | primary |
- Merged from: RULE-movimentacao-BE-04-025
- Related rules: RULE-MOVIMENTACAO-ADT-039

## Notes
Verified at core/models/movimentacao.py montar_list_ultimos_dados (criado_em - timedelta(hours=3)).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
