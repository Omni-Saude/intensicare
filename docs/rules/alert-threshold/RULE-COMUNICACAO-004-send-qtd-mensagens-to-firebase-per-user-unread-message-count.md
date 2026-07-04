# RULE-COMUNICACAO-004 — send_qtd_mensagens_to_firebase — per-user unread-message counter fanout

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
For every user belonging to a setor, updates that user's Firestore unread-message-count document. If the event is a 'reacao' (reaction), only the updated-at timestamp is bumped for every user (count unchanged). If reduzir_qtd=True, every user's count is decremented by 1, floored at 0, with timestamp bumped. Otherwise (a normal new-message event): the user matching usuario_pk (i.e. the sender) keeps their count unchanged (with no timestamp bump); every OTHER user in the setor has their count incremented by 1 with the timestamp bumped.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| setor | Setor pk | — | — |
| usuario_pk | user pk (string) | — | — |
| is_reacao | boolean | — | default False |
| reduzir_qtd | boolean | — | default False |

## Outputs
| Name | Type | Unit |
|---|---|---|
| firestore doc per user | {qtd_mensagens: int, atualizado_em?: timestamp, usuario: {...}} | — |

## Logic
```text
FOR usuario IN Setor.objects.get(pk=setor).usuarios.all():
  payload = doc_ref.get().to_dict() OR {}
  IF is_reacao:
    message_payload = {"atualizado_em": SERVER_TIMESTAMP}
  ELIF reduzir_qtd:
    current = payload.get("qtd_mensagens", 0)
    message_payload = {
      "atualizado_em": SERVER_TIMESTAMP,
      "qtd_mensagens": (current - 1) IF current > 0 ELSE 0,
    }
  ELSE:
    IF usuario_pk == str(usuario.pk):
      message_payload = {"qtd_mensagens": payload.get("qtd_mensagens", 0)}   # unchanged, no timestamp bump
    ELSE:
      message_payload = {
        "qtd_mensagens": payload.get("qtd_mensagens", 0) + 1,
        "atualizado_em": SERVER_TIMESTAMP,
      }
  data_payload = {**message_payload, "usuario": {id, nome, foto_perfil url or "", email}}
  doc_ref.set(data_payload) IF NOT payload ELSE doc_ref.update(data_payload)
```

## Edge cases (as implemented)
Decrement is floored at 0 (never negative). The is_reacao and reduzir_qtd branches apply identically to ALL users in the setor regardless of usuario_pk (the sender-exclusion logic only exists in the 'else'/new-message branch).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | utils/firebase.py | 19-75 | 8166c07e | primary |
- Merged from: RULE-msg-BE-11-045
- Related rules: RULE-COMUNICACAO-005, RULE-COMUNICACAO-006, RULE-COMUNICACAO-007, RULE-COMUNICACAO-023, RULE-COMUNICACAO-037

## Notes
Called from Mensageiro.enviar_observacao/enviar_observacao_automatica_e_homecare (RULE-alert-BE-11-047/048) and referenced by reduzir_qtd (RULE-msg-BE-11-046) which computes the reduzir_qtd flag's eligibility.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
