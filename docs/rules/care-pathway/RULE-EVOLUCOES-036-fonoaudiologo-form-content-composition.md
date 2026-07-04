# RULE-EVOLUCOES-036 — Fonoaudiologo form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Speech-language therapist form content blocks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['fonoaudiologo'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(fonoaudiologo) = ["impressao_geral", "avaliacao_fonoaudiologica",
                                 "conduta_fonoaudiologica", "meta_terapeutica"]
permission_trilhas = ("can_preencher_formulario_fonoaudiologo",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_fonoaudiologo.py` | 9-32 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-022
- Related rules: RULE-EVOLUCOES-028

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
