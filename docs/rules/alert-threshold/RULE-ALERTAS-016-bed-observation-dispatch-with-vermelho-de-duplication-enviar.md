# RULE-ALERTAS-016 — Bed observation dispatch with VERMELHO de-duplication (enviar_observacao_leito)

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
Decides whether to push an automated criteria observation for a bed. If the previous alert was not VERMELHO, send whenever there is content; if the previous alert was VERMELHO, send only when the current criteria content differs from the last stored one (suppress duplicates while already red).

## Inputs

- leito (object; tipo in {automatica, homecare, ...})
- alerta_antigo (VERMELHO | other)

## Outputs

- side_effect (dispatch)

## Logic

```text
exclude = {"conteudo": []}
if leito.tipo == "automatica": exclude["paciente_automatica"] = {}
elif leito.tipo == "homecare": exclude["paciente_homecare"] = {}
if alerta_antigo != "VERMELHO":
    conteudo = conteudo_observacao_criterios(leito)
    if conteudo: Mensageiro().enviar_observacao_automatica_e_homecare(leito, conteudo)
else:  # was VERMELHO
    conteudo_atual = conteudo_observacao_criterios(leito)
    conteudo_anterior = Observacao.objects.filter(leito=leito, texto__isnull=True).exclude(**exclude).order_by("-criado_em").first()
    if conteudo_anterior and conteudo_atual and conteudo_anterior.conteudo != conteudo_atual:
        Mensageiro().enviar_observacao_automatica_e_homecare(leito, conteudo_atual)
```

## Edge cases (as implemented)

Non-VERMELHO path sends on any truthy content. VERMELHO path requires BOTH a prior observation AND current content AND that they differ (change detection) - suppresses repeat identical red alerts. 'anterior' query excludes rows with texto NOT null (only auto/criteria observations) and excludes the current-type paciente/conteudo fields.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 163-190 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ALERT-BE-12-011`

**Related rules:**

- [RULE-ALERTAS-014](RULE-ALERTAS-014-conteudo-observacao-criterios-tipo-dependent-whitelist-filte.md)
- [RULE-ALERTAS-019](../care-pathway/RULE-ALERTAS-019-mensageiro-enviar-observacao-automatica-e-homecare-hardcoded.md)

## Notes

De-dup logic prevents alert spam while a bed remains red; content change re-notifies. Currently invoked only from commented-out code in get_alerta_leito (RULE-ALERTAS-006).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
