# RULE-EVOLUCOES-035 — Farmaceutico clinico form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Clinical pharmacist form content blocks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['farmaceutico'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(farmaceutico) = ["impressao_geral", "conciliacao_medicamentosa",
                                "conduta_farmaceutica", "profilaxias", "meta_terapeutica"]
permission_trilhas = ("can_preencher_formulario_farmaceutico",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_farmaceutico.py` | 7-31 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-020
- Related rules: RULE-EVOLUCOES-028, RULE-EVOLUCOES-062

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
