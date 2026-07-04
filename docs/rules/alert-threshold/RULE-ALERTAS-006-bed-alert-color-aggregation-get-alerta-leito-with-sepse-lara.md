# RULE-ALERTAS-006 — Bed alert color aggregation (get_alerta_leito, with sepse LARANJA override)

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
Computes a bed's overall alert color from its pathway alerts; an interactive sepse alert of LARANJA (automatic beds) takes top priority, else VERMELHO > AMARELO > NEUTRO among un-attended pathways.

## Inputs

- pathway alerts (list[str] VERMELHO|AMARELO|NEUTRO|LARANJA)
- tipo (bed: homecare|automatica)

## Outputs

- alerta (string)

## Logic

```text
Trilhas = homecare set if tipo==homecare, automatic set if tipo==automatica,
          else raise ValidationError.
alerta = ""; trilhas = []
for each pathway Trilha (latest via get_trilha(Trilha, self, self.tipo)):
  if trilha:
    if trilha.alerta in ("VERMELHO","AMARELO") and trilha.assistido is False:
        trilhas.append(trilha.alerta)
    if trilha.tipo == "sepse" and self.tipo == "automatica":
        alerta = trilha.alerta_trilha_interativa
if alerta != "LARANJA":
    if "VERMELHO" in trilhas: alerta = "VERMELHO"
    elif "AMARELO" in trilhas: alerta = "AMARELO"
    else: alerta = "NEUTRO"
return alerta
```

## Edge cases (as implemented)

Only un-attended (assistido is False) VERMELHO/AMARELO pathways count toward escalation. LARANJA (interactive sepse) is preserved and overrides everything. Called from Leito.save (only when ocupado) storing into Leito.alerta.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 246-280 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-BE-04-013`

**Related rules:**

- [RULE-ALERTAS-005](RULE-ALERTAS-005-bed-level-alert-rollup-util-define-tipo-alerta-leito-dead-co.md)
- [RULE-ALERTAS-007](RULE-ALERTAS-007-automatic-bed-alert-ignoring-attendance-alerta-nao-assistido.md)
- [RULE-ALERTAS-010](RULE-ALERTAS-010-automatic-bed-payload-alert-attendance-flag.md)

## Notes

get_trilha (utils/trilha.py) fetches the latest pathway record by nr_atendimento. LARANJA is a fourth color beyond the {VERMELHO,AMARELO,NEUTRO} triad used elsewhere. Contains a commented-out call to enviar_observacao_leito (RULE-ALERTAS-016) with a "!TODO verificar POR QUE ENVIA TODA VEZ" note.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
