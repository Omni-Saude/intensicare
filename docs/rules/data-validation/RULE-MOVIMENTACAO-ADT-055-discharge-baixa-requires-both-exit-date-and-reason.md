# RULE-MOVIMENTACAO-ADT-055 — Discharge (baixa) requires BOTH exit date and reason

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Discharging a patient requires both data_saida (exit date) AND motivo_baixa (reason). Enforced identically in the backend (MovimentacaoBaixaViewSet.create raises ValidationError under key 'baixa_leito' if either is missing) and in the frontend removal form (both fields marked required). The two implementations agree.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| data_saida | date/datetime, required |  |  |
| motivo_baixa | string, required |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| eligible_for_baixa / valid discharge | boolean |  |

## Logic
```text
# BACKEND (core/api/v1/views/movimentacao.py:88-111):
data_saida = request.data.get("data_saida")
motivo = request.data.get("motivo_baixa")
if not (data_saida and motivo):
    raise ValidationError({"baixa_leito": "obrigatorio o envio da data_saida e motivo"})
BaixaMovimentacao(movimentacao=kwargs["movimentacoes__pk"], data_saida=data_saida,
                   movito_baixa=motivo, encerrado_por=request.user)
return Response({"success": "sucesso na baixa da movimentacao"})

# FRONTEND (src/utils/dataForms/dataFormRemovePaciente.ts:1-22):
required: data_saida (type "data", showTime=true), motivo_baixa (string)
```

## Edge cases (as implemented)
Both fields required simultaneously (AND, not OR). The BaixaMovimentacao call uses a keyword argument literally named 'movito_baixa' (typo preserved verbatim). Frontend performs no validation of data_saida vs admission date.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/movimentacao.py` | 88-111 | `8166c07e` | primary |
| trilhas-frontend | `src/utils/dataForms/dataFormRemovePaciente.ts` | 1-22 | `f9656be2` | frontend-copy |

- Merged from: RULE-movimentacao-BE-05-003, RULE-patient-FE-01-006
- Related rules: RULE-MOVIMENTACAO-ADT-031

## Notes
BE/FE reconciled and VERIFIED to agree (both require data_saida + motivo_baixa) - no divergence. permission_trilhas=('can_remove_paciente',) on the BE viewset. FE removal form's exported const is confusingly named dataFormPaciente though it is the removal form.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
