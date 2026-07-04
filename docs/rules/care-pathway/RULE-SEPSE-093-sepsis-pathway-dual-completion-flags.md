# RULE-SEPSE-093 — Sepsis-pathway dual completion flags

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | low |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The sepsis interactive-pathway record (TrilhaInterativa.Sepse) carries two distinct boolean completion-related flags — "finalizado" and "concluida" — with only "concluida" having an associated "concluida_em" completion timestamp; the exact distinction between the two flags is not defined by any logic present in this partition.

## Inputs

- finalizado (boolean)
- concluida (boolean)
- concluida_em (string (datetime), optional)

## Outputs

- pathway completion state (derived)

## Logic

```text
// best interpretation, not confirmed by code in this partition:
finalizado = true  -> the interactive pathway session has ended/closed (regardless of outcome)
concluida  = true  -> the pathway was completed successfully (e.g. all required bundle items checked)
concluida_em = timestamp of the concluida transition
```

## Edge cases (as implemented)

No boolean-combination validation is present (e.g. whether concluida=true implies finalizado=true).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/TrilhaInterativa.d.ts` | 3-14 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-07-001`

**Related rules:**

- [RULE-SEPSE-075](RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)
- [RULE-SEPSE-073](RULE-SEPSE-073-sepse-protocol-rejection-workflow-and-neutral-alert.md)
- [RULE-SEPSE-074](RULE-SEPSE-074-sepse-protocol-closure-accepted-encerrado-workflow.md)
- [RULE-SEPSE-085](RULE-SEPSE-085-interactive-sepsis-pathway-completion-transition.md)
- [RULE-SEPSE-090](RULE-SEPSE-090-sepsis-protocol-lifecycle-state-display.md)

## Notes

A verifier should check the backend partition for the actual state-machine definition distinguishing finalizado vs concluida.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
