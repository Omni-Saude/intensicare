# RULE-MOVIMENTACAO-ADT-066 — Update-patient-list button disabled check uses array reference equality

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
The "Atualizar Lista de Pacientes" button's disabled prop compares the current row-selection array to the initial-selection array using strict reference equality (===) rather than a value/content comparison.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| selectedRowKeys (array of ids, React state) | n/a | n/a | n/a |
| initialPacientes (array of ids, React state) | n/a | n/a | n/a |

## Outputs
| Name | Type | Unit |
|---|---|---|
| disabled (boolean) | n/a | n/a |

## Logic
```text
disabled = (selectedRowKeys === initialPacientes)   // reference (identity) comparison, not deep-equality
```

## Edge cases (as implemented)
Because both selectedRowKeys and initialPacientes are set via setState calls that always produce new array instances, the two variables are essentially never the same object reference once any state update has occurred - meaning the button is, in practice, almost always enabled, even when the user has not changed the selection from the initial linked-patient set. This looks like a bug: the evident intent (disable until the selection differs from initial) is not what === implements. Recorded verbatim, not corrected.

## Divergence
Intent-vs-implementation discrepancy (single-implementation defect): reference equality (===) used where deep/value equality was evidently intended, so the disable-guard is effectively inert. Recorded verbatim.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/GestaoPacienteContent/GestaoPacienteContent.tsx | 266-279 | f9656be2 | primary |

- Merged from: RULE-gestaopaciente-FE-06-028
- Related rules: RULE-MOVIMENTACAO-ADT-045, RULE-MOVIMENTACAO-ADT-042

## Notes
State declarations for both arrays are at lines 45-51 of the same file.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
