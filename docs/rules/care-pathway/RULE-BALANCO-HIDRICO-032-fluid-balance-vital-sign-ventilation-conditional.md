# RULE-BALANCO-HIDRICO-032 — Fluid-balance vital-sign ventilation conditional

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
In the fluid-balance vital-signs sub-form, ventilation mode conditionally requires supplemental O2 flow or FiO2.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ventilacao | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| fluxo_o2_sup / fio2 | — | — |

## Logic
```text
ventilacao options { ambiente:"Ar ambiente", suporte_o2:"Suporte de O2", mecanica:"Ventilação mecânica" }
  suporte_o2 -> fluxo_o2_sup (number) required
  mecanica   -> fio2 (number) required
```

## Edge cases (as implemented)
Ar ambiente reveals nothing; no numeric bounds on flow/FiO2 here.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormBalancoHidrico.ts | 509-545 | f9656be2 | primary |
- Merged from: RULE-fluidbalance-FE-01-014
- Related rules: RULE-BALANCO-HIDRICO-053

## Notes
Other vital fields (FC, FR, PAS, PAD, temperatura, saturacao_o2, HGT) captured as unbounded numbers in this sub-form (470-508).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
