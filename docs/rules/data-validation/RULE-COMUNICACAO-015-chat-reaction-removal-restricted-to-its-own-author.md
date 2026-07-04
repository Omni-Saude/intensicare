# RULE-COMUNICACAO-015 — Chat reaction removal restricted to its own author

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
In the reactions drawer, tapping a user entry under a given emoji only triggers a delete call when that entry belongs to the currently logged-in user AND the current user has an existing reaction (myReaction) to delete; tapping another user's entry does nothing.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| myReaction (current user's own reaction id, optional) | string \| undefined | — | — |
| userId (current user id) | string | — | — |
| usuario.id (row being tapped) | string | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| onDelete(myReaction) invocation | side effect | — |

## Logic
```text
handleDelete(usuarioId):
  if (myReaction && userId === usuarioId):
    onDelete(myReaction)
  // else: no-op
```

## Edge cases (as implemented)
Even if userId === usuarioId, if myReaction is falsy (the user has no reaction recorded), the tap is a no-op - clicking one's own row does not implicitly add/toggle a reaction here, only remove an existing one.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/DrawerReacoes/DrawerReacoes.tsx | 29-33,50-54 | f9656be2 | primary |
- Merged from: RULE-reacao-FE-05-001
- Related rules: RULE-COMUNICACAO-002, RULE-COMUNICACAO-038

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
