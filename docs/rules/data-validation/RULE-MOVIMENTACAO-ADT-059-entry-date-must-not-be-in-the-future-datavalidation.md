# RULE-MOVIMENTACAO-ADT-059 — Entry date must not be in the future (DataValidation)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Validates a datetime string against an expected format and rejects future dates.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| data | string datetime; must parse with formato_esperado, default %Y-%m-%dT%H:%M:%S |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid \| ValidationError | bool |  |

## Logic
```text
data = datetime.strptime(self.data, formato_esperado).replace(tzinfo=pytz.utc)
  on ValueError -> raise {"data_entrada": "Favor enviar a data no formato <formato>"}
if data and data > timezone.now(): raise {"data_entrada": "Data de entrada nao pode ser futura"}
```

## Edge cases (as implemented)
Parsed as UTC regardless of source tz. Error key is always "data_entrada" even when validating other dates. all([data, data>now]) - data is always truthy after parse.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/validators/data.py` | 19-34 | `8166c07e` | primary |

- Merged from: RULE-validation-BE-04-041
- Related rules: RULE-MOVIMENTACAO-ADT-057, RULE-MOVIMENTACAO-ADT-062, RULE-MOVIMENTACAO-ADT-060

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
