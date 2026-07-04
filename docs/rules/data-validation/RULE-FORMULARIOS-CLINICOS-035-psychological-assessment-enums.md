# RULE-FORMULARIOS-CLINICOS-035 — Psychological-assessment enums

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule
Psychological assessment covering attitude toward interviewer, mood, disease awareness, thought pattern.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_psicologica.* | enum/string | null | see logic |

## Outputs

| Name | Type | Unit |
|---|---|---|
| psych assessment | object | null |

## Logic

```text
atitude {cooperativo, resistente, indiferente}
humor {normal, exaltado, baixa_de_humor, quebra_subita}
consciencia_da_doenca {sim, parcial, nao}
pensamento {acelerado, hipocondria, confuso, fuga_negacao}
sintomas_psicologicos(string); queixa_ou_motivo(string)
```

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormPsicologo.ts | 78-139 | f9656be2 | primary |

- Merged from: RULE-psico-FE-01-066
- Related rules: RULE-FORMULARIOS-CLINICOS-034

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
