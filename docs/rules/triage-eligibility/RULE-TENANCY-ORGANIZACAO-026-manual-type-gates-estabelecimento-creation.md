# RULE-TENANCY-ORGANIZACAO-026 — Manual-type gates estabelecimento creation

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The "add estabelecimento" floating action button is only rendered when the current company's tipo === "manual"; companies of other types cannot create establishments through this UI.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| empresaData.tipo | string enum |  | manual \| automatica \| homecare (observed) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| add-button-visibility | boolean |  |

## Logic

```text
if (empresaData?.tipo === "manual") {
  show "+" add-estabelecimento button
}
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/configuracoes/estabelecimentos/index.tsx` | 227-242 | `f9656be2` | primary |

- Merged from: `RULE-empresa-FE-08-004`
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-027, RULE-TENANCY-ORGANIZACAO-028

## Notes
This is a UI-only restriction; no server-side re-check of tipo observed in this page. | Reconciliation: part of a 3-rule family (estabelecimento/leito/setor creation-and-editing gates) all keyed on empresa.tipo === 'manual', each on its own configuracoes page; kept as separate rules since each gates a distinct UI surface, cross-referenced via related.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
