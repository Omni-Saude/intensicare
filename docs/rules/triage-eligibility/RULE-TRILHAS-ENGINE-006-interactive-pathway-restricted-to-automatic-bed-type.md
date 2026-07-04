# RULE-TRILHAS-ENGINE-006 — Interactive pathway restricted to automatic bed type

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
The TrilhaInterativa (interactive protocol) component is rendered inside a pathway tab only when the occupancy's bed type is "automatica".

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| ocupacao.leito.tipo | string |  | "automatica" \| (other) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| TrilhaInterativa rendered? | boolean |  |

## Logic
```text
if (ocupacao.leito.tipo === "automatica"):
  render <TrilhaInterativa trilha=... idLeito=ocupacao.leito.id .../>
```

## Edge cases (as implemented)
Exact string match on "automatica"; any other leito.tipo suppresses the interactive protocol UI entirely for that occupancy.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TabRecomendacoes/TabRecomendacoes.tsx` | 286-296 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-002`
- Related rules: RULE-TRILHAS-ENGINE-005

## Notes
"automatica" (automatic bed) vs manual beds. This is the outer gate; the inner gate (Sepse/Profilaxia + protocol flags) is RULE-TRILHAS-ENGINE-005.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
