# RULE-EVOLUCOES-029 — anterior_indicadores aggregation (previous form/vitals/24h indicators)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
The 'anterior_indicadores' GET action assembles a payload combining the patient, the most recent vital-signs record not in the future, the most recent Formulario of the same tipo for the encounter (WITHOUT the author/status visibility restriction used by the main list queryset), and six 24h rolling clinical indicators. On merge, keys from the freshly computed payload (paciente/indicadores_24h/sinais_vitais) override any same-named keys carried over from the previous form's serialized data.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| request.leito.nr_atendimento |  |  |  |
| now |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| payload.paciente |  |  |
| payload.indicadores_24h |  |  |
| payload.sinais_vitais |  |  |

## Logic
```text
now = datetime.now().astimezone()
qs = SinaisVitais.objects_without_deleted.filter(
       balanco__nr_atendimento=nr_atendimento, modificado_em__lte=now
     ).order_by("-modificado_em").first()
formulario_anterior = Formulario.objects.filter(
       tipo=tipo_formulario, nr_atendimento=nr_atendimento
     ).order_by("-modificado_em").first()          # NOTE: no preenchido_por/status filter here
if formulario_anterior:
    formulario_anterior = serializer_class(instance=formulario_anterior).data
    formulario_anterior.pop("sinais_vitais", None)
    formulario_anterior.pop("indicadores_24", None)
sinais = SinaisVitaisSimpleSerializer(qs).data if qs else None
indicadores_24h = {
  "evacuacoes_24h": evacuacoes_24h_evo(now, nr_atendimento),
  "diurese_24h": diureses_24h_evo(now, nr_atendimento),
  "ganhos_24h": ganhos_24h_evo(now, nr_atendimento),
  "temperatura_max_24h": temperatura_24h_evo(now, nr_atendimento),
  "hgt_24h": hgt_24h_evo(now, nr_atendimento),
  "balanco_24h": balanco_24h_evo(now, nr_atendimento),
}
payload = {"paciente": PacienteSerializer(request.leito.paciente).data,
           "indicadores_24h": indicadores_24h, "sinais_vitais": sinais}
if formulario_anterior:
    payload = {**formulario_anterior, **payload}
return Response(payload)
```

## Edge cases (as implemented)
formulario_anterior lookup can surface another user's still-unreleased (non-"liberado") draft form as "the previous form", which is inconsistent with the stricter visibility enforced by BaseFormViewSet.get_queryset() (RULE-formulario-BE-08-014). Requires `request.leito` / `request.setor` populated by out-of-partition mixins.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_base.py` | 92-140 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-016
- Related rules: RULE-EVOLUCOES-007, RULE-EVOLUCOES-047

## Notes
The six *_24h_evo() functions and get_visao_geral-style helpers live in trilha_homecare/utils.py, outside this partition's scope; only their names/call-signature and the assembly logic above are captured here.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
