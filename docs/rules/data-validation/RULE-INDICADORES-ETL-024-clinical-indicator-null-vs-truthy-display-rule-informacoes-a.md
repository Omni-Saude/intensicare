# RULE-INDICADORES-ETL-024 — Clinical indicator null-vs-truthy display rule (Informações Assistenciais)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
In the "Informações Assistenciais" card, numeric/scalar clinical fields (RASS, Glasgow, diurese 24h, balanço hídrico 24h, temperatura, leucócitos, plaquetas, PCR, lactato, pH, bicarbonato, pO2, pCO2, P/F, creatinina, ureia, bilirrubinas) are shown whenever the value is not null and not undefined (so a value of 0 is still shown), while pressão arterial, delirium, noradrenalina, and cateter de hemodiálise are shown only when the field is plain-truthy (an empty string, 0, or null all hide the field).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| informacoesAssistenciais.<numeric field> | number \| null \| undefined |  |  |
| informacoesAssistenciais.pressao_arterial | object \| null |  |  |
| informacoesAssistenciais.delirium | string \| null |  |  |
| informacoesAssistenciais.noradrenalina | string \| null |  |  |
| informacoesAssistenciais.cateter_de_hemodialise | string \| null |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| fieldVisible | boolean |  |

## Logic
```text
dataExists(v) = v !== null && v !== undefined
// used for: rass, glasgow, diurese_24h, balanco_hidrico_24h, temperatura,
//           leucocitos, plaquetas, pcr, lactato, ph, bicarbonato, po2, pco2, pf, creatinina, ureia, bilirrubinas
show(numericField) = dataExists(numericField)
// used for: pressao_arterial, delirium, noradrenalina, cateter_de_hemodialise
show(otherField) = !!otherField
```

## Edge cases (as implemented)
A temperatura of 0 or an RASS of 0 (a valid clinical value, e.g. RASS 0 = alert & calm) IS displayed; an empty-string delirium or a noradrenalina dose string of '0' would be hidden under the truthy check.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/InformacaoesAssistenciais/InformacoesAssistenciais.tsx` | 16-164 | `f9656be2` | primary |

- Merged from: RULE-indicadores-FE-06-018
- Related rules: RULE-INDICADORES-ETL-025, RULE-INDICADORES-ETL-026, RULE-INDICADORES-ETL-022

## Notes
Contrast with RULE-dashboard-FE-06-008, which uses plain-truthy checks for tx_mortalidade (hiding a true 0% value).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
