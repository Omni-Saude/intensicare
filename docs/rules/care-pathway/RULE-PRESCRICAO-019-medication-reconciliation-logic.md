# RULE-PRESCRICAO-019 — Medication reconciliation logic

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Reconciliation captures high-risk medication classes, treatment adherence (low adherence requires a reason), admission-reconciliation decision and reconciliation completeness.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| medicamentos_uso | enum[] (multicheck) |  | see logic |
| adesao_tratamento | enum |  | baixa\|alta |

## Outputs

| Name | Type | Unit |
|---|---|---|
| reconciliation record | object |  |

## Logic

```text
medicamentos_uso multicheck {corticoides, analgesicos_tempo_prolongado, antibioticos_antifungicos,
  medicamentos_controlados, medicamentos_potencialmente_perigosos}
adesao_tratamento {baixa, alta}; baixa -> motivo_adesao_tratamento(string) required-if
paciente_conciliado_admissao {manter_prescricao_original, alterar_prescricao}
realizada_conciliacao_medicamentosa {parcial, total, nao_realizada, aguardando_informacoes}
```

## Edge cases (as implemented)
Only "baixa" adherence opens the reason field.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFarmaceutico.ts` | 462-539 | `f9656be2` | primary |

**Merged from:**

- RULE-pharma-FE-01-060

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
