# RULE-MOVIMENTACAO-ADT-057 — Movimentacao data_entrada - absent OK, empty invalid, future rejected

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
The admission timestamp data_entrada may be omitted (accepted, defaults applied) but must not be an empty string and must not be in the future.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| data_entrada | datetime\|empty\|absent; <= now |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| http_status | int |  |

## Logic
```text
data_entrada absent (key deleted)                 -> 201 (test_post_data_entrada_faltando; payload has dados_prontuario)
data_entrada == "" (empty string)                 -> 400 (test_post_sem_dados_prontuario)
data_entrada = now + 1 day (future)               -> 400 (test_post_data_entrada_futura)
data_entrada = valid ISO timestamp / now          -> 201
```

## Edge cases (as implemented)
Empty string is invalid but a missing key is tolerated; future dates rejected (admission cannot be in the future). Format "%Y-%m-%dT%H:%M:%S" accepted.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/tests/test_movimentacao.py` | 61-78,395-414 | `8166c07e` | primary |

- Merged from: RULE-VALIDATION-BE-12-026
- Related rules: RULE-MOVIMENTACAO-ADT-058, RULE-MOVIMENTACAO-ADT-059, RULE-MOVIMENTACAO-ADT-062

## Notes
Test-asserted acceptance contract. The future-rejection half is implemented by DataValidation (RULE-059); this rule additionally documents the absent-OK / empty-400 behavior tested at the API level.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
