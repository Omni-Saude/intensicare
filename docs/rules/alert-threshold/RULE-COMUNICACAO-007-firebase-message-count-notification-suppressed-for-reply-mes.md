# RULE-COMUNICACAO-007 — Firebase message-count notification suppressed for reply messages

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
When a new Observacao is created, a Firebase push/counter update is normally sent (incrementing the setor's unread count for the responsavel). However, if this new observation IS a reply to another (has 'resposta' set) AND reduzir_qtd() on the parent succeeds (meaning the reply already caused a counter decrement), the increment notification is SKIPPED - to avoid simultaneously incrementing and decrementing the same message-count total in Firebase.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| observacao.resposta | object \| null | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| firebase_notification_sent | boolean | — |

## Logic
```text
observacao = super().create(validated_data)   # validated_data["alerta"] <- popped "alerta_observacao"
for arquivo in arquivos_b64: ObservacaoArquivo.objects.create(...)
for checagem in checagens: ChecagemObservacao.objects.create(observacao=observacao, **checagem)
if not (observacao.resposta and reduzir_qtd(observacao.resposta, resposta=observacao.get_pk)):
    send_qtd_mensagens_to_firebase.apply_async(
        args=[observacao.setor.get_pk, observacao.responsavel.get_pk]
    )
return observacao
```

## Edge cases (as implemented)
No @transaction.atomic decorator is used deliberately (explicit code comment: 'Não colocar transaction atomic!'), so partial failures (e.g. after arquivo/checagem creation but before the firebase call) are possible without rollback.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/observacao.py | 183-220 | 8166c07e | primary |
- Merged from: RULE-observacao-BE-05-004
- Related rules: RULE-COMUNICACAO-004, RULE-COMUNICACAO-005, RULE-COMUNICACAO-043

## Notes
reduzir_qtd and send_qtd_mensagens_to_firebase implementations live in utils.firebase, out of this partition's scope; behavior recorded from call-site semantics and the explanatory code comment.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
