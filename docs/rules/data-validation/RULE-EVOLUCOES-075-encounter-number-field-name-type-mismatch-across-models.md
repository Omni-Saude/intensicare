# RULE-EVOLUCOES-075 — Encounter-number field name/type mismatch across models

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
The patient-encounter identifier is represented inconsistently across models — Models.Prontuario.numero_atendimento is typed `number`, while the equivalent field is named `nr_atendimento` and typed `string` in Models.BalancoHidrico.Balanco, Models.Evolucao.Formulario/FormularioMedico, and (as part of the Firestore-derived Usuario.Paciente) elsewhere.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| numero_atendimento (Prontuario) |  |  |  |
| nr_atendimento (BalancoHidrico/Evolucao) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| encounter identifier |  |  |

## Logic
```text
Prontuario.numero_atendimento: number
BalancoHidrico.Balanco.nr_atendimento: string
Evolucao.Formulario.nr_atendimento: string
Evolucao.FormularioMedico.nr_atendimento: string
```

## Edge cases (as implemented)
Recorded verbatim; both field name and type differ for what appears to be the same domain concept.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Prontuario.d.ts` | 4-4 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-07-003

## Notes
Cross-reference src/@types/models/BalancoHidrico.d.ts line 8 and src/@types/models/Evolucao.d.ts lines 9 and 23.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
