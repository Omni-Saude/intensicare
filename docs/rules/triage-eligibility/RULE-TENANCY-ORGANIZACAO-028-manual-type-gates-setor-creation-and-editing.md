# RULE-TENANCY-ORGANIZACAO-028 — Manual-type gates setor creation and editing

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
For Setores (sectors), companies with tipo === "manual" may both create new setores (add button shown) and edit existing ones (edit button enabled, drawer Save/Ok button shown); all other company types can only view setores read-only (no add button; edit button disabled; drawer hideOk true).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| empresaData.tipo | string enum |  | manual \| automatica \| homecare (observed) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| add-button-visibility | boolean |  |
| edit-button-disabled | boolean |  |
| drawer-hideOk | boolean |  |

## Logic

```text
showAddButton      = (empresaData?.tipo === "manual")
editButtonDisabled = (empresaData?.tipo !== "manual")
drawerHideOk        = (empresaData?.tipo !== "manual") ? true : false
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/configuracoes/setores/index.tsx` | 217-313 | `f9656be2` | primary |

- Merged from: `RULE-empresa-FE-08-006`
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-026, RULE-TENANCY-ORGANIZACAO-027

## Notes
This page has no SSR permission gate (uses default validateRoute(ctx)); restriction is company-type-based, evaluated purely client-side. | Reconciliation: part of the same manual-type-gates-creation family as FE-08-004/005; this is the only one of the three that also gates editing (not just creation) of existing records.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
