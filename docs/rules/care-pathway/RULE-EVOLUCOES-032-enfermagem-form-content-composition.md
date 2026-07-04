# RULE-EVOLUCOES-032 — Enfermagem form content composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Nursing evolution form (tipo_formulario='enfermagem') has no extra content blocks beyond the base 'impressao_geral'.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_formulario ['enfermagem'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| content blocks |  |  |

## Logic
```text
content_blocks(enfermagem) = ["impressao_geral"]   # inherited from BaseFormViewSet only
permission_trilhas = ("can_preencher_formulario_enfermeiro",)
exceto_metodo = "GET"
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_enfermagem.py` | 9-15 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-019
- Related rules: RULE-EVOLUCOES-033, RULE-EVOLUCOES-040, RULE-EVOLUCOES-028

## Notes
Same content composition (impressao_geral only) also applies to tecnico_enfermagem (RULE-formulario-BE-08-028) and terapeuta (RULE-formulario-BE-08-029), each gated by a distinct permission.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
