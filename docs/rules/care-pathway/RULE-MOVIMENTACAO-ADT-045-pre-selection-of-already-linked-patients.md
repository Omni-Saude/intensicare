# RULE-MOVIMENTACAO-ADT-045 — Pre-selection of already-linked patients

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
When loading the list of patients for a sector on the patient-linking screen, the checkbox rows for patients that already have a vinculo (existing link to the current professional) are pre-checked by default.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| paciente.vinculo | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| initialPacientes / selectedRowKeys | array of patient ids |  |

## Logic
```text
idsPacientes = pacientes.filter(p => p.vinculo).map(p => p.id)
initialPacientes = idsPacientes
selectedRowKeys = idsPacientes
```

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/GestaoPacienteContent/GestaoPacienteContent.tsx` | 58-86 | `f9656be2` | primary |

- Merged from: RULE-gestaopaciente-FE-06-027
- Related rules: RULE-MOVIMENTACAO-ADT-042, RULE-MOVIMENTACAO-ADT-044, RULE-MOVIMENTACAO-ADT-066

## Notes
The resulting selectedRowKeys are later submitted as pacientes_id when saving the professional-to-patient vinculo (line 97), consumed by the backend bulk diff-sync (RULE-042).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
