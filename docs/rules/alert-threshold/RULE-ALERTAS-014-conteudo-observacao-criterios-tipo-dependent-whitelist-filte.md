# RULE-ALERTAS-014 — conteudo_observacao_criterios - tipo-dependent whitelist filter on RED-alert criteria, with a disabled sepse special case

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Builds alert content for a leito's pathways, branching by leito.tipo. For 'automatica', evaluates the 5 hardcoded v3 pathway models and only includes a criterio message if its 'nome' appears in the pathway object's own criterios_mensagem whitelist attribute; for any other tipo ('homecare'), ALL criterio messages of a RED pathway are included unconditionally, with no whitelist filter. A block of dead (commented-out) code shows a previously-active special case that would have added a fixed message 'Risco para SEPSE: realizar abertura do Protocolo Institucional' whenever a pathway's tipo == 'sepse' - currently disabled.

## Inputs

- leito (Leito instance)

## Outputs

- lista_conteudo (list of {criterios: [str], trilha: str, tipo_trilha: str}, only appended if non-empty)

## Logic

```text
tipo = leito.tipo
IF tipo == "automatica":
  trilhas = [TrilhaSedacaoV3Model, TrilhaEstabilidadeV3Model, TrilhaEficienciaV3Model,
             TrilhaProfilaxiaV3Model, TrilhaSepseV3Model]
  attr = "alerta"
ELSE:
  trilhas = leito.get_trilhas_homecare()
  attr = "alerta"
objs = [get_trilha(trilha, leito, leito.tipo) FOR trilha IN trilhas IF get_trilha(...) is truthy]
lista_conteudo = []
FOR obj IN objs:
  IF getattr(obj, attr) == "VERMELHO":
    list_criterio = []
    FOR msg IN obj.get_detalhe()["criterios"]:
      IF (tipo == "automatica" AND msg.get("nome") IN getattr(obj, "criterios_mensagem")) OR tipo == "homecare":
        list_criterio.append(msg.get("alerta", ""))
    IF list_criterio:
      lista_conteudo.append({"criterios": list_criterio, "trilha": obj.nome, "tipo_trilha": obj.tipo})
RETURN lista_conteudo
# DISABLED (commented out): IF obj.tipo == "sepse": list_criterio.append(
#   "Risco para SEPSE: realizar abertura do Protocolo Institucional")
```

## Edge cases (as implemented)

For tipo=='automatica', a RED pathway contributes NOTHING to the output if none of its criterio 'nome' values are present in criterios_mensagem (list_criterio stays empty and the whole entry is skipped by the `if list_criterio` guard), even though the underlying pathway is alerting RED.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 151-196 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alert-BE-11-037`

**Related rules:**

- [RULE-ALERTAS-013](RULE-ALERTAS-013-conteudo-trilha-automatica-criterios-red-alert-content-extra.md)
- [RULE-ALERTAS-015](RULE-ALERTAS-015-conteudo-trilha-homecare-criterios-red-alert-content-extract.md)
- [RULE-ALERTAS-016](RULE-ALERTAS-016-bed-observation-dispatch-with-vermelho-de-duplication-enviar.md)

## Notes

AMBIGUOUS/flag for verifier: the commented-out sepse-specific fixed alert message ('Risco para SEPSE: realizar abertura do Protocolo Institucional') indicates a previously intended (or previously live) sepsis protocol-opening prompt now inactive in this code path. Determine with product owner whether this was intentionally retired or accidentally disabled.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
