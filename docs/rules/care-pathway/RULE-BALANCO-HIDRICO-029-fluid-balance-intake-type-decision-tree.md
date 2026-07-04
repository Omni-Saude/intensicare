# RULE-BALANCO-HIDRICO-029 — Fluid-balance intake type decision tree

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
A fluid intake ("entrada") record selects one of 8 types; each type conditionally reveals type-specific required fields, most terminating in a required volume in ml.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | — | — | — |
| quantidade | — | ml | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| intake entry | — | — |

## Logic
```text
tipo required. conditions[tipo]:
  dieta_enteral   -> quantidade(ml) required
  dieta_oral      -> aceitacao required (see RULE-008)
  medicamento     -> nome (route enum, required) + quantidade(ml) required
  hidratacao_venosa -> nome (solution enum, required) + quantidade(ml) required
  drogas_hidratacao_bi -> nome (drug enum, required) + quantidade(ml) required
  antibiotico     -> nome (antibiotic enum, required) + quantidade(ml) required
  reposicao_eletrolito -> nome (electrolyte enum, required) + quantidade(ml) required
  outra_entrada   -> nome (free string, required) + quantidade(ml) required
Also: observacao(string) optional; horario(masked HH:MM, RULE-004).
```

## Edge cases (as implemented)
All quantidade fields required; medicamento route enum = {intravenoso, oral, gastrostomia, sonda nasoenteral, retal}.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormBalancoHidrico.ts | 1-302 | f9656be2 | primary |
- Merged from: RULE-fluidbalance-FE-01-007
- Related rules: RULE-BALANCO-HIDRICO-020, RULE-BALANCO-HIDRICO-030, RULE-BALANCO-HIDRICO-055, RULE-BALANCO-HIDRICO-056, RULE-BALANCO-HIDRICO-057, RULE-BALANCO-HIDRICO-058

## Notes
Sub-vocabularies broken out as RULE-009..012.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
