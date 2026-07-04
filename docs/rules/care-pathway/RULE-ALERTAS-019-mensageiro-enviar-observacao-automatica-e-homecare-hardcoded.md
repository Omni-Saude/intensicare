# RULE-ALERTAS-019 — Mensageiro.enviar_observacao_automatica_e_homecare - hardcoded RED alert with tipo-dependent patient FK

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Creates an Observacao for a leito (bed) that is ALWAYS alerta='VERMELHO', using the same system-user provisioning as RULE-ALERTAS-018. Additionally attaches a patient reference in a tipo-dependent field: leito.tipo=='homecare' sets paciente_homecare, leito.tipo=='automatica' sets paciente_automatica; neither is set for any other tipo.

## Inputs

- leito (Leito instance)
- conteudo (any alert content payload; optional, default None)

## Outputs

- Observacao (created model row, alerta='VERMELHO')

## Logic

```text
usuario = get_or_create_sistema_user()
payload = {
  "responsavel_id": usuario.id, "setor_id": leito.setor.id, "leito_id": leito.id,
  "paciente": leito.paciente OR None, "alerta": "VERMELHO", "texto": None, "conteudo": conteudo,
}
IF leito.tipo == "homecare": payload["paciente_homecare"] = leito.get_paciente_homecare
ELIF leito.tipo == "automatica": payload["paciente_automatica"] = leito.get_paciente_automatica
Observacao.objects.create(**payload)
send_qtd_mensagens_to_firebase.apply_async(args=[str(leito.setor.pk), str(usuario.id)])
```

## Edge cases (as implemented)

For leito.tipo not in {'homecare','automatica'} (e.g. 'manual'), neither paciente_homecare nor paciente_automatica is populated, relying solely on the generic 'paciente' key.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/mensageiro.py` | 50-75 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alert-BE-11-048`

**Related rules:**

- [RULE-ALERTAS-018](RULE-ALERTAS-018-mensageiro-enviar-observacao-hardcoded-red-level-system-aler.md)
- [RULE-ALERTAS-016](../alert-threshold/RULE-ALERTAS-016-bed-observation-dispatch-with-vermelho-de-duplication-enviar.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
