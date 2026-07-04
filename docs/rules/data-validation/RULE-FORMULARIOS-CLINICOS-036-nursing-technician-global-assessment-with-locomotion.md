# RULE-FORMULARIOS-CLINICOS-036 — Nursing-technician global assessment with locomotion

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule
TecEnfermagem global assessment covering edema grade, general state, boolean signs, and a locomotion enum.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_global.locomocao | enum | null | acamado\|deambula\|deambula_auxilio\|cadeirante |

## Outputs

| Name | Type | Unit |
|---|---|---|
| global assessment | object | null |

## Logic

```text
edema {sem_edema, edema1, edema2, edema3, anasarca}; estado_geral {grave, regular}
booleans: hipocorado, ictericia, febre, cianose
locomocao {acamado, deambula, deambula_auxilio, cadeirante}
```

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormTecEnfermagem.ts | 24-82 | f9656be2 | primary |

- Merged from: RULE-tecnursing-FE-01-072
- Related rules: RULE-FORMULARIOS-CLINICOS-011

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
