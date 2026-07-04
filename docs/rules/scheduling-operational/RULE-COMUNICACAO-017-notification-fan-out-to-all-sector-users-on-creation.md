# RULE-COMUNICACAO-017 — Notification fan-out to all sector users on creation

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
Creating a Notificacao generates one UsuarioNotificacao (unread) per user in the observation's sector and dispatches a websocket task.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| observacao.setor.usuarios | queryset[Usuario] | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| UsuarioNotificacao rows + ws task | side-effect | — |

## Logic
```text
@transaction.atomic save():
  if not exists (new):
    bulk_create UsuarioNotificacao(notificacao=self, usuario=u) for u in observacao.setor.usuarios.all()
  super().save()
  if new: tasks.notificacao_ws_trilha.delay(self.pk)
```

## Edge cases (as implemented)
Fan-out and ws dispatch only on first save (not updates). UsuarioNotificacao.visto defaults False; unique_together(notificacao,usuario).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/notificacao.py | 15-30 | 8166c07e | primary |
- Merged from: RULE-notificacao-BE-04-027
- Related rules: RULE-COMUNICACAO-018, RULE-COMUNICACAO-019

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
