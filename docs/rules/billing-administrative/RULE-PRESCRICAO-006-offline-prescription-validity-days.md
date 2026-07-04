# RULE-PRESCRICAO-006 — Offline prescription validity days

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | prescricao |

## Rule
Defines the number of days an offline prescription is considered valid as the constant 2.

## Outputs

| Name | Type | Unit |
|---|---|---|
| QTD_DIAS | integer | days |

## Logic

```text
class PrescricaoOfflineEnum:
    QTD_DIAS = 2
```

## Edge cases (as implemented)
Static constant; no computation.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/enum.py` | 1-2 | `8166c07e` | primary |

**Merged from:**

- RULE-ADMIN-BE-12-021

## Notes
No caller found within this repo tree; semantics inferred from class/const name ('prescricao offline', qtd dias = quantity of days). AMBIGUOUS on exact usage but value is unambiguous.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
