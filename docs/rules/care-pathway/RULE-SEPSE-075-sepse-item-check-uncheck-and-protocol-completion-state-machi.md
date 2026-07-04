# RULE-SEPSE-075 — SEPSE item check / uncheck and protocol completion state machine

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Checking a SEPSE item (transition not-checado -> checado) stamps horario_checagem=now and posts an item-specific documentation observation, appending a late-check flag when the item is overdue. Unchecking (checado -> not-checado) clears checado_por and horario_checagem. When an update checks an item and no unchecked items remain, the interactive trilha is concluded (finalizado=true, concluida=true, concluido_em=now, aceito=false) and the parent TrilhaSepseV3 is set assistido=true with alert cleared to null.

## Inputs

- instance.checado (boolean)
- validated_data.checado (boolean)
- instance.nome_item (enum, {solicitacao_exames, inicio_escalonamento_antimicrobiano, realizacao_expansao_volemica, exames, status_hemodinamico, dispositivos_invasivos, drogas_vasoativas})
- atraso_item_interativa (boolean)

## Outputs

- horario_checagem (datetime)
- trilha_interativa.concluida (boolean)
- alerta_trilha_interativa

## Logic

```text
agora = now()
if not instance.checado and validated_data.get("checado"):
    instance.horario_checagem = agora
    atraso_suffix = "- !! Item checado em atraso" if instance.atraso_item_interativa else ""
    # message template selected by nome_item:
    #   solicitacao_exames / inicio_escalonamento_antimicrobiano / realizacao_expansao_volemica
    #        -> "Intervencao realizada por <user @ ts><atraso>"
    #   exames               -> "Reavaliacao dos resultados de exames por <user @ ts>-<atraso>"
    #   status_hemodinamico  -> "Reavaliacao do status hemodinamico por <user @ ts>-<atraso>"
    #   dispositivos_invasivos -> "Reavaliacao dos dispositivos invasivos por<user @ ts>-<atraso>"
    #   drogas_vasoativas    -> "Reavaliacao das drogas vasoativas por <user @ ts>-<atraso>"
    post_observation(message, tipo_trilha="sepse", responsavel=checado_por_id)
elif instance.checado and not validated_data.get("checado"):
    instance.checado_por = None
    instance.horario_checagem = None
instance = super().update(instance, validated_data)
if validated_data.get("checado") and not instance.trilha_interativa.itens_trilha_interativa.filter(checado=False):
    ti = instance.trilha_interativa
    ti.finalizado = True; ti.concluida = True; ti.concluido_em = agora; ti.aceito = False; ti.save()
    TrilhaSepseV3Model.filter(pk=ti.trilha.get_pk).update(assistido=True, alerta_trilha_interativa=None)
    post_observation("Trilha interativa concluida e finalizada por <user @ ts>")
```

## Edge cases (as implemented)

Completion is evaluated AFTER super().update() persists the current item, so the just-checked item counts toward "no remaining unchecked". On completion aceito is forced False. create() of an item calls checagem_envio_automatico(item) (out of partition). checado_por_id is auto-set to the acting user upstream (RULE-sepse-BE-02-022).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/item_trilha_interativa_sepse.py` | 40-167 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-012`

**Related rules:**

- [RULE-SEPSE-069](../scheduling-operational/RULE-SEPSE-069-bundle-item-overdue-atraso-item-interativa-time-windows.md)
- [RULE-SEPSE-076](RULE-SEPSE-076-sepse-interactive-protocol-bundle-hour-1-vs-reassessment-ite.md)
- [RULE-SEPSE-077](RULE-SEPSE-077-sepse-item-checker-auto-attribution.md)
- [RULE-SEPSE-090](RULE-SEPSE-090-sepsis-protocol-lifecycle-state-display.md)
- [RULE-SEPSE-093](RULE-SEPSE-093-sepsis-pathway-dual-completion-flags.md)

## Notes

Note the message-string micro-differences between items (e.g. "por<user>" missing space for dispositivos_invasivos, "{msg}{atraso}" vs "{msg}-{atraso}" separators) are as-implemented.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
