# RULE-EVOLUCOES-024 — criar_sepse_evolucao / get_ultimos_sinais_vitais — sepsis note auto-linked to most recent vitals

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When a Sepse evolution record is created for a formulario, it is automatically linked to the most recently created SinaisVitais (vital signs) record whose balanco (fluid-balance record) shares the same nr_atendimento as the formulario; if no such vitals record exists, sinais_vitais is left null.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| formulario |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| Sepse |  |  |

## Logic
```text
get_ultimos_sinais_vitais(formulario):
  RETURN SinaisVitais.objects.select_related("balanco")
           .filter(balanco__nr_atendimento=formulario.nr_atendimento)
           .order_by("-criado_em").first()
criar_sepse_evolucao(formulario):
  sinais_vitais = get_ultimos_sinais_vitais(formulario)
  Sepse.objects.create(sinais_vitais=sinais_vitais OR None, nr_atendimento=formulario.nr_atendimento, evolucao=formulario)
```

## Edge cases (as implemented)
Chooses the single most recent SinaisVitais by criado_em (creation timestamp), not by any clinical timestamp field on the vitals themselves — if vitals were entered out of chronological order (e.g. backdated), the 'most recent' one is not necessarily the clinically-latest one.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/evolucoes.py` | 106-129 | `8166c07e` | primary |
- Merged from: RULE-evo-BE-11-073
- Related rules: RULE-EVOLUCOES-014

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
