# RULE-EVOLUCOES-014 — Medical evolution displays most recent vital signs at/before its own creation time

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When rendering a medical evolution document, the associated vital-signs snapshot shown alongside it is the single most recent SinaisVitais record for the same encounter whose creation time is at or before the medical evolution's own creation time (not necessarily the globally-latest vital signs for the patient).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.nr_atendimento |  |  |  |
| instance.criado_em |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| sinais_vitais |  |  |

## Logic
```text
qs = SinaisVitais.objects.filter(
    balanco__nr_atendimento=instance.nr_atendimento,
    criado_em__lte=instance.criado_em,
).order_by("-criado_em").first()
return SinaisVitaisSimpleSerializer(qs).data if qs else None
```

## Edge cases (as implemented)
Returns None if no vital-signs record exists at or before the evolution's creation time — even if later vital signs exist for the same encounter.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_medico.py` | 300-309 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-015
- Related rules: RULE-EVOLUCOES-024

## Notes
Duplicated (using SinaisVitaisPdfSerializer instead of SinaisVitaisSimpleSerializer) in FormularioMedicoPdfSerializer.get_sinais_vitais, lines 393-402 of the same file — identical filter/order/first() logic.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
