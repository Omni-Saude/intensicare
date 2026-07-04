# RULE-OPERACIONAL-INFRA-009 — format_horario — normalize hour-only strings to HH:MM

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Given a time-of-day string, strips whitespace and, if it contains no ':' character, appends ':00' (treats the input as an hour-only value and pads to HH:00).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| horario_formatado | string | - |

## Logic

```text
horario = horario.strip()
RETURN horario + ":00" IF horario.find(":") == -1 ELSE horario
```

## Edge cases (as implemented)

Any presence of ':' anywhere in the string (not just as an HH:MM separator) is treated as 'already formatted' and left untouched.

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Hour-only-to-HH:MM padding is an internal string-normalization helper.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 221-223 | `8166c07e` | primary |

- Merged from: RULE-util-BE-11-039
- Related rules: RULE-OPERACIONAL-INFRA-001

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
