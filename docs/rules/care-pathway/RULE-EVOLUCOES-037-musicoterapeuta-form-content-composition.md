# RULE-EVOLUCOES-037 — Musicoterapeuta form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Music-therapy form content blocks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['musicoterapeuta'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(musicoterapeuta) = ["impressao_geral", "conduta_realizada", "meta_terapeutica"]
permission_trilhas = ("can_preencher_formulario_musicoterapeuta",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_musicoterapeuta.py` | 7-29 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-025
- Related rules: RULE-EVOLUCOES-028

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
