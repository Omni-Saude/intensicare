# RULE-INDICADORES-ETL-017 — Sector occupancy dashboard auto-reload interval

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
When a numeric `reloadTime` (seconds) prop is supplied and the global auto-reload toggle (AutoReloadContext.update) is on, the bed list re-applies its current filters on a fixed interval to refresh occupancy data; the interval is cleared on unmount or when the global toggle is switched off.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| reloadTime | number | seconds |  |
| AutoReloadContext.update | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| pollingIntervalMs | number | milliseconds |

## Logic
```text
if (reloadTime && update) {
  intervalId = setInterval(() => applyFilters({...filters}), reloadTime * 1000)
}
// cleared on unmount, and whenever `update` becomes false while an interval is running
```

## Edge cases (as implemented)
If reloadTime is 0/undefined, no polling is scheduled regardless of the `update` toggle.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListOcupacoes/ListOcupacoes.tsx` | 116-141 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-015
- Related rules: RULE-INDICADORES-ETL-013, RULE-INDICADORES-ETL-014

## Notes
The user-facing on/off switch for `update` lives in PageContainer.tsx (SwitchAutoReload), also in this partition.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
