# RULE-NUTRICAO-010 — Care-risk (riscos assistenciais) checklist with allergy detail

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | nutricao |

## Rule
A "Riscos assistenciais" master switch, when on, reveals a multi-select of care risks {lpp = pressure skin injury, broncoaspiracao, alergia_alimentar}. Selecting food allergy reveals a free-text field for the allergy description.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| riscosAssistenciais (switch) | boolean |  |  |
| riscos_assistenciais (checkbox group) | string[] |  | lpp | broncoaspiracao | alergia_alimentar |
| alergia_alimentar checked | boolean |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| descricao_alergia_alimentar visible | boolean |  |

## Logic
```text
riscosAssistenciais initial = (getFieldValue(avaliacao_global.riscos_assistenciais) != null)
alergias initial          = (getFieldValue(avaliacao_global.descricao_alergia_alimentar) != null)
if (riscosAssistenciais):
  render Checkbox.Group avaliacao_global.riscos_assistenciais:
    "lpp"               -> "Lesao de pele por pressao"
    "broncoaspiracao"   -> "Broncoaspiracao"
    "alergia_alimentar" -> "Alergias alimentares" (onChange -> setAlergias(checked))
  if (alergias): render textarea avaliacao_global.descricao_alergia_alimentar ("Qual alergia?")
```

## Edge cases (as implemented)
The master switch is UI-only (no bound form name); persisted value is riscos_assistenciais. Other nutrition boolean flags captured as CustomSwitch (no derived logic): ventilacao_mecanica_invasiva, uso_previo_protese_dentaria, edema_periferico, terapia_de_hemodialise.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FieldsetAvGlobalNutricionista/FieldsetAvGlobalNutricionista.tsx | 166-211 | f9656be2 | primary |

- Merged from: RULE-nutricao-FE-04-032
- Related rules: none

## Notes
Verified against source lines 166-212.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
