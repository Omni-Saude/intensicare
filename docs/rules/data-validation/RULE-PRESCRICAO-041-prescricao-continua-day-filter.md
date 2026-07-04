# RULE-PRESCRICAO-041 — Prescricao continua day filter

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Continuous-prescription records can be filtered by an exact-match 'dia' (day) query parameter via django-filter, wired into PrescricaoViewSet.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dia | date |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| filtered queryset | queryset |  |

## Logic
```text
class PrescricaoContinuaFilter(FilterSet):
    class Meta:
        model = PrescricaoContinua
        fields = ("dia",)
```

## Edge cases (as implemented)
Exact match only; no range/date-lookup support.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/filters/prescricao.py` | 9-12 | `8166c07e` | primary |

- Merged from: RULE-filtro-BE-08-003

## Notes
Used by trilha_homecare/api/v1/views/prescricao.py (filter_class = PrescricaoContinuaFilter).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
