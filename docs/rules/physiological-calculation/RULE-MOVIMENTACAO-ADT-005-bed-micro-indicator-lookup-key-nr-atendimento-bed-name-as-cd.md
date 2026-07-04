# RULE-MOVIMENTACAO-ADT-005 — Bed micro-indicator lookup key: nr_atendimento + bed name as CD_UNIDADE

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
OcupacaoSerializer.get_micro_indicadores and get_procedimentos both resolve a MicroIndicadores row using the combination of the bed's current nr_atendimento AND the bed's own name (instance.nome) matched against the external system's CD_UNIDADE code - i.e. Leito.nome is assumed to equal the legacy hospital system's unit code.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.nr_atendimento | string |  |  |
| instance.nome | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| micro_indicadores | object |  |
| procedimentos_invasivos | object |  |

## Logic
```text
micro_indicador = MicroIndicadores.objects.filter(
    NR_ATENDIMENTO=instance.nr_atendimento, CD_UNIDADE=instance.nome
).first()
return get_microindicadores(micro_indicador)          # or get_procedimentos_invasivos(...)
```

## Edge cases (as implemented)
Uses .first() (not .get()), so if multiple MicroIndicadores rows match the same (NR_ATENDIMENTO, CD_UNIDADE) pair, an arbitrary one (per default ordering) is used silently. Returns whatever get_microindicadores/get_procedimentos_invasivos do with a None argument if no match is found.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Internal data-model lookup key: MicroIndicadores row resolved by (NR_ATENDIMENTO = bed.nr_atendimento, CD_UNIDADE = bed.nome) via .first(). Proprietary integration/business rule mapping Leito.nome to the external Tasy/Oracle unit code CD_UNIDADE. No published clinical reference applies.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/leito.py | 81-99 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-002
- Related rules: RULE-MOVIMENTACAO-ADT-002, RULE-MOVIMENTACAO-ADT-016

## Notes
get_microindicadores/get_procedimentos_invasivos are in utils.micro_indicadores, out of this partition - only the lookup-key rule is captured.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
