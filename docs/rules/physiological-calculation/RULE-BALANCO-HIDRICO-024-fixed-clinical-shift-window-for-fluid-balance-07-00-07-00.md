# RULE-BALANCO-HIDRICO-024 — Fixed clinical shift window for fluid balance (07:00-07:00)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | threshold |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
The fluid-balance (balanço hídrico) page always computes/displays balances using a fixed 24-hour "turno" (shift) window running from 07:00 to 07:00 the next day, regardless of any facility-specific shift configuration. The date picker and initial date state are both pinned to this window.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| current date/time | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| date | turno-aligned reference date | — |

## Logic
```text
initialDate = dateTurn(moment(), "7:00", "7:00")
// CustomDatePicker configured with dateTurnProps = { start: "7:00", end: "7:00" }
// UI label: "Turno vigente: 7:00 às 7:00"
```

## Edge cases (as implemented)
dateTurn implementation itself is out of FE-08 scope (utils/dateTurn); this page passes identical start/end "7:00" strings in all cases, so the shift boundary is not configurable from this page.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Same 07:00-to-07:00 nursing-shift 'turno' convention as RULE-023, applied on the frontend (fixed start/end '7:00'). Institutional/operational convention, no authoritative published clinical standard mandating this exact window. (n/a)
- Test vectors: 3/3 match
- Frontend display convention mirroring RULE-023's backend 07:00 boundary; the two surfaces are mutually consistent. No external clinical reference to validate the exact 07:00-07:00 turno (facility convention). dateTurn implementation is out of the cited partition (utils/dateTurn) — internally consistent as written. Flag for internal review; not clinically wrong.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/balanco/index.tsx | 67-69, 321-335 | f9656be2 | primary |
- Merged from: RULE-balanco-FE-08-001
- Related rules: RULE-BALANCO-HIDRICO-023, RULE-BALANCO-HIDRICO-027

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
