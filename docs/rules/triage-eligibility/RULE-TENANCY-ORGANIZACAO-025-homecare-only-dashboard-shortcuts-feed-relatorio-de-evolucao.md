# RULE-TENANCY-ORGANIZACAO-025 — Homecare-only dashboard shortcuts (Feed / Relatório de Evolução)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
On the company (empresa) dashboard, floating shortcut buttons to the Feed page and the Relatório de Evolução page are only rendered when the current company's tipo === "homecare". The Relatório de Evolução button additionally requires the can_access_relatorio_evolucao effective permission.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| currentEmpresa.tipo | string enum |  | homecare \| manual \| automatica (observed) |
| can_access_relatorio_evolucao | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| button-visibility | boolean |  |

## Logic

```text
if (currentEmpresa.tipo === "homecare") {
  show Feed button
  if (can_access_relatorio_evolucao) {
    show Relatório de Evolução button
  }
}
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa].tsx` | 121-152 | `f9656be2` | primary |

- Merged from: `RULE-empresa-FE-08-001`
- Related rules: RULE-TENANCY-ORGANIZACAO-016

## Notes
can_access_relatorio_evolucao is computed via useEffectivePermissions() (hook implementation out of FE-08 scope). Cross-reference RULE-relatorio-FE-08-001.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
