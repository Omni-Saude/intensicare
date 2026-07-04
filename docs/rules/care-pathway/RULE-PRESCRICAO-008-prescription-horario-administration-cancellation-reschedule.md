# RULE-PRESCRICAO-008 — Prescription horario administration/cancellation/reschedule state machine

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Updating a scheduled prescription dose (HorariosPrescricao) branches into one of four mutually exclusive flows depending on which fields are present in the request, each producing a different combination of side effects (checador assignment, digital signature attempt, cancellation bookkeeping, or a simple reschedule), and each is logged as a distinct action.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| validated_data.administrado | boolean (nullable) |  |  |
| validated_data.motivo_nao_administrado | string (nullable) |  |  |
| validated_data.justificativa_cancelamento | string (nullable) |  |  |
| validated_data.horario | string "HH:MM" (nullable) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| acoes | list[string] |  |
| instance fields (checado_por, cancelado_por, assinatura, motivo_nao_administrado, alterado_por) | mixed |  |

## Logic

```text
if administrado is False and motivo_nao_administrado:
    validar_motivo(validated_data)
    checado_por = user
    validar_realizar_assinatura_cryptocubo(user, instance, "horario_prescricao")
    acoes = ["nao_administrar"] + (["assinar"] if instance.assinatura else [])
elif administrado is False and justificativa_cancelamento:
    validar_cancelamento(instance, validated_data, user)  # only original checador may cancel
    cancelado_por = user
    checado_por = None
    motivo_nao_administrado = None
    assinatura = None
    AssinaturaCryptocubo.objects.filter(horarios_prescricao=instance).update(ativo=False)
    acoes = ["cancelar"]
elif horario:  # reschedule
    alterado_por = user
    acoes = ["alterar"]
    if administrado:
        checado_por = user
        validar_realizar_assinatura_cryptocubo(user, instance, "horario_prescricao")
        acoes += ["administrar"] + (["assinar"] if instance.assinatura else [])
else:  # bare "administrado" checkbox
    checado_por = user
    validar_realizar_assinatura_cryptocubo(user, instance, "horario_prescricao")
    acoes = ["administrar"]
if qtd_exportada:
    exportar_prescricao(qtd_exportada, instance, validated_data)  # see RULE-prescricao-BE-07-010
criar_acao_da_prescricao(acoes, instance)
horario_obj = super().update(instance, validated_data)
if horario_obj.assinatura:
    enviar_arquivo_amhdocs.apply_async(args=[
        horario_obj.prescricao_continua.prescricao.NR_ATENDIMENTO,
        {"pdf_base64": ..., "categoria": "PRHC", "dia": str(horario_obj.prescricao_continua.dia),
         "data_arquivo": horario_obj.modificado_em.astimezone().isoformat(timespec="seconds")},
        "vida-conecta-prescricao-balanco",
    ])
```

## Edge cases (as implemented)
Branch order matters: administrado=False with BOTH motivo_nao_administrado and justificativa_cancelamento present would only ever hit the first (nao_administrar) branch, since elif short-circuits. The cancellation branch explicitly deactivates ALL AssinaturaCryptocubo rows tied to the instance (ativo=False), effectively revoking any prior signature. The final "if horario_obj.assinatura" re-send to AMH Docs happens for ALL branches that leave a signature in place, not just the "administrar" ones.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 194-277 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-07-006

**Related rules:**

- RULE-PRESCRICAO-034
- RULE-PRESCRICAO-035
- RULE-PRESCRICAO-036
- RULE-PRESCRICAO-029
- RULE-PRESCRICAO-021
- RULE-PRESCRICAO-025
- RULE-PRESCRICAO-028

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
