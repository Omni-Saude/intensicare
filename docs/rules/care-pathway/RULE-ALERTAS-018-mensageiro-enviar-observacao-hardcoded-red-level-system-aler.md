# RULE-ALERTAS-018 — Mensageiro.enviar_observacao - hardcoded RED-level system alert + system-user auto-provisioning

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
Creates an Observacao (clinical note/alert) for a movimentacao that is ALWAYS alerta='VERMELHO' (RED), regardless of underlying pathway data, with content built by conteudo_trilha_criterios(movimentacao) (RULE-ALERTAS-012). The responsible user is a singleton system account (username='sistema'), auto-created with a hardcoded email and password if it does not already exist. After creation, triggers an async Firebase unread-count fanout for the setor.

## Inputs

- movimentacao (Movimentacao instance)

## Outputs

- Observacao (created model row, alerta='VERMELHO')

## Logic

```text
TRY: usuario = Usuario.objects.get(username="sistema")
EXCEPT Usuario.DoesNotExist:
  usuario = Usuario.objects.create(username="sistema", email="sistema@omnisaude.co", password="sis_info")
Observacao.objects.create(
  responsavel_id=usuario.id, setor_id=movimentacao.leito.setor.id,
  movimentacao_id=movimentacao.id, leito_id=movimentacao.leito.id,
  paciente_id=movimentacao.paciente.id, alerta="VERMELHO", texto=None,
  conteudo=conteudo_trilha_criterios(movimentacao))
send_qtd_mensagens_to_firebase.apply_async(args=[str(movimentacao.leito.setor.pk), str(usuario.id)])
```

## Edge cases (as implemented)

The system user's 'password' is passed directly to Usuario.objects.create as a plain literal ('sis_info') rather than through a password-hashing helper (e.g. create_user/set_password) - as written, this would store the literal string as the password field value, not a hashed credential (a security-relevant observation, not a formula error, recorded verbatim).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/mensageiro.py` | 10-27, 29-48 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alert-BE-11-047`

**Related rules:**

- [RULE-ALERTAS-012](../alert-threshold/RULE-ALERTAS-012-conteudo-trilha-criterios-red-alert-content-extraction-for-m.md)
- [RULE-ALERTAS-019](RULE-ALERTAS-019-mensageiro-enviar-observacao-automatica-e-homecare-hardcoded.md)

## Notes

Every system-generated observation from this path is unconditionally RED; there is no code path here to generate a lower-severity system alert. Flag the plaintext-looking password literal for the rebuild's auth design.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
