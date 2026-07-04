# RULE-COMUNICACAO-028 — Online-call roster filtered to users currently in call

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
The "Usuários na sala" list for a sector's video room is populated from Firestore users under that sector filtered to online_call === true, i.e. only users who are presently marked as being in the call are listed; if none are online, an empty-state is shown instead.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| Firestore path /chats/{setor.id}/usuarios/ documents where online_call === true |  | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| usersOnline | Models.Usuario.UserFirebase[] | — |

## Logic
```text
useCollection({ path: `/chats/${setor.id}/usuarios/`, initialFilter: ref => ref.where("online_call","==",true) })
render: if usersOnline.length > 0: list each user (with a green "online" Ball + avatar + name)
        else: show Divider + Empty("Nenhum usuário na sala")
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/BuildVideoChat/BuildVideoChat.tsx | 34-37,113-146 | f9656be2 | primary |
- Merged from: RULE-video-FE-05-002
- Related rules: RULE-COMUNICACAO-016, RULE-COMUNICACAO-029, RULE-COMUNICACAO-030, RULE-COMUNICACAO-044

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
