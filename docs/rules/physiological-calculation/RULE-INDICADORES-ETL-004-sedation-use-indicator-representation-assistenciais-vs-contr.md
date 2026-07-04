# RULE-INDICADORES-ETL-004 — Sedation-use indicator representation (assistenciais vs controle-infeccao)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
The two indicator viewsets present sedation differently. The assistance view plots taxa_uso_sedacao * 100 (a rate as percentage, labeled "Tx. sedacao"). The infection-control view plots the raw dias_sedacao field (days) under the same label "Tx. sedacao".

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| taxa_uso_sedacao | number | ratio |  |
| dias_sedacao | number | dias |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| serie_sedacao | number | % or dias |

## Logic
```text
# indicadores_assistenciais.py chart3:
uso_sedacao = ArrayAgg(F("taxa_uso_sedacao") * 100)   # percentage, eixo y1
# indicadores_controle_Infeccao.py chart3:
uso_sedacao = ArrayAgg("dias_sedacao")                # raw days, eixo y
```

## Edge cases (as implemented)
Different source field, unit, and axis assignment despite identical series label.

## Verification
- Verdict: DISCREPANCY (clinical impact: moderate)
- Reference: No external guideline mandates the representation; this is an internal cross-view consistency defect. Clinical framing: sedation exposure in the ICU (PADIS 2018 guideline emphasis on minimizing sedation) is meaningfully different as a rate/% vs as absolute days, so a shared label across differing units is a genuine interpretation hazard.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/views/indicadores_assistenciais.py` | 105-111 | `8166c07e` | primary |

- Merged from: RULE-indicador-BE-02-019
- Related rules: RULE-INDICADORES-ETL-003

## Notes
DISCREPANCY/duplication: indicadores_controle_Infeccao.py (lines 112-118) is a near-copy of indicadores_assistenciais.py but with drifted field names elsewhere too: chart2 uses tx_mortalidade / mortalidade_esperada vs assistenciais' tx_mortalidade_observada / tx_mortalidade_esperada. Same TLP*100. Verify which field set is canonical.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
