# RULE-TRILHAS-ENGINE-016 — Criterion recommendations and interventions rendering

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
For each red-alert criterion of a pathway, the UI lists its recommendations followed by its interventions. When intervencoes exist they are concatenated after recomendacoes into one list; otherwise only recomendacoes are shown. If neither recommendations nor interventions exist, a placeholder "Nao ha recomendacoes para este criterio" is shown.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| criterio.alerta | string |  |  |
| criterio.recomendacoes | string[] |  |  |
| criterio.intervencoes | string[]\|undefined |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| merged recommendation list | string[] |  |

## Logic
```text
dataSource =
  criterio.intervencoes
    ? [ ...criterio.recomendacoes, ...criterio.intervencoes ]
    : criterio.recomendacoes
hasContent = criterio.recomendacoes.length > 0
             OR (criterio.intervencoes && criterio.intervencoes.length > 0)
if (!hasContent): render "Nao ha recomendacoes para este criterio"
// Panel header = criterio.alerta; panel styled with VERMELHO palette.
```

## Edge cases (as implemented)
Recommendations precede interventions in the merged list. When intervencoes is undefined only recomendacoes are used. A criterion with empty recomendacoes but present (non-empty) intervencoes still renders the merged list.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TabRecomendacoes/TabRecomendacoes.tsx` | 213-285 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-008`
- Related rules: RULE-TRILHAS-ENGINE-017, RULE-TRILHAS-ENGINE-004

## Notes
Pathway-level recomendacao (trilha.recomendacao, lines 312-323) is rendered separately below the criteria, with a divider only if criterios.length > 0. When there are no criteria and no recomendacao, the tab shows "Nao ha alertas nem recomendacoes para essa trilha" (lines 281-285).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
