# RULE-BALANCO-HIDRICO-031 — Fluid-balance output type decision tree

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
A fluid output ("saida") record selects one of 5 types; each reveals type-specific required fields including presence-grading and stool aspect enums.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| output entry | — | — |

## Logic
```text
tipo required. conditions[tipo]:
  diurese_sonda      -> quantidade(ml) required
  diurese_espontanea -> presenca_espontanea required { ausente | presente }
  evacuacao          -> presenca required { ausente | presente+ | presente++ | presente+++ }
                        + aspecto required { regular | pastosa | liquida | sangue-melema }
  vomito_retorno_sonda -> presenca required { ausente | presente+ | presente++ | presente+++ }
  outra_saida        -> nome (string) required + quantidade(ml) required
Also observacao(string) optional; horario HH:MM (RULE-004).
```

## Edge cases (as implemented)
Presence grading 1+/2+/3+ has clinical semi-quantitative meaning; only sonda/outra branches capture ml volume.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormBalancoHidrico.ts | 304-468 | f9656be2 | primary |
- Merged from: RULE-fluidbalance-FE-01-013
- Related rules: RULE-BALANCO-HIDRICO-021, RULE-BALANCO-HIDRICO-022

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
