# RULE-BALANCO-HIDRICO-060 — Fluid-balance complaint conditional

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
If a complaint is flagged, a free-text description becomes required.

## Inputs

- queixa

## Outputs

- motivo_queixa

## Logic

```text
queixa == true -> motivo_queixa (string) required
```

## Edge cases (as implemented)

false reveals nothing.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormBalancoHidrico.ts` | 623-637 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fluidbalance-FE-01-017`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
