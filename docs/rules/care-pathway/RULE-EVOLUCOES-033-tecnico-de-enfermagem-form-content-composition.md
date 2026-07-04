# RULE-EVOLUCOES-033 — Tecnico de enfermagem form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Nursing-technician form has no extra content blocks beyond base 'impressao_geral'.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['tecnico_enfermagem'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(tecnico_enfermagem) = ["impressao_geral"]
permission_trilhas = ("can_preencher_formulario_tec_enfermagem",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_tecnico_enfermagem.py` | 5-11 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-028
- Related rules: RULE-EVOLUCOES-032, RULE-EVOLUCOES-040, RULE-EVOLUCOES-028

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
