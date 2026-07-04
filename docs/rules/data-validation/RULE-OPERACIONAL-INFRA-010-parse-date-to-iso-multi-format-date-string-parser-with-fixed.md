# RULE-OPERACIONAL-INFRA-010 — parse_date_to_iso — multi-format date string parser with fixed precedence

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Parses a date string into a datetime by checking, IN ORDER, the count of '/' and '-' separators: exactly one '/' -> month/year (MM/YYYY); exactly one '-' -> year-month (YYYY-MM); exactly two '/' -> day/month/year (DD/MM/YYYY); exactly two '-' -> year-month-day (YYYY-MM-DD); otherwise falls back to dateutil.parser.parse for any other format.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| date | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| parsed_date | datetime | - |

## Logic

```text
IF date.count("/") == 1: RETURN strptime(date, "%m/%Y")
ELIF date.count("-") == 1: RETURN strptime(date, "%Y-%m")
ELIF date.count("/") == 2: RETURN strptime(date, "%d/%m/%Y")
ELIF date.count("-") == 2: RETURN strptime(date, "%Y-%m-%d")
ELSE: RETURN dateutil.parser.parse(date)
```

## Edge cases (as implemented)

Checks are mutually exclusive on separator TYPE and COUNT only, evaluated in this fixed order ('/' checked before '-'); a string containing exactly one '/' AND some number of '-' would match the first '/' branch and attempt %m/%Y regardless of the '-' characters present, potentially raising a strptime ValueError instead of falling through to dateutil.

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Multi-format date parsing with a fixed separator-count precedence is an internal parsing helper (Python datetime.strptime + dateutil.parser fallback).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 48-60 | `8166c07e` | primary |

- Merged from: RULE-util-BE-11-041

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
