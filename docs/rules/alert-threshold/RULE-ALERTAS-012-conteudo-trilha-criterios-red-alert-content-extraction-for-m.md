# RULE-ALERTAS-012 — conteudo_trilha_criterios - RED-alert content extraction for manual-trilha movimentacao

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
For a movimentacao's linked prontuario, inspects the 4 manual pathway objects (trilha_sepse, trilha_ventilacao, trilha_sedacao, trilha_estabilidade). For each whose alerta == 'VERMELHO' (RED), collects all criterio alert messages from its get_payload()['criterios'] and appends {criterios, trilha: nome} to the output list.

## Inputs

- movimentacao (object exposing .dados_prontuario.{trilha_sepse,trilha_ventilacao,trilha_sedacao,trilha_estabilidade})

## Outputs

- lista_conteudo (list of {criterios: [str], trilha: str})

## Logic

```text
objs = [trilha_sepse, trilha_ventilacao, trilha_sedacao, trilha_estabilidade]
lista_conteudo = []
FOR obj IN objs:
  IF obj.alerta == "VERMELHO":
    list_criterio = [msg.get("alerta","") FOR msg IN obj.get_payload()["criterios"]]
    lista_conteudo.append({"criterios": list_criterio, "trilha": obj.nome})
RETURN lista_conteudo
```

## Edge cases (as implemented)

Only 'VERMELHO' triggers inclusion; any other alerta value (e.g. AMARELO/VERDE, if they exist elsewhere) is silently excluded from this content builder.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 109-126 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alert-BE-11-035`

**Related rules:**

- [RULE-ALERTAS-013](RULE-ALERTAS-013-conteudo-trilha-automatica-criterios-red-alert-content-extra.md)
- [RULE-ALERTAS-014](RULE-ALERTAS-014-conteudo-observacao-criterios-tipo-dependent-whitelist-filte.md)
- [RULE-ALERTAS-015](RULE-ALERTAS-015-conteudo-trilha-homecare-criterios-red-alert-content-extract.md)
- [RULE-ALERTAS-018](../care-pathway/RULE-ALERTAS-018-mensageiro-enviar-observacao-hardcoded-red-level-system-aler.md)

## Notes

Used by Mensageiro.enviar_observacao (RULE-ALERTAS-018) to build the auto-generated Observacao content.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
