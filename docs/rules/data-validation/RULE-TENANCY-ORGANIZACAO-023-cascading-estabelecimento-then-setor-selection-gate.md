# RULE-TENANCY-ORGANIZACAO-023 — Cascading estabelecimento-then-setor selection gate

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
In the establishment/sector picker, the "Setor de atendimento" search field is disabled (shown as a non-functional placeholder input) until an estabelecimento has been chosen; selecting a new estabelecimento first clears the sector search (briefly unmounting/remounting it via a 100ms delay) before enabling it again scoped to the newly chosen establishment.

## Inputs

| Name | Type | Unit |
|---|---|---|
| estabId (selected estabelecimento id) | string \| undefined |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| setorSearchEnabled | boolean |  |

## Logic

```text
onEstabelecimentoChange(value):
  estabId = undefined            // disable/reset setor search immediately
  onChangeEstabelecimento()
  setTimeout(() => { estabId = value }, 100)   // re-enable, scoped to new estab, after 100ms
setorSearchEnabled = !!estabId
```

## Edge cases (as implemented)
The 100ms setTimeout is a fixed delay with no cancellation/debounce guard; rapid consecutive estabelecimento changes could race and apply an out-of-order estabId.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/SelectPlace/SelectPlace.tsx` | 21-73 | `f9656be2` | primary |

- Merged from: `RULE-selectplace-FE-06-032`

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
