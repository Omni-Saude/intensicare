# RULE-EVOLUCOES-007 — Form visibility rule - own draft or released

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A Formulario (clinical form/evolution) of a given type is only visible to a user if it belongs to the same encounter (nr_atendimento) and matches the requested tipo_formulario, AND (it was authored/filled by the requesting user OR its status is "liberado" i.e. released). Draft forms authored by other users are excluded.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| leito.nr_atendimento |  |  |  |
| tipo_formulario |  |  |  |
| request.user |  |  |  |
| status [e.g. 'liberado', other statuses (e.g. draft, inativo)] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset |  |  |

## Logic
```text
Formulario.objects.filter(
    Q(nr_atendimento=leito.nr_atendimento, tipo=tipo_formulario),
    Q(preenchido_por=request.user) | Q(status="liberado"),
).order_by("-modificado_em")
```

## Edge cases (as implemented)
Forms with any status other than "liberado" (e.g. draft/rascunho) are only visible to their original author; there is no explicit handling for a null/unset preenchido_por.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_base.py` | 61-66 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-014
- Related rules: RULE-EVOLUCOES-029, RULE-EVOLUCOES-006

## Notes
Contrast with RULE-formulario-BE-08-016 (anterior_indicadores), whose "previous form" lookup does NOT apply this visibility restriction.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
