# RULE-EVOLUCOES-048 — Dual query-parameter encoding on evolution-report fetch

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | evolucoes |

## Rule
The evolution-report endpoint manually encodes profissional_id/data_inicio/data_fim directly into the URL string, while ALSO forwarding a separate `params` argument through the same axios request config — meaning any caller-supplied `params` object would be applied in addition to, not instead of, the manually-built query string.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| profissional_id |  |  |  |
| data_inicio / data_fim |  |  |  |
| params |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| relatorio |  |  |

## Logic
```text
GET empresas/{idEmpresa}/evolucoes/?profissional_id={profissional_id}&data_inicio={data_inicio}&data_fim={data_fim}
  // ALSO passing { params, headers } in the same axios call
```

## Edge cases (as implemented)
If a caller passes `params` containing e.g. a different profissional_id, axios would append it as an additional query string segment onto a URL that already has that parameter hard-coded, producing a duplicate query key — behavior not exercised/guarded against in this partition.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/networking/evolucao.ts` | 206-226 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-07-004
- Related rules: none

## Notes
Recorded as ambiguous rather than corrected, per ground rules; best interpretation is that `params` is unused by current callers of this hook (dead parameter) but the code path exists.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
