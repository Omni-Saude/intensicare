# RULE-TRILHAS-ENGINE-004 — Pathway alert-status color precedence

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
The color/severity styling of a pathway tab is chosen by precedence: if the pathway is marked assistido (attended), use the ASSISTIDO style; otherwise use the pathway's alert level (trilha.alerta); if no alert, default to NEUTRO.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilha.assistido | boolean |  |  |
| trilha.alerta | enum(string) |  | NEUTRO \| VERMELHO \| AMARELO \| LARANJA (or null) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| statusTrilha key -> colors {ballColor, backgroundShade} | enum |  |

## Logic
```text
key = trilha.assistido
        ? "ASSISTIDO"
        : (trilha.alerta || "NEUTRO")
style.borderColor     = statusTrilha[key].ballColor
// when tab is active also:
style.backgroundColor = statusTrilha[key].backgroundShade
style.color           = statusTrilha[key].ballColor
```

## Edge cases (as implemented)
assistido overrides any alert level. A null/absent alerta falls back to NEUTRO (green). Criteria panels are always styled with the VERMELHO (red) palette regardless of the tab color.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TabRecomendacoes/TabRecomendacoes.tsx` | 110-139 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-006`
- Related rules: RULE-TRILHAS-ENGINE-007, RULE-TRILHAS-ENGINE-008

## Notes
statusTrilha color map (out of partition, src/utils/statusTrilha.ts) defines keys NEUTRO (green #00DC50), VERMELHO (red #FF1633), AMARELO (yellow #ffd900), LARANJA (orange #ff5900), ASSISTIDO (blue #00B0FF). Severity ordering is not numerically encoded here; alerta is taken verbatim from the backend.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
