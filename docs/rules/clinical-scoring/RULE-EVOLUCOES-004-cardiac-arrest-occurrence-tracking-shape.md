# RULE-EVOLUCOES-004 — Cardiac-arrest occurrence tracking shape

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | validation |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | low |
| Cluster | evolucoes |

## Rule
DadosProntuario tracks whether a cardiorespiratory arrest occurred (ocorreu_parada_cardiorespiratoria, a string field despite its yes/no semantics) and, if so, its start time.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ocorreu_parada_cardiorespiratoria [presumed yes/no or free text, not constrained to a literal union in this file] |  |  |  |
| horario_inicio |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ParadaCardiorrespiratoria |  |  |

## Logic
```text
ParadaCardiorrespiratoria = { ocorreu_parada_cardiorespiratoria: string, horario_inicio: string }
```

## Edge cases (as implemented)
Unlike other boolean clinical flags in the same DadosProntuario object (e.g. delirium and dpoc, both typed boolean), this occurrence flag is typed as a free-form string rather than boolean — inconsistent typing convention recorded verbatim.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference governs the storage data-type of a cardiorespiratory-arrest occurrence flag. Utstein-style in-hospital cardiac arrest reporting (Jacobs I, Nadkarni V, et al. Circulation. 2004;110:3385-3397) specifies WHICH variables to record (occurrence, time of arrest) but not their software field type.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Prontuario.d.ts` | 68-71 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-07-005
- Related rules: none

## Notes
Exact expected string values (e.g. "sim"/"nao") are not present in this partition.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
