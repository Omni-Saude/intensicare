# RULE-INDICADORES-ETL-003 — TLP (standardized letality) percentage conversion

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
In the assistance and infection-control indicator charts, the TLP series ("taxa de letalidade padronizada") is computed by multiplying the stored letalidade_tlp field by 100 to express it as a percentage.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| letalidade_tlp | number | ratio |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| TLP | number | % |

## Logic
```text
TLP = letalidade_tlp * 100
# ArrayAgg(F("letalidade_tlp") * 100) aggregated per dt_mes_ano
```

## Edge cases (as implemented)
Aggregated over each month (dt_mes_ano); null letalidade_tlp yields null in the array.

## Verification
- Verdict: VERIFIED (clinical impact: none)
- Reference: Standardized Mortality/Lethality Ratio (SMR = observed deaths / expected deaths). TLP = 'taxa de letalidade padronizada'. SMR is a dimensionless ratio conventionally reported either as a ratio (~1.0) or scaled x100; ratio*100 = percentage is a correct, standard unit conversion.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/views/indicadores_assistenciais.py` | 82-84 | `8166c07e` | primary |

- Merged from: RULE-indicador-BE-02-018
- Related rules: RULE-INDICADORES-ETL-004

## Notes
Same *100 conversion in indicadores_controle_Infeccao.py lines 82-84.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
