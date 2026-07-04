# RULE-SINAIS-VITAIS-005 — Physician-form vital-sign ranges (partial) — HR/FR/temp/SpO2 unbounded

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
On the physician form (dataFormFormularioMedico.ts "Sinais vitais" group) only blood pressure is range-bounded; heart rate, respiratory rate, temperature and SpO2 are unbounded number inputs — unlike the movimentacao form and the backend validators, which do bound HR/FR/temp.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| pas | number | mmHg | 50-250 |
| pad | number | mmHg | 0-150 |
| frequencia_cardiaca | number | bpm | unbounded |
| frequencia_respiratoria | number | ipm | unbounded |
| temperatura | number | Celsius | unbounded |
| saturacao_o2 | number | percent | unbounded |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid vitals | boolean |  |

## Logic
```text
pas 50-250; pad 0-150
frequencia_cardiaca / frequencia_respiratoria / temperatura / saturacao_o2: number, no min/max
(fields nested under "sinais_vitais" key, vs "dados_prontuario" on movimentacao)
```

## Edge cases (as implemented)
Inconsistent with movimentacao where HR/FR/temp ARE bounded, and with backend validators which enforce HR 0-200, FR 0-50, temp 20-43.

## Divergence
Cross-implementation (frontend vs backend) divergence found in reconciliation: the physician form leaves frequencia_cardiaca, frequencia_respiratoria and temperatura UNBOUNDED, whereas the backend enforces FrequenciaCardiacaValidator 0-200 (RULE-SINAIS-VITAIS-027), FRValidator 0-50 (RULE-SINAIS-VITAIS-015) and TemperaturaValidator 20-43 (RULE-SINAIS-VITAIS-023) on save — so out-of-range values accepted by this form are rejected by the backend. SpO2 (saturacao_o2) is unbounded on BOTH sides (SatO2Validator is disabled, RULE-SINAIS-VITAIS-033), so SpO2 is consistent. PAS 50-250 / PAD 0-150 match backend and the movimentacao form.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 270-308 | `f9656be2` | frontend-copy |

- Merged from: RULE-vitals-FE-01-035
- Related rules: RULE-SINAIS-VITAIS-015, RULE-SINAIS-VITAIS-018, RULE-SINAIS-VITAIS-019, RULE-SINAIS-VITAIS-023, RULE-SINAIS-VITAIS-027, RULE-SINAIS-VITAIS-033, RULE-SINAIS-VITAIS-001

## Notes
Phase-1 recorded this OK with only an internal FE inconsistency note; reconciliation against the backend validators upgrades it to DISCREPANCY (frontend under-validates HR/FR/temp relative to backend). Recorded as a new divergence.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
