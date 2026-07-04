# RULE-BALANCO-HIDRICO-055 — IV hydration solution vocabulary

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
Controlled list of intravenous hydration solution types.

## Inputs

- nome

## Outputs

- valid solution

## Logic

```text
options = { Agua destilada, Solução Hipertônica, Soro Fisiológico, Soro Glicosado,
            Soro Ringer, Solução hipotônica, Solução Polarizante }
```

## Edge cases (as implemented)

Free-text not allowed for this branch.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormBalancoHidrico.ts` | 123-145 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fluidbalance-FE-01-009`

**Related rules:**

- [RULE-BALANCO-HIDRICO-029](../care-pathway/RULE-BALANCO-HIDRICO-029-fluid-balance-intake-type-decision-tree.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
