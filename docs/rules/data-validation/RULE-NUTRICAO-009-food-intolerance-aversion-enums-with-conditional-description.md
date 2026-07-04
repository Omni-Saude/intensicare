# RULE-NUTRICAO-009 — Food intolerance / aversion enums with conditional description

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | nutricao |

## Rule
Intolerancia and Aversao are each captured as {sim, nao, desconhece}. Selecting "sim" reveals a free-text field asking which intolerance / aversion.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| intolerancia | enum |  | sim | nao | desconhece |
| aversao | enum |  | sim | nao | desconhece |

## Outputs
| Name | Type | Unit |
|---|---|---|
| showDescription | boolean |  |

## Logic
```text
intolerancia select options: sim / nao / desconhece
if (intolerancia === "sim") render textarea avaliacao_global.descricao_intolerancia ("Qual intolerancia?")
aversao select options: sim / nao / desconhece
if (aversao === "sim") render textarea avaliacao_global.descricao_aversao ("Qual aversao?")
```

## Edge cases (as implemented)
Description fields are optional (no required rule). All inputs disabled when mode === "in_page".

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FieldsetAvGlobalNutricionista/FieldsetAvGlobalNutricionista.tsx | 98-130 | f9656be2 | primary |

- Merged from: RULE-nutricao-FE-04-031
- Related rules: none

## Notes
Verified against source lines 98-130.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
