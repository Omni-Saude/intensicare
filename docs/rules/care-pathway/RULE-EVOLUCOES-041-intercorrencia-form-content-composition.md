# RULE-EVOLUCOES-041 — Intercorrencia form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Adverse-event/incident ("intercorrencia") form content blocks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['intercorrencia'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(intercorrencia) = ["impressao_geral", "descricao_intercorrencia",
                                  "intervencao_conduta", "desfecho", "relato_gastos"]
permission_trilhas = ("can_preencher_formulario_intercorrencia",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_intercorrencia.py` | 5-29 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-023
- Related rules: RULE-EVOLUCOES-028

## Notes
'relato_gastos' (expense report) block suggests incident forms may capture billing-relevant out-of-pocket costs; no further billing logic present in this partition.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
