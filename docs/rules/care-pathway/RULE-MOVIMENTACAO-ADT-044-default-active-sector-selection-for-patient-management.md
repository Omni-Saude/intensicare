# RULE-MOVIMENTACAO-ADT-044 — Default active sector selection for patient management

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
When the patient-linking screen mounts, if the current professional has one or more sectors assigned, the first sector in their list is automatically selected as the active sector for which patients are loaded/managed.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| currentUser.setores | array |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| currentSetor | string, setor id |  |

## Logic
```text
onMount: if (setores.length > 0) { currentSetor = setores[0].id }
```

## Edge cases (as implemented)
If the professional has zero assigned sectors, no sector is auto-selected and no patient list is loaded.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/GestaoPacienteContent/GestaoPacienteContent.tsx` | 177-181 | `f9656be2` | primary |

- Merged from: RULE-gestaopaciente-FE-06-026
- Related rules: RULE-MOVIMENTACAO-ADT-045, RULE-MOVIMENTACAO-ADT-030

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
