# RULE-MOVIMENTACAO-ADT-054 — Patient gender icon mapping

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
The occupied-bed patient's gender code is mapped to a display icon: "M" maps to a male icon, "F" maps to a female icon, and any other value (including null/undefined/unknown codes) falls back to a generic "unknown person" icon.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| ocupacao.paciente.genero | string: M \| F \| other |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| icon | icon reference |  |

## Logic
```text
switch (genero) {
  case "M": return mdiGenderMale
  case "F": return mdiGenderFemale
  default:  return mdiAccountQuestion
}
```

## Edge cases (as implemented)
Any value other than exactly "M" or "F" (including undefined) falls to default.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao].tsx` | 63-72 | `f9656be2` | primary |
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/balanco/index.tsx` | 233-242 | `f9656be2` | duplicate |

- Merged from: RULE-ocupacao-FE-08-001
- Related rules: RULE-MOVIMENTACAO-ADT-064

## Notes
Identical switch duplicated in balanco/index.tsx lines 233-242 (same repo/commit) - both source locations recorded under one rule.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
