# RULE-TENANCY-ORGANIZACAO-027 — Manual-type gates leito creation

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The "add leito" (bed) floating action button is only rendered when the current company's tipo === "manual".

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
  show "+" add-leito button
}
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/configuracoes/leitos/index.tsx` | 244-259 | `f9656be2` | primary |

- Merged from: `RULE-empresa-FE-08-005`
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-026, RULE-TENANCY-ORGANIZACAO-028

## Notes
Reconciliation: part of the same manual-type-gates-creation family as FE-08-004/006; kept separate (distinct UI surface), cross-referenced.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
