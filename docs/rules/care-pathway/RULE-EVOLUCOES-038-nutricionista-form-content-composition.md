# RULE-EVOLUCOES-038 — Nutricionista form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Nutritionist form content blocks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['nutricionista'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(nutricionista) = ["impressao_geral", "avaliacao_diaria_nutricionista",
                                 "meta_terapeutica", "objetivos_diarios_pendencias"]
permission_trilhas = ("can_preencher_formulario_nutricionista",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_nutricionista.py` | 7-34 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-026
- Related rules: RULE-EVOLUCOES-028, RULE-EVOLUCOES-056, RULE-EVOLUCOES-015

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
