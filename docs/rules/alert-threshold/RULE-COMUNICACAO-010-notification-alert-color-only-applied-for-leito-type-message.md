# RULE-COMUNICACAO-010 — Notification alert color only applied for leito-type messages

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | comunicacao |

## Rule
The colored status ball/icon on a notification row is only derived from the shared statusTrilha[alerta] lookup when the notification's message type is "leito"; every other message type renders with a fixed neutral gray (#959595) regardless of any alerta value present.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| notificacao.mensagem.tipo_mensagem | string | — | — |
| notificacao.mensagem.alerta | string (key into statusTrilha map, out of partition) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ballColor | string (CSS color) | — |

## Logic
```text
ballColor = (tipoMessage === "leito") ? statusTrilha[notificacao.mensagem.alerta]?.ballColor : "#959595"
iconNotificacao = (tipoMessage === "leito") ? mdiBellOutline : mdiMessage
```

## Edge cases (as implemented)
If tipoMessage === "leito" but statusTrilha has no entry for the given alerta key, ballColor resolves to undefined (optional chaining), which renders as no explicit background color rather than falling back to the neutral gray used for non-leito messages.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.tsx | 26-39 | f9656be2 | primary |
- Merged from: RULE-notificacao-FE-05-004
- Related rules: RULE-COMUNICACAO-011, RULE-COMUNICACAO-009

## Notes
statusTrilha itself is defined in src/utils/statusTrilha.ts, out of this partition's scope; only the conditional use of it is verified here.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
