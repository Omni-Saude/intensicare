# RULE-SINAIS-VITAIS-006 — SinaisVitais listing includes soft-deleted records

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | sinais-vitais |

## Rule
SinaisVitaisViewSet.get_queryset() uses the default SinaisVitais.objects manager (not objects_without_deleted), so soft-deleted vital-sign records are included in the listing. Identical pattern to the entrada/saida viewsets in the balanco cluster.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| balancos__pk (URL kwarg) | uuid |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | queryset |  |

## Logic
```text
SinaisVitais.objects.select_related("balanco")
  .filter(balanco_id=kwargs["balancos__pk"])
  .order_by("-deletado_em", "criado_em")
```

## Edge cases (as implemented)
Uses default manager instead of objects_without_deleted -> soft-deleted rows leak into the list. Same NULL-ordering caveat as the entrada viewset (deletado_em NULL ordering).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/sinais_vitais.py` | 29-35 | `8166c07e` | primary |

- Merged from: RULE-sinal-BE-08-048
- Related rules: RULE-SINAIS-VITAIS-007, RULE-SINAIS-VITAIS-008

## Notes
Cross-cluster analogues (balanco-hidrico): RULE-entrada-BE-08-010 and RULE-saida-BE-08-045 share the identical default-manager pattern.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
