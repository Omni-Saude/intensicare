# RULE-OPERACIONAL-INFRA-020 — Offline evolution forms visible if authored by the requesting user OR marked 'liberado'

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

EvolucoesOfflineSerializer.get_evolucoes, for each professional-role form type (medico, tecnico_enfermagem, enfermagem, fisioterapeuta, musicoterapeuta, nutricionista, psicologo, fonoaudiologo, farmaceutico, intercorrencia), returns the most recent qualifying Formulario ('anterior_indicadores') plus up to 2 most recent as 'historico'. A form qualifies for a given bed/atendimento if the requesting user authored it (preenchido_por=user) OR it has been released (status='liberado') - draft forms authored by OTHER users are invisible to this user.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.user | object | - | - |
| instance.nr_atendimento | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| evolucoes[tipo].anterior_indicadores | object \| null | - |
| evolucoes[tipo].historico | array (max 2) | - |

## Logic

```text
for tipo, Serializer in tipo_serializer_map.items():
    formularios = Formulario.objects.filter(
        Q(leito=instance, tipo=tipo, nr_atendimento=instance.nr_atendimento),
        (Q(preenchido_por=user) | Q(status="liberado"))
    ).order_by("-modificado_em")
    formulario_anterior = formularios.first()
    payload[tipo] = {
        "anterior_indicadores": Serializer(formulario_anterior, context=context).data if formulario_anterior else None,
        "historico": Serializer(formularios[:2], many=True, context=context).data,
    }
```

## Edge cases (as implemented)

'historico' can include the same record as 'anterior_indicadores' (formularios[:2] re-slices the same ordered queryset from the top, does not exclude the first record).

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/dados_offline.py` | 100-150 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-003

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
