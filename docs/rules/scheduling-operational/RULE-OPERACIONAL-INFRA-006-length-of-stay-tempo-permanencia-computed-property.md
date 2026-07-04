# RULE-OPERACIONAL-INFRA-006 — Length of stay (TEMPO_PERMANENCIA) computed property

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Micro-indicator length of stay = days since admission (DT_ENTRADA).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| DT_ENTRADA | date | date | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| TEMPO_PERMANENCIA | int | days |

## Logic

```text
TEMPO_PERMANENCIA = handlers.diferenca_dias(DT_ENTRADA)
# diferenca_dias (utils/handlers.py:63): (timezone.now().date() - entrada).days
```

## Edge cases (as implemented)

Returns negative if DT_ENTRADA is in the future; no null guard (TypeError if DT_ENTRADA None).

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. 'Length of stay' is a standard operational metric but its exact computation (calendar-date difference in whole days vs elapsed 24h periods) is an internal definitional choice with no governing paper/guideline/calculator.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/microindicadores.py` | 46-48 | `8166c07e` | primary |

- Merged from: RULE-operational-BE-03-022

## Notes

diferenca_dias itself is in utils/handlers.py (outside BE-03).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
