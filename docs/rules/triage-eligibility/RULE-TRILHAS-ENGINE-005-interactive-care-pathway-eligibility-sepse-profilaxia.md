# RULE-TRILHAS-ENGINE-005 — Interactive care-pathway eligibility (Sepse / Profilaxia)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
The interactive protocol accept/refuse card is offered only for pathways named exactly "Sepse" or "Profilaxia", and only when there is either an existing interactive protocol instance, a protocol history, or permission to create a new protocol.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilha.nome | string |  | "Sepse" \| "Profilaxia" (case-sensitive) |
| trilha.trilha_interativa | object\|null |  |  |
| trilha.has_historico_protocolo | boolean |  |  |
| trilha.can_criar_novo_protocolo | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| hasTrilhaInterativaOption | boolean |  |

## Logic
```text
hasTrilhaInterativaOption =
  (trilha.nome === "Sepse" || trilha.nome === "Profilaxia")
  AND (
    trilha.trilha_interativa
    OR trilha.has_historico_protocolo
    OR trilha.can_criar_novo_protocolo
  )
```

## Edge cases (as implemented)
Name comparison is exact and case-sensitive ("Sepse", "Profilaxia"); any other pathway name yields no interactive card regardless of the other flags.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TrilhaInterativa/TrilhaInterativa.tsx` | 156-163 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-001`
- Related rules: RULE-TRILHAS-ENGINE-006, RULE-TRILHAS-ENGINE-014, RULE-TRILHAS-ENGINE-015

## Notes
Hard-codes the two interactive protocols supported by the platform (Sepse, Profilaxia). Combined with RULE-TRILHAS-ENGINE-006 the interactive card requires BOTH an automatic bed and one of these two pathway names. Pure UI gating on flags — encodes no clinical threshold/dose — so verify:false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
