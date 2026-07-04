# RULE-PRESCRICAO-007 — Prescription-item type priority ordering (5-tier)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Prescription items are grouped/ordered by a fixed 5-tier priority on their Tasy item-type classification (DS_TIPO_ITEM_PRESCR): diet, then medication/solution, then PRN (SN_ACM), then nursing recommendations, then general recommendations; any other type gets a NULL priority. The same formula is applied in the printable PDF serializer annotation and in the interactive continuous-prescription listing view, which diverge in soft-delete handling and secondary sort.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| DS_TIPO_ITEM_PRESCR | enum |  | DIETA\|MEDICAMENTO_SOLUÇÃO\|SN_ACM\|RECOMENDACAO_ENFERMAGEM\|RECOMENDACAO\|<other> |

## Outputs

| Name | Type | Unit |
|---|---|---|
| prioridade | integer\|null |  |
| ordering | queryset |  |

## Logic

```text
# 5-tier priority by Tasy item type (DS_TIPO_ITEM_PRESCR), no Case(default=...):
prioridade = CASE
  WHEN DS_TIPO_ITEM_PRESCR = 'DIETA'                   THEN 1
  WHEN DS_TIPO_ITEM_PRESCR = 'MEDICAMENTO_SOLUCAO'     THEN 2   # 'MEDICAMENTO_SOLUÇÃO'
  WHEN DS_TIPO_ITEM_PRESCR = 'SN_ACM'                  THEN 3
  WHEN DS_TIPO_ITEM_PRESCR = 'RECOMENDACAO_ENFERMAGEM' THEN 4
  WHEN DS_TIPO_ITEM_PRESCR = 'RECOMENDACAO'            THEN 5
  ELSE NULL
END
# PDF/serializer variant (horario_prescricao.py 357-383):  .order_by("prioridade")
# Interactive-listing view (views/prescricao.py 15-53):     PrescricaoContinua.objects   # NOT objects_without_deleted
#                                                            .order_by("prioridade", "criado_em")
```

## Edge cases (as implemented)
No Case(default=...) so unmatched item types get prioridade=NULL; the sort position of NULL vs 1-5 is DB-dependent (PostgreSQL sorts NULLs last on ascending order by default) and not explicitly controlled.

## Divergence
Same 5-tier CASE formula, divergent surrounding query behaviour: (a) SOFT-DELETE - the interactive listing view (views/prescricao.py 15-53) uses the plain PrescricaoContinua.objects manager, so SOFT-DELETED prescriptions REMAIN in the list, whereas the PDF path is used in an objects_without_deleted context; (b) SECONDARY SORT - the listing adds 'criado_em' as a deterministic tiebreaker after 'prioridade', the PDF serializer orders by 'prioridade' only. A third byte-identical application exists in the PDF-export view (RULE-pdf-BE-08-040, different partition / not in this cluster; excludes soft-deleted, no secondary sort).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/prescricao.py` | 15-53 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 357-383 | `8166c07e` | duplicate |

**Merged from:**

- RULE-prescricao-BE-07-013
- RULE-prescricao-BE-08-043

## Notes
Merged the two in-cluster applications of the shared item-type priority formula. Status DISCREPANCY (BE-08-043) dominates the AMBIGUOUS NULL-ordering note from BE-07-013. Third instance RULE-pdf-BE-08-040 lives in another partition and is only cross-referenced in text.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
