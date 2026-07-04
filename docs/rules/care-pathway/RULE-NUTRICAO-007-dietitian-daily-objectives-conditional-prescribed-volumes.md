# RULE-NUTRICAO-007 — Dietitian daily-objectives conditional prescribed volumes

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | nutricao |

## Rule
In the dietitian "Objetivos diarios e pendencias" group, each diet-route toggle, when true, reveals a corresponding prescribed-detail field (consistency string, prescribed volume in ml, or supplement string).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dieta_via_oral / nutricao_enteral / nutricao_parenteral / suplementacao | boolean |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| prescribed detail | string|number | ml (for enteral/parenteral) |

## Logic
```text
group key = objetivos_diarios_pendencias
dieta_via_oral == true      -> consistencia (string)
nutricao_enteral == true    -> Volume_prescrito_enteral (number, ml)
nutricao_parenteral == true -> Volume_prescrito_parenteral (number, ml)
suplementacao == true       -> suplemento (string)
```

## Edge cases (as implemented)
Field key "Volume_prescrito_enteral" (and "Volume_prescrito_parenteral") is capitalized (case-sensitive persistence key), unlike the surrounding snake_case keys.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormNutricionista.ts | 347-415 | f9656be2 | primary |

- Merged from: RULE-nutrition-FE-01-050
- Related rules: none

## Notes
Verified against source lines 347-415. Conditional field reveals via `conditions.true`. No clinical threshold/anchor -> verify:false.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
