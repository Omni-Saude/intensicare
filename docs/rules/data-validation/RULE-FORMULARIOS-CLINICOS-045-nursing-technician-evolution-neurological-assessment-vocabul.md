# RULE-FORMULARIOS-CLINICOS-045 — Nursing-technician evolution neurological assessment vocabulary

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule

Controlled-vocabulary 'Avaliação Neurológica' section in the nursing-technician evolution form: Orientação (level of consciousness) constrained to {ativo, sonolento, torporoso, comatoso, reativo} and Emocional constrained to {calmo, agitado, agressivo, letargico, nsa}. Single-choice select vocabularies, no scoring/threshold/computation.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_neurologica.orientacao | select | - | ativo | sonolento | torporoso | comatoso | reativo |
| avaliacao_neurologica.emocional | select | - | calmo | agitado | agressivo | letargico | nsa |

## Outputs

| Name | Type | Unit |
|---|---|---|
| validated enum values | string | - |

## Logic

```text
Avaliação Neurológica (avaliacao_neurologica):
  Orientação -> {ativo, sonolento, torporoso, comatoso, reativo}
  Emocional  -> {calmo, agitado, agressivo, letargico, nsa}
```

## Edge cases (as implemented)

Both fields are single-choice selects stored under avaliacao_neurologica.*. This is a subset of the pharmacist neuro vocabulary (RULE-FORMULARIOS-CLINICOS-044): it has no Pupilas or Abertura Ocular fields.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormTecEnfermagem.ts` | 83-113 | `f9656be2` | primary |

- Merged from: RULE-gap6-09
- Related rules: RULE-FORMULARIOS-CLINICOS-044, RULE-FORMULARIOS-CLINICOS-036, RULE-FORMULARIOS-CLINICOS-012

## Notes

Surrounding sections are covered (24-82 by RULE-FORMULARIOS-CLINICOS-036, 114-215 by RULE-FORMULARIOS-CLINICOS-012), but this neurological-assessment vocabulary was uncited. Minor: controlled-vocabulary field definitions, no thresholds/decisions.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
