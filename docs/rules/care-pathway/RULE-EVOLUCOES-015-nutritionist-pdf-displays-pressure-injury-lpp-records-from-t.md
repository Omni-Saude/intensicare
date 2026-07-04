# RULE-EVOLUCOES-015 — Nutritionist PDF displays pressure-injury (LPP) records from the latest nursing evolution

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
The nutritionist evolution's printed report does not track its own LPP (pressure injury) data; instead it looks up the most recently registered nursing ("enfermagem") evolution for the same bed and encounter and displays that evolution's LPP list.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.leito |  |  |  |
| instance.nr_atendimento |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| lpps |  |  |

## Logic
```text
ultima_evolucao_enfermagem = Formulario.objects.filter(
    tipo="enfermagem",
    leito=instance.leito,
    nr_atendimento=instance.nr_atendimento,
).order_by("-dt_registro").first()
if ultima_evolucao_enfermagem and ultima_evolucao_enfermagem.avaliacao_global:
    return LPPSerializer(ultima_evolucao_enfermagem.avaliacao_global.lpps, many=True).data
else:
    return {}
```

## Edge cases (as implemented)
Returns an empty dict `{}` (not a list) when no qualifying nursing evolution exists — an inconsistent "empty" representation for what is otherwise a list field.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_nutricionista.py` | 225-246 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-017
- Related rules: RULE-EVOLUCOES-056, RULE-EVOLUCOES-038

## Notes
Duplicated (using LPPPDFSerializer and returning list(...) instead of {} on the empty branch — same {} inconsistency) in FormularioNutricionistaPdfSerializer.get_lpps, lines 335-358 of the same file.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
