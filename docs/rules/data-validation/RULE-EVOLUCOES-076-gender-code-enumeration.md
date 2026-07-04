# RULE-EVOLUCOES-076 — Gender code enumeration

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Patient gender is restricted to one of four codes system-wide — Male (M), Female (F), Other (O), Not-informed (N) — used consistently across Prontuario.Paciente, Ocupacao.Paciente, Chat.Paciente, and Estatisticas.Generos aggregate counts.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| genero [M \| F \| O \| N] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| genero |  |  |

## Logic
```text
Genero = "M" | "F" | "O" | "N"
```

## Edge cases (as implemented)
None beyond the closed 4-value set.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Prontuario.d.ts` | 83-83 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-07-004

## Notes
Estatisticas.Generos (src/@types/models/Estatisticas.d.ts lines 24-29) aggregates counts using the same 4 letters as field names (M/F/N/O).

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
