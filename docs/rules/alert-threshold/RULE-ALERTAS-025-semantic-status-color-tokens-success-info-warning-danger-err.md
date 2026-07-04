# RULE-ALERTAS-025 — Semantic status color tokens (success/info/warning/danger/error)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | low |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
next.config.js (modifyVars) and src/styles/variables.less both declare an identical set of named color tokens layered on antd's dark+compact theme base: @primary-color #fe6d01 (orange), @secondary-color #606060, @success-color #258a10 (green), @info-color #1a3bb7 (blue), @warning-color #d6a400 (amber), @danger-color #ff1633 (red), @error-color = @danger-color, @default-color #bbbbbb. These establish a platform-wide semantic color convention (green=success, blue=info, amber=warning, red=danger/error) that antd components (Tag, Alert, Badge, Button) consume automatically.

## Inputs

- semantic_state (success | info | warning | danger/error | default)

## Outputs

- hex_color (#258a10 | #1a3bb7 | #d6a400 | #ff1633 | #bbbbbb)

## Logic

```text
COLOR_FOR_STATE = {
  success: "#258a10",
  info:    "#1a3bb7",
  warning: "#d6a400",
  danger:  "#ff1633",
  error:   "#ff1633",   # aliased to danger
  default: "#bbbbbb"
}
```

## Edge cases (as implemented)

AMBIGUOUS: this partition only defines the token->color mapping; it does not show which specific clinical states/alerts map to which token - that wiring lives in component files outside this partition's scope. Only the color-palette rule itself (a candidate severity/status convention) is recorded; surrounding aesthetic styling in globals.css/globals.less/LightTheme.less is excluded as pure design.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/styles/variables.less` | 1-15 | `f9656be266` | primary |
| trilhas-frontend | `next.config.js` | 5-21, 31-37 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-UI-FE-09-005`

**Related rules:**

- [RULE-ALERTAS-024](../care-pathway/RULE-ALERTAS-024-care-pathway-trilha-status-severity-color-palette-statustril.md)

## Notes

Duplicated verbatim between variables.less and next.config.js; theme base is antd getThemeVariables({dark:true, compact:true}). Distinct color system from statusTrilha (RULE-ALERTAS-024) - the antd semantic tokens (danger #ff1633 matches statusTrilha VERMELHO ballColor #FF1633) vs the trilha status ball palette; the two use the same red but different greens (#258a10 success vs #00DC50 NEUTRO ball). Not a clinical divergence - two independent presentation layers.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
