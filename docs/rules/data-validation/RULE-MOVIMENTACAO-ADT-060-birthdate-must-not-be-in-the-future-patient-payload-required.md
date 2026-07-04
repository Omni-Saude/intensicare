# RULE-MOVIMENTACAO-ADT-060 — Birthdate must not be in the future + patient payload required

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Patient data is required and the birthdate (YYYY-MM-DD) cannot be a future date.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| paciente.data_nascimento | string date, %Y-%m-%d |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid \| ValidationError | bool |  |

## Logic
```text
if not request.data.get("paciente"): raise {"paciente":"O envio dos dados do paciente e obrigatorio"}
data_nascimento = datetime.strptime(paciente["data_nascimento"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
if data_nascimento and data_nascimento > timezone.now():
    raise {"data_nascimento":"Data de nasicmento nao pode ser futura"}
```

## Edge cases (as implemented)
Missing/malformed data_nascimento raises unhandled TypeError/ValueError (no explicit guard). Error message typo "nasicmento".

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/validators/paciente.py` | 12-27 | `8166c07e` | primary |

- Merged from: RULE-validation-BE-04-043
- Related rules: RULE-MOVIMENTACAO-ADT-056, RULE-MOVIMENTACAO-ADT-062, RULE-MOVIMENTACAO-ADT-064

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
