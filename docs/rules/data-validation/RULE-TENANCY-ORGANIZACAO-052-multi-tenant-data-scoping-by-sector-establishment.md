# RULE-TENANCY-ORGANIZACAO-052 — Multi-tenant data scoping by sector/establishment

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Read endpoints restrict rows to the caller's active tenant context. Indicator viewsets filter on both request.setor.codigo AND request.estabelecimento.codigo; the assinaturas-inconsistentes viewset filters on request.setor.codigo (ordered by data_item).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.setor.codigo | identifier |  |  |
| request.estabelecimento.codigo | identifier |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| queryset | filtered rows |  |

## Logic
```text
# indicadores_assistenciais / indicadores_controle_Infeccao:
IndicadoresAssistenciais.objects.filter(
    cd_setor_atendimento == request.setor.codigo,
    cd_estabelecimento   == request.estabelecimento.codigo)
# assinaturas_inconsistentes:
AssinaturasInconsistentesModel.objects.filter(
    cd_setor_atendimento == request.setor.codigo).order_by("data_item")
```

## Edge cases (as implemented)
request.setor / request.estabelecimento are injected by upstream middleware (out of partition). Interactive SEPSE viewsets instead scope by URL kwargs (trilhas__pk / trilha_interativa_sepse__pk).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/api/v1/views/indicadores_assistenciais.py | 22-26 | 8166c07e | primary |

- Merged from: RULE-sepse-BE-02-021

## Notes
Also indicadores_controle_Infeccao.py lines 22-26 and assinaturas_inconsistentes.py lines 24-27. assinaturas_inconsistentes filter supports date-range (data_inicio gte / data_fim lte on data_item) and icontains on leito/item/ds_paciente/ds_profissional.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
