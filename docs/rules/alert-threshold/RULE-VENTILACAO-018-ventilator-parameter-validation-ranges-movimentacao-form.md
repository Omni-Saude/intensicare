# RULE-VENTILACAO-018 — Ventilator parameter validation ranges (movimentacao form)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Validation bounds for mechanical-ventilation parameters recorded on the movimentacao form.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| fio2 (%, 21-100) | | | |
| peep (cmH2O, 0-40) | | | |
| pressao_inspiratoria/PINS (cmH2O, 0-30) | | | |
| volume_corrente (ml, 0-1500) | | | |
| fr (rpm, 0-50) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid vent params (boolean) | | |

## Logic

```text
fio2: interval 21-100; peep: 0-40; pressao_inspiratoria: 0-30; volume_corrente: 0-1500; fr: 0-50
```

## Edge cases (as implemented)

FiO2 floor 21 = room air.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 110-144 | `f9656be2` | primary |

- Merged from: RULE-resp-FE-01-023
- Related rules: RULE-VENTILACAO-019, RULE-VENTILACAO-020, RULE-VENTILACAO-022, RULE-VENTILACAO-023

## Notes

Same FiO2 21-100 / PEEP 0-40 / PINS 0-30 / VC 0-1500 set as the physician FormularioMedico form (RULE-VENTILACAO-019) - those two AGREE. The physiotherapist form and backend homecare validators use DIFFERENT PEEP/PINS bounds (5-18 / 5-40) - see RULE-VENTILACAO-020/022/023. Pure input-plausibility bounds, no published clinical target -> verify=false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
