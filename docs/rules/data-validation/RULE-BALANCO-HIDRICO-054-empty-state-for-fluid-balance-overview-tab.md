# RULE-BALANCO-HIDRICO-054 — Empty-state for fluid-balance overview tab

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
The "Visão Geral" tab of the fluid-balance page shows an empty-state message only when both the entradas (inputs) and saidas (outputs) arrays are empty; otherwise it renders whichever of the two non-empty sections exist (they render independently/simultaneously, not mutually exclusively).

## Inputs

- balancoVisaoGeral.entradas
- balancoVisaoGeral.saidas

## Outputs

- rendered-section

## Logic

```text
if (entradas.length > 0) render entradas section
if (saidas.length > 0) render saidas section
if (entradas.length === 0 && saidas.length === 0) render Empty("Não há registros cadastrados")
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/balanco/index.tsx` | 356-380 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-08-003`

**Related rules:**

- [RULE-BALANCO-HIDRICO-013](../physiological-calculation/RULE-BALANCO-HIDRICO-013-fluid-balance-visao-geral-2-hour-time-bucketing-08-00-start.md)
- [RULE-BALANCO-HIDRICO-025](../alert-threshold/RULE-BALANCO-HIDRICO-025-fluid-balance-overview-cell-visibility-threshold-grid-vs-mob.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
