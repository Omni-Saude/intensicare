# RULE-EVOLUCOES-002 — SOFA score display threshold

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When a prontuario record carries a SOFA score (escore_sofa) that is >= 0, a badge "Escore sofa: {value}" is displayed at the top of the form.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dados_prontuario.escore_sofa [0-24 (SOFA scale; code only checks >= 0)] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| showSofaTag |  |  |

## Logic
```text
if (initialValues.dados_prontuario && initialValues.dados_prontuario.escore_sofa >= 0):
  render Tag "Escore sofa: {escore_sofa}"
```

## Edge cases (as implemented)
undefined/null escore_sofa: `undefined >= 0` is false -> hidden. A value of exactly 0 is shown. Negative values (not expected clinically) would be hidden. SOFA itself is computed server-side; this partition only displays it.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Vincent JL et al. The SOFA score to describe organ dysfunction/failure. Intensive Care Med. 1996;22(7):707-710. SOFA total range 0-24 (integer).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/FormDadosProntuario.tsx` | 85-94 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-016
- Related rules: RULE-EVOLUCOES-001

## Notes
SOFA computation logic is not in this partition (backend / other FE partition).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
