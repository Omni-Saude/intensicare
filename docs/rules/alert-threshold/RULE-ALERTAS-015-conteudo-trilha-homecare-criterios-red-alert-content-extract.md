# RULE-ALERTAS-015 — conteudo_trilha_homecare_criterios - RED-alert content extraction for homecare pathways

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
For a leito's homecare pathways (leito.get_trilhas_homecare()), resolves each via get_trilha(trilha, leito, leito.tipo); for any resolved object with alerta == 'VERMELHO', collects ALL criterio alert messages (unconditionally) from get_detalhe()['criterios'] and appends {criterios, trilha: nome, tipo_trilha: tipo}.

## Inputs

- leito (Leito instance)

## Outputs

- lista_conteudo (list of {criterios: [str], trilha: str, tipo_trilha: str})

## Logic

```text
trilhas = leito.get_trilhas_homecare()
objs = [get_trilha(trilha, leito, leito.tipo) FOR trilha IN trilhas IF get_trilha(...) is truthy]
lista_conteudo = []
FOR obj IN objs:
  IF obj.alerta == "VERMELHO":
    list_criterio = [msg.get("alerta","") FOR msg IN obj.get_detalhe()["criterios"]]
    lista_conteudo.append({"criterios": list_criterio, "trilha": obj.nome, "tipo_trilha": obj.tipo})
RETURN lista_conteudo
```

## Edge cases (as implemented)

Structurally identical to conteudo_trilha_automatica_criterios (RULE-ALERTAS-013) but iterating homecare pathways instead of automatic ones.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 199-218 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alert-BE-11-038`

**Related rules:**

- [RULE-ALERTAS-013](RULE-ALERTAS-013-conteudo-trilha-automatica-criterios-red-alert-content-extra.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
