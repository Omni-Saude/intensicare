# RULE-TRILHAS-ENGINE-008 — Pathway overdue-item alert

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
When a pathway has any overdue protocol item, a red warning "Existem itens em atraso." is displayed in the interactive protocol card header.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilha.has_item_em_atraso | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| overdue warning shown? | boolean |  |

## Logic
```text
if (trilha.has_item_em_atraso):
  render danger text "Existem itens em atraso."
```

## Edge cases (as implemented)
Presence-driven boolean; the overdue computation is server-side.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TrilhaInterativa/TrilhaInterativa.tsx` | 190-194 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-005`
- Related rules: RULE-TRILHAS-ENGINE-004, RULE-TRILHAS-ENGINE-005

## Notes
Related to per-item RULE-sepse-FE-03-002 (atraso_primeira_hora, in the sepse cluster) but at the pathway aggregate level. Operational overdue flag — no published clinical anchor, so verify:false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
