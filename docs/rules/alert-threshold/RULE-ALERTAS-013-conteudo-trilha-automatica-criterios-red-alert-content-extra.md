# RULE-ALERTAS-013 — conteudo_trilha_automatica_criterios - RED-alert content extraction for automatic pathways

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
For a leito's automatic pathways (leito.get_trilhas_automaticas()), resolves each via get_trilha(trilha, leito, leito.tipo); for any resolved object with alerta == 'VERMELHO', collects ALL criterio alert messages (unconditionally, no whitelist filter) from get_detalhe()['criterios'] and appends {criterios, trilha: nome, tipo_trilha: tipo}.

## Inputs

- leito (Leito instance)

## Outputs

- lista_conteudo (list of {criterios: [str], trilha: str, tipo_trilha: str})

## Logic

```text
trilhas = leito.get_trilhas_automaticas()
objs = [get_trilha(trilha, leito, leito.tipo) FOR trilha IN trilhas IF get_trilha(...) is truthy]
lista_conteudo = []
FOR obj IN objs:
  IF obj.alerta == "VERMELHO":
    list_criterio = [msg.get("alerta","") FOR msg IN obj.get_detalhe()["criterios"]]
    lista_conteudo.append({"criterios": list_criterio, "trilha": obj.nome, "tipo_trilha": obj.tipo})
RETURN lista_conteudo
```

## Edge cases (as implemented)

Unlike conteudo_observacao_criterios (RULE-ALERTAS-014), there is no per-message whitelist filtering here - every criterio message of a RED pathway is included.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 129-148 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alert-BE-11-036`

**Related rules:**

- [RULE-ALERTAS-014](RULE-ALERTAS-014-conteudo-observacao-criterios-tipo-dependent-whitelist-filte.md)
- [RULE-ALERTAS-015](RULE-ALERTAS-015-conteudo-trilha-homecare-criterios-red-alert-content-extract.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
