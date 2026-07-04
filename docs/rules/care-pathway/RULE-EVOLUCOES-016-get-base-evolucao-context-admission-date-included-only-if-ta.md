# RULE-EVOLUCOES-016 — get_base_evolucao_context — admission date included only if Tasy micro-indicators exist for the encounter

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
When building the template context for rendering an evolution PDF, the patient's admission date (dt_entrada) is looked up from the Tasy-sourced MicroIndicadores table by the form's nr_atendimento; it is included only if such a record exists, otherwise dt_entrada is None in the context.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| formulario |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| context.dt_entrada |  |  |

## Logic
```text
IF MicroIndicadores.objects.filter(NR_ATENDIMENTO=formulario.nr_atendimento).exists():
  dt_entrada = MicroIndicadores.objects.filter(NR_ATENDIMENTO=formulario.nr_atendimento).first().DT_ENTRADA
ELSE:
  dt_entrada = None
```

## Edge cases (as implemented)
Runs the filter().exists() check and then a SEPARATE filter().first() query (two DB round-trips instead of one), but behaviorally equivalent to a single first()-with-None-fallback.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/pdfs.py` | 52-77 | `8166c07e` | primary |
- Merged from: RULE-evo-BE-11-072
- Related rules: none

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
