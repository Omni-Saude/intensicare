# RULE-MOVIMENTACAO-ADT-063 — Movimentacao chronic-condition / pathway flags

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Boolean diagnosis flags recorded on the movimentacao (transfer/round) form that drive downstream care pathways.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| covid_19 / dpoc / eme / shic / historico_cirurgia_abdominal_recente / baixa_aceitacao_dieta_vo | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| pathway flags | boolean set |  |

## Logic
```text
dados_prontuario booleans: covid_19, dpoc (Doenca Pulmonar Obstrutiva Cronica),
eme (Estado de Mal Epileptico), shic (Sindrome de Hipertensao Intra Craniana),
historico_cirurgia_abdominal_recente, baixa_aceitacao_dieta_vo.
```

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 1-37 | `f9656be2` | primary |

- Merged from: RULE-movimentacao-FE-01-018
- Related rules: RULE-MOVIMENTACAO-ADT-047

## Notes
EME/SHIC are Portuguese acronyms for status epilepticus / intracranial hypertension syndrome.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
