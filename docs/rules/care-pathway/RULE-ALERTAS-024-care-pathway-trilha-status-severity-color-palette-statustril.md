# RULE-ALERTAS-024 — Care-pathway (trilha) status severity color palette (statusTrilha)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | care-pathway |
| Type | threshold |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Defines the finite set of trilha status severity categories and the color scheme used to render each. Categories: NEUTRO (green/normal), VERMELHO (red/critical), AMARELO (yellow), LARANJA (orange), ASSISTIDO (blue/assisted). Ordering red > orange > yellow > green mirrors a triage severity color scale.

## Inputs

- statusKey (enum NEUTRO|VERMELHO|AMARELO|LARANJA|ASSISTIDO)

## Outputs

- palette (object)

## Logic

```text
statusTrilha = {
  NEUTRO:    { color:#5BCE85, background:#16302A, backgroundLight:#E1FCE0, ballColor:#00DC50, ballBackground:#08712E, backgroundShade:#08712E1A },  # green
  VERMELHO:  { color:#C54C5C, background:#412125, backgroundLight:#FCE4DD, ballColor:#FF1633, ballBackground:#740614, backgroundShade:#7406141A },  # red
  AMARELO:   { color:#cebc5a, background:#443f23, backgroundLight:#fffadb, ballColor:#ffd900, ballBackground:#726208, backgroundShade:#7262081A },  # yellow
  LARANJA:   { color:#F9A65A, background:#4A2B1F, backgroundLight:#FFEDDD, ballColor:#ff5900, ballBackground:#712B08, backgroundShade:#7137081A },  # orange
  ASSISTIDO: { color:#4FBFE1, background:#04314A, backgroundLight:#DCFDFB, ballColor:#00B0FF, ballBackground:#0060A0, backgroundShade:#0060A01A },  # blue
}
```

## Edge cases (as implemented)

Typed `as any`; unknown keys return undefined. Note LARANJA.ballBackground is #712B08 but its backgroundShade base is #713708 (inconsistent hex, verbatim).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/statusTrilha.ts` | 1-44 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-status-FE-02-001`

**Related rules:**

- [RULE-ALERTAS-011](../alert-threshold/RULE-ALERTAS-011-assistido-overrides-alerta-status-color-precedence-frontend.md)

## Notes

Enum values are the clinically meaningful pathway severity states shared with the backend alerta enum (VERMELHO/AMARELO/NEUTRO/LARANJA) plus the frontend-only ASSISTIDO. Color mapping itself is presentation; the enumeration of statuses is the rule. Status-computation (which record -> which color) lives elsewhere.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
