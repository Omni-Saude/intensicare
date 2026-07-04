# RULE-VENTILACAO-019 — Physician respiratory-assessment ventilation decision tree (FormularioMedico)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Ventilation type conditionally reveals invasive-VM parameters (with ranges) or a supplemental-O2 flow field.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_ventilacao (enum ventilacao_ar_ambiente|ventilacao_suporte_o2|ventilacao_mecanica_invasiva|intermitente) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| vent params (object) | | |

## Logic

```text
tipo_ventilacao options (value/label): ventilacao_ar_ambiente "Espontanea",
  ventilacao_suporte_o2 "VNI", ventilacao_mecanica_invasiva "VM", intermitente "Intermitente".
conditions:
  ventilacao_mecanica_invasiva -> fio2(21-100) + peep(0-40) + pins(0-30) + vc(0-1500)
  ventilacao_suporte_o2        -> fluxo_o2 (1-15)
Also tipo_secrecao {ausente,hialina,espessa,grande_quantidade}; tipos_respiratoria multicheck.
```

## Edge cases (as implemented)

Value/label mismatch (ventilacao_ar_ambiente labeled "Espontanea"; ventilacao_suporte_o2 labeled "VNI") - semantic drift but functional.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 309-407 | `f9656be2` | primary |

- Merged from: RULE-resp-FE-01-036
- Related rules: RULE-VENTILACAO-018, RULE-VENTILACAO-020, RULE-VENTILACAO-021, RULE-VENTILACAO-026

## Notes

Same VM parameter ranges as the movimentacao form (RULE-VENTILACAO-018); O2 flow bounded 1-15 L/min here, matching backend homecare RULE-VENTILACAO-021. Different form from RULE-VENTILACAO-018 (not a duplicate); the VM param ranges agree between the two so no discrepancy.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
