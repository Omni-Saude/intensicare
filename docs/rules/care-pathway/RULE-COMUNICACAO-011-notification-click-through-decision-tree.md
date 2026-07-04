# RULE-COMUNICACAO-011 — Notification click-through decision tree

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
Clicking a popup notification, or an ItemNotificacao row, routes the user differently based on the notification's message type: "setor" (chat message) opens the sector's chat/message list, while any other type (e.g. "leito") navigates to the associated trilha (care-pathway) page for that leito/occupation, marking the notification read first.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| notificacao.mensagem.tipo_mensagem | 'setor' \| 'leito' \| other | — | — |
| notificacao.mensagem.tipo_trilha | string | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| navigation target (window.location.replace URL) | string (URL) | — |

## Logic
```text
onNotificationClick(notificacao):
  if notificacao.mensagem.tipo_mensagem === "setor":
    openMessageList(notificacao)
      -> replace `/empresa/{empresa.id}/estabelecimento/{estabelecimento.id}/setor/{setor.id}?openChat=true`
  else:
    openTrilhaPage(notificacao, notificacao.mensagem.tipo_trilha):
      -> clearMessages(notificacao.id)      // marks as visto/read first
      -> replace `/empresa/{empresa.id}/estabelecimento/{estabelecimento.id}/setor/{setor.id}?trilha={tipo_trilha}&ocupacao={leito.id}&leito={leito.nome}`
ItemNotificacao row click: only wired when tipoMessage === "setor" (calls onClickMessage);
for "leito" rows the row itself is not clickable (cursor:"default"), but the trilha Tag
chip inside it is separately clickable and calls onClickTrilha(tipo_trilha).
```

## Edge cases (as implemented)
For "leito" notifications with no mensagem.texto, ItemNotificacao instead renders one Tag per entry in mensagem.conteudo, each independently clickable to open that entry's own tipo_trilha - i.e. a single notification can fan out to multiple trilha destinations.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/DisplayNotificaoes/DisplayNotificaoes.tsx | 56-70,82-88 | f9656be2 | primary |
- Merged from: RULE-notificacao-FE-05-003
- Related rules: RULE-COMUNICACAO-039, RULE-COMUNICACAO-019, RULE-COMUNICACAO-010

## Notes
Row-click wiring cross-referenced at src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.tsx lines 42-54,88-129.

---

RECONCILED: cross-checked against src/@types/models/Mensagem.d.ts (TipoMensagem = "setor"|"leito", RULE-COMUNICACAO-039) and core/models/observacao.py (tipo_mensagem = "leito" if self.leito else "setor", RULE-COMUNICACAO-019): the backend only ever emits "setor" or "leito", so this component's else-branch (anything not "setor") always resolves to the leito/trilha routing path in practice — no divergence found.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
