# RULE-OPERACIONAL-INFRA-011 — get_number — safe numeric coercion with zero default

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Attempts to coerce a value to float; on ValueError or TypeError, returns 0 instead of raising.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| value | any | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| number | float | - |

## Logic

```text
TRY: value = float(value)
EXCEPT (ValueError, TypeError): value = 0
RETURN value
```

## Edge cases (as implemented)

Silently masks invalid/non-numeric input as 0 rather than surfacing an error to the caller.

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. get_number is a generic Python float-coercion helper (utils/handlers.py:68-73) that returns 0 on ValueError/TypeError. Not a clinical scale, equation, or guideline-derived rule.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 68-73 | `8166c07e` | primary |

- Merged from: RULE-util-BE-11-042

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
