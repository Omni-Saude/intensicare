# RULE-COMUNICACAO-023 — Unread-message badge sourced from Firestore, reset on open

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
The sector occupancy page shows an unread-message badge count from a per-user, per-sector Firestore document field qtd_mensagens. Clicking the messages button opens the chat drawer and resets qtd_mensagens to 0 for that user/sector; the badge is not reset merely by rendering.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| setorDoc.qtd_mensagens (Firestore doc at chats/{id_setor}/usuarios/{userId}) | number | count | >= 0 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| badge count | number | count |

## Logic
```text
onClick messages-button:
  setVisibleChat(true)
  setorDocCtrl.update({ qtd_mensagens: 0 })
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor].tsx | 50-52, 140-164 | f9656be2 | primary |
- Merged from: RULE-chat-FE-08-002
- Related rules: RULE-COMUNICACAO-004, RULE-COMUNICACAO-022

## Notes
Cross-checked: this Firestore path (chats/{id_setor}/usuarios/{userId}.qtd_mensagens) is the SAME field maintained server-side by send_qtd_mensagens_to_firebase (RULE-COMUNICACAO-004). This FE action performs an unconditional reset to 0 on chat-drawer open, distinct from the backend's incremental +1/-1-with-eligibility updates (RULE-COMUNICACAO-004/005) — an intentional 'mark all read' UX shortcut, not a bug, but noted as a point where client and server can independently mutate the same counter.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
