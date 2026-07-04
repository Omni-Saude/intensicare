# RULE-MOVIMENTACAO-ADT-047 — Cardiorespiratory arrest capture (nullable group)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Records whether a cardiac arrest occurred and its datetime, in a nullable group.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| ocorreu_parada_cardiorespiratoria | boolean |  |  |
| horario_inicio | datetime |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| PCR event | object |  |

## Logic
```text
parada_cardiorrespiratoria (anulavel): ocorreu_parada_cardiorespiratoria(boolean) + horario_inicio(datetime, showTime)
```

## Edge cases (as implemented)
No conditional linking of datetime to boolean=true (both independently editable).

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 263-288 | `f9656be2` | primary |

- Merged from: RULE-movimentacao-FE-01-029
- Related rules: RULE-MOVIMENTACAO-ADT-034

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
