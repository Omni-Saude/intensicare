# RULE-EVOLUCOES-039 — Psicologo form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Psychologist form content blocks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['psicologo'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(psicologo) = ["impressao_geral", "avaliacao_psicologica",
                             "conduta_psicologica", "meta_terapeutica"]
permission_trilhas = ("can_preencher_formulario_psicologo",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_psicologo.py` | 14-37 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-027
- Related rules: RULE-EVOLUCOES-028

## Notes
File imports FormularioFisioterapeutaSerializer/FormularioTerapeutaSerializer/FormularioNutricionistaSerializer but never uses them (dead imports, not a rule).

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
