# RULE-COMUNICACAO-018 — Record interaction indicator on first notification view

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
When a user marks a specific notification as seen and it was previously unseen, an Indicador of type 'interacao_notificacao' is recorded (analytics of notification engagement); then the user's matching notifications are set to seen.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| id (notificacao id) | id\|null | - | None => mark all seen, no indicator |
| existing visto flag | boolean | - | must be False to log indicator |

## Outputs
| Name | Type | Unit |
|---|---|---|
| Indicador | record | - |
| visto | boolean | - |

## Logic
```text
qs = UsuarioNotificacao.objects.filter(usuario=self.usuario)
if id is not None:
    qs = qs.filter(notificacao__id=id)
    if qs.filter(visto=False).exists():
        Indicador(tipo="interacao_notificacao", dados={"notificacao_id": id, "usuario_id": usuario.get_pk}).save()
qs.update(visto=True)
```

## Edge cases (as implemented)
Indicator only logged when id is provided AND at least one matching row is still unseen (fires once, on transition False->True). When id is None, all the user's notifications are marked seen with NO indicator. Triggered from receive_json only when incoming message has visto truthy. Consumer connect defaults page_size=30 and (unless popover=true) streams the most recent page_size notifications.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/consumers/notificacao.py | 26-42 | 8166c07e | primary |
- Merged from: RULE-OPERATIONAL-BE-12-023
- Related rules: RULE-COMUNICACAO-017

## Notes
page_size default 30 (connect, line 94); popover flag suppresses history stream (lines 95, 113).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
