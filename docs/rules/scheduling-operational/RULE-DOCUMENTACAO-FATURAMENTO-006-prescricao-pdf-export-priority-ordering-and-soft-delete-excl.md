# RULE-DOCUMENTACAO-FATURAMENTO-006 — Prescricao PDF export - priority ordering and soft-delete exclusion

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
The printed continuous-prescription list is ordered into 5 priority tiers by item type (excluding soft-deleted rows): DIETA first, then MEDICAMENTO_SOLUÇÃO, then SN_ACM, then RECOMENDACAO_ENFERMAGEM, then RECOMENDACAO. Items whose DS_TIPO_ITEM_PRESCR is none of these five values receive a null priority and are ordered by the database's default NULL ordering relative to the others. There is no secondary sort key (e.g. creation time).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| prescricao.DS_TIPO_ITEM_PRESCR | string (enum) |  | 'DIETA'|'MEDICAMENTO_SOLUÇÃO'|'SN_ACM'|'RECOMENDACAO_ENFERMAGEM'|'RECOMENDACAO'|other |

## Outputs
| Name | Type | Unit |
|---|---|---|
| prioridade | integer or null |  |

## Logic
```text
prioridade = CASE
  WHEN DS_TIPO_ITEM_PRESCR = 'DIETA' THEN 1
  WHEN DS_TIPO_ITEM_PRESCR = 'MEDICAMENTO_SOLUÇÃO' THEN 2
  WHEN DS_TIPO_ITEM_PRESCR = 'SN_ACM' THEN 3
  WHEN DS_TIPO_ITEM_PRESCR = 'RECOMENDACAO_ENFERMAGEM' THEN 4
  WHEN DS_TIPO_ITEM_PRESCR = 'RECOMENDACAO' THEN 5
  ELSE NULL
END
queryset = PrescricaoContinua.objects_without_deleted.select_related("prescricao")
             .filter(prescricao__NR_ATENDIMENTO=leito.nr_atendimento, dia=dia)
             .annotate(prioridade=...)
             .order_by("prioridade")
```

## Edge cases (as implemented)
Uses objects_without_deleted (soft-deleted prescriptions excluded from the printed PDF). No deterministic tiebreaker within the same priority tier - order among same-priority rows is database-dependent.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_prescricao.py | 29-52 | 8166c07e | primary |
- Merged from: RULE-pdf-BE-08-040
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-022, RULE-DOCUMENTACAO-FATURAMENTO-023, RULE-DOCUMENTACAO-FATURAMENTO-001

## Notes
Same priority-tier formula is duplicated in the interactive PrescricaoViewSet (RULE-prescricao-BE-08-043), but that variant (a) includes soft-deleted rows and (b) adds "criado_em" as a secondary, deterministic sort key.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
