# RULE-PRESCRICAO-033 — Horario prescricao scoped to parent prescricao continua

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Prescription-schedule-slot (HorariosPrescricao) records are only listable/retrievable when scoped to their parent continuous prescription id from the nested route, excluding soft-deleted rows.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| prescricoes__pk (URL kwarg) | uuid |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | queryset |  |

## Logic
```text
HorariosPrescricao.objects_without_deleted
  .select_related("prescricao_continua")
  .filter(prescricao_continua_id=kwargs["prescricoes__pk"])
```

## Edge cases (as implemented)
Uses objects_without_deleted (excludes soft-deleted), unlike Entrada/Saida/SinaisVitais viewsets.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/horario_prescricao.py` | 30-34 | `8166c07e` | primary |

- Merged from: RULE-prescricao-BE-08-032
- Related rules: RULE-PRESCRICAO-022

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
