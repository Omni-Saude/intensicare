# RULE-COMUNICACAO-020 — Real-time notifications filter out the current user's own messages

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
Both the notification-badge websocket stream and the popup-toast websocket stream ignore any incoming message whose responsavel (author) id matches the currently logged-in user's id, so users never receive a notification/popup for their own messages.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dataParse.mensagem.responsavel.id (badge stream) / dataParsePopover.mensagem.responsavel.id (popup stream) | string | — | — |
| user.usuario.id | string | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| notificacoes (badge list state) | Models.Notificacao[] | — |
| popup notification (antd notification.open) | side effect | — |

## Logic
```text
ws.onmessage: if dataParse.mensagem.responsavel?.id !== user.usuario.id:
                 setNotificacoes(prev => [dataParse, ...prev])
wsPopover.onmessage: if dataParsePopover.mensagem.responsavel.id !== user.usuario.id:
                 trotthleNotification(dataParsePopover)     // see RULE-notificacao-FE-05-002
```

## Edge cases (as implemented)
Both sockets are opened per-render via useMemo keyed only on `token`, and both are closed together in a single cleanup effect; a mismatch/race between which socket delivered which event is not otherwise guarded beyond this author-id check.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/DisplayNotificaoes/DisplayNotificaoes.tsx | 100-126 | f9656be2 | primary |
- Merged from: RULE-notificacao-FE-05-001
- Related rules: RULE-COMUNICACAO-009

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
