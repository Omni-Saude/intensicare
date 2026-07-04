# RULE-INDICADORES-ETL-019 — Assistencial-indicators endpoint URL template bug

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
The endpoint that fetches per-sector assistencial indicators builds its URL with a stray extra closing brace immediately after the empresaId interpolation, producing a malformed request path.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| empresaId | string |  |  |
| estabelecimentoId | string |  |  |
| setorId | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| request URL | string |  |

## Logic
```text
// as written (verbatim, includes bug):
GET `/empresas/${empresaId}}/estabelecimentos/${estabelecimentoId}/setores/${setorId}/indicadores-assistenciais/`
// note the literal extra "}" immediately after ${empresaId} — this is NOT a template
// expression, it is a stray character that gets concatenated into the resulting string,
// e.g. empresaId="123" produces path segment "123}"
```

## Edge cases (as implemented)
This would cause every call to useGetIndicadoresAssistenciais to hit a URL containing a literal "}" character in the empresa-id path segment, likely producing a 404 from the backend router unless the backend happens to tolerate/strip it.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/networking/dashboard.ts` | 4-21 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-07-004
- Related rules: RULE-INDICADORES-ETL-022

## Notes
Recorded verbatim per ground rules (never corrected). Line 12 specifically contains the malformed template literal.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
