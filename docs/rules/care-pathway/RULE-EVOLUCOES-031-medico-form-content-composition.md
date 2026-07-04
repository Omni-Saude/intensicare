# RULE-EVOLUCOES-031 — Medico form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Physician evolution form content blocks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['medico'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(medico) = ["impressao_geral", "impressao_medica", "plano_terapeutico", "conduta_medica"]
permission_trilhas = ("can_preencher_formulario_medico",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_medico.py` | 12-39 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-024
- Related rules: RULE-EVOLUCOES-017, RULE-EVOLUCOES-028, RULE-EVOLUCOES-014

## Notes
See RULE-formulario-BE-08-030 for the bundled vital-signs/balanco-hidrico side effect implemented in the same manage_data() override.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
