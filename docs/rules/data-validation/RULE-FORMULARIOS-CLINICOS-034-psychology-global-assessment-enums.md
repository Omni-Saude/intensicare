# RULE-FORMULARIOS-CLINICOS-034 — Psychology global assessment enums

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule
Psychologist global assessment covering general state, orientation/reactivity, emotional state, eye-opening.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_global.* | enum | null | see logic |

## Outputs

| Name | Type | Unit |
|---|---|---|
| global assessment | object | null |

## Logic

```text
estado_geral {grave, regular}
orientacao {ativo, sonolento, torporoso, comatoso, reativo}
emocional {calmo, agitado, agressivo, letargico, nsa}
abertura_ocular {espontanea, ao_comando, a_dor, nenhuma}
```

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormPsicologo.ts | 22-77 | f9656be2 | primary |

- Merged from: RULE-psico-FE-01-065
- Related rules: RULE-FORMULARIOS-CLINICOS-031, RULE-FORMULARIOS-CLINICOS-035

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
