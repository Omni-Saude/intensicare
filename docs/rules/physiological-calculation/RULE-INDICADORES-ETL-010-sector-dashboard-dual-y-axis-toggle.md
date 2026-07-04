# RULE-INDICADORES-ETL-010 — Sector dashboard dual y-axis toggle

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | threshold |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | indicadores-etl |

## Rule
Each clinical indicator chart on the sector dashboard renders a single left y-axis by default; a second (right-side) y-axis is only added to the chart configuration when the indicator data includes a y1 field (i.e., a secondary series/unit is present).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| grafico.y | string (axis label) |  |  |
| grafico.y1 | string (axis label) \| undefined |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| chart scales config | object |  |

## Logic
```text
scales.y  = { title: { text: grafico.y }, position: "left", ... }        // always present
scales.y1 = grafico.y1
  ? { title: { text: grafico.y1 }, position: "right", grid: { drawOnChartArea: false }, ... }
  : undefined
```

## Edge cases (as implemented)
When grafico.y1 is undefined, scales.y1 is explicitly undefined (no secondary axis rendered).

## Verification
- Verdict: UNVERIFIABLE (clinical impact: n/a)
- Reference: No authoritative clinical/published reference. Chart.js dual-axis configuration (scales.y always present; scales.y1 conditionally added when a secondary series label exists). Pure front-end presentation logic.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/dashboard/index.tsx` | 89-113 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-08-001
- Related rules: RULE-INDICADORES-ETL-023

## Notes
Chart series data itself (values, per-dataset chart type "line"/"bar") is supplied entirely by the backend API; this page only conditionally wires the secondary axis.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
