# RULE-COMUNICACAO-022 — Auto-select first sector conversation

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
When the establishment-wide chats page loads its list of sector conversations, if no conversation is currently selected, the first item in the fetched list is automatically selected.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| data (setores/chats list) | array | — | — |
| setorSelecionado.id | string \| undefined | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| setorSelecionado | object | — |

## Logic
```text
if (data && data.length > 0 && !setorSelecionado.id) {
  setorSelecionado = data[0]
}
```

## Edge cases (as implemented)
If data is empty, no selection is made and the chat panel is not shown.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/chats/index.tsx | 46-63 | f9656be2 | primary |
- Merged from: RULE-chat-FE-08-001
- Related rules: RULE-COMUNICACAO-023

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
