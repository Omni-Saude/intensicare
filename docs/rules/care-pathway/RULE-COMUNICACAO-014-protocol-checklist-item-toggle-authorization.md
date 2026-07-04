# RULE-COMUNICACAO-014 — Protocol-checklist item toggle authorization

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
A "checagem" (protocol/alert checklist checkbox) inside a chat message can be toggled by the current user unless it has already been checked by someone else, and can never be toggled from within a reply-preview context.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| checagem.checado | boolean | — | — |
| isMyMessage | boolean | — | — |
| isReply | boolean | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| disabled | boolean | — |

## Logic
```text
disabled = (checagem.checado && !isMyMessage) || isReply
```

## Edge cases (as implemented)
An unchecked item is always togglable (checado is false, so first clause is false) regardless of authorship, as long as it's not in a reply preview.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/MessageBallon/MessageBallon.tsx | 203-218 | f9656be2 | primary |
- Merged from: RULE-chat-FE-06-016
- Related rules: RULE-COMUNICACAO-033, RULE-COMUNICACAO-006

## Notes
onCheck callback (_patchChecagemMsg) lives in MessagesList.tsx, also in this partition.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
