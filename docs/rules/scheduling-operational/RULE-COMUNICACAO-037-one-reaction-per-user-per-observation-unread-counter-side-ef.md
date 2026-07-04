# RULE-COMUNICACAO-037 — One reaction per user per observation + unread-counter side effect

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | scheduling-operational |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A user may have at most one reaction on a given observation; saving/deleting a reaction adjusts Firebase unread-message counters.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| observacao | Observacao FK |  |  |
| usuario | Usuario FK |  |  |
| emoji | string |  | sorriso\|choro\|aprovacao\|reprovacao\|forca\|gratidao\|coracao |

## Outputs

| name | type | unit |
|---|---|---|
| Reacao (unique) + firebase counter | side-effect |  |

## Logic

```text
unique_together(observacao, usuario).
_trigger_firebase(): if reduzir_qtd(observacao):
    send_qtd_mensagens_to_firebase(setor.pk, responsavel.pk, False, True)
  else:
    send_qtd_mensagens_to_firebase(setor.pk, responsavel.pk, True)
Called on both save() and delete().
```

## Edge cases (as implemented)

Counter side-effect fires on every save and delete (idempotency depends on reduzir_qtd).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/reacao.py` | 8-43 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-reacao-BE-04-029`

**Related rules:**

- [RULE-COMUNICACAO-001](../data-validation/RULE-COMUNICACAO-001-reaction-count-by-emoji-aggregation-sql-correct-vs-order-dep.md)
- [RULE-COMUNICACAO-002](../data-validation/RULE-COMUNICACAO-002-current-user-s-own-reaction-id-on-an-observation.md)
- [RULE-COMUNICACAO-038](../data-validation/RULE-COMUNICACAO-038-reaction-usuario-observacao-always-server-injected.md)
- [RULE-COMUNICACAO-036](../data-validation/RULE-COMUNICACAO-036-chat-feed-emoji-reaction-enumeration.md)
- [RULE-COMUNICACAO-004](../alert-threshold/RULE-COMUNICACAO-004-send-qtd-mensagens-to-firebase-per-user-unread-message-count.md)
- [RULE-COMUNICACAO-005](../alert-threshold/RULE-COMUNICACAO-005-reduzir-qtd-mensageiro-eligibility-to-decrement-an-observati.md)

## Notes

Emoji enum from ReacaoChoices.emoji().

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
