# RULE-EVOLUCOES-003 — RASS field type mismatch across models

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | validation |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
The RASS (Richmond Agitation-Sedation Scale) value is typed as `number` in Models.Ocupacao.InformacoesAssistenciais.rass but as `string` in Models.DadosProntuario.rass — two different representations for what appears to be the same clinical measure.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| rass (Ocupacao.InformacoesAssistenciais) [clinically -5 to +4] |  |  |  |
| rass (Prontuario.DadosProntuario) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| rass |  |  |

## Logic
```text
Ocupacao.InformacoesAssistenciais.rass: number
Prontuario.DadosProntuario.rass: string
```

## Edge cases (as implemented)
Recorded verbatim; not reconciled. A consumer merging data from both sources would need an explicit cast/parse step that is not present in this partition.

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: Sessler CN, Gosnell MS, Grap MJ, Brophy GM, O'Neal PV, Keane KA, et al. The Richmond Agitation-Sedation Scale: validity and reliability in adult intensive care unit patients. Am J Respir Crit Care Med. 2002;166(10):1338-1344. 10-level integer ordinal scale, -5 (unarousable) to +4 (combative).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Prontuario.d.ts` | 22-22 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-07-002
- Related rules: none

## Notes
Cross-reference src/@types/models/Ocupacao.d.ts line 115 (rass typed as number there).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
