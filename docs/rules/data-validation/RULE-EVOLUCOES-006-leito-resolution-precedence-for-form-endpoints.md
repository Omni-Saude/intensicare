# RULE-EVOLUCOES-006 — Leito resolution precedence for form endpoints

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When resolving which leito (bed/patient-stay) a form request applies to, the nested-route kwarg 'ocupacoes__pk' takes precedence over the 'nr_atendimento' query parameter; if neither is present, a validation error is raised.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ocupacoes__pk (URL kwarg) |  |  |  |
| nr_atendimento (query param) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| leito |  |  |

## Logic
```text
if ocupacoes__pk:
    return Leito.objects.get(pk=ocupacoes__pk)
elif nr_atendimento:
    return Leito.objects.get(nr_atendimento=nr_atendimento)
else:
    raise ValidationError("Não foi possível identificar o leito")
```

## Edge cases (as implemented)
Raises Leito.DoesNotExist (uncaught) if a pk/nr_atendimento is supplied but does not match any Leito.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_base.py` | 48-59 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-013
- Related rules: RULE-EVOLUCOES-007, RULE-EVOLUCOES-028

## Notes
This get_leito() helper is only used by get_queryset(); manage_data() (write path) instead unconditionally does `Leito.objects.get(pk=kwargs.get("ocupacoes__pk"))`, so the nr_atendimento fallback works for reads but not for writes. See RULE-formulario-BE-08-015.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
