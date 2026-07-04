# RULE-DOCUMENTACAO-FATURAMENTO-014 — Double-gated evolution report access

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | documentacao-faturamento |

## Rule
The Relatório de Evolução page is gated twice by conceptually the same permission, via two different mechanisms: (1) server-side, validateRoute redirects to "/" if the static "trilhas.permissions" cookie array does not include "can_access_relatorio_evolucao"; (2) client-side, the page additionally checks a "can_access_relatorio_evolucao" value computed by the useEffectivePermissions() hook, and if false, shows an empty-report placeholder instead of the filter form (even though the SSR gate already passed).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| cookie-based permissions array (trilhas.permissions) | array |  |  |
| useEffectivePermissions().can_access_relatorio_evolucao | boolean |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| page rendered / redirected / empty-state | enum |  |

## Logic
```text
// SSR (validateRoute)
if (!cookiePermissions.includes("can_access_relatorio_evolucao")) redirect -> "/"

// client render
if (can_access_relatorio_evolucao) {
  render FilterFormRelatorioEvolucao
} else {
  render Result("Relatório vazio", "Atualmente essa empresa não possui nenhum relatório de evolução.")
}
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/relatorio-evolucao/index.tsx | 18-19, 32-46, 52-65 | f9656be2 | primary |
- Merged from: RULE-relatorio-FE-08-001
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-019

## Notes
Best interpretation: useEffectivePermissions() (hook out of FE-08 scope) likely computes a dynamic/derived version of permissions (e.g. incorporating company plan/feature flags) that can differ from the static cookie snapshot read by validateRoute, so the client-side re-check is a legitimate defense-in-depth / freshness check rather than redundant dead code. This cannot be fully confirmed without reading useEffectivePermissions (src/hooks, out of this partition).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
