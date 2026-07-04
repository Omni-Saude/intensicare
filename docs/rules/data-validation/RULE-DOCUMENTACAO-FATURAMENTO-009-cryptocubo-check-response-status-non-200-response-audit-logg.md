# RULE-DOCUMENTACAO-FATURAMENTO-009 — Cryptocubo __check_response_status — non-200 response audit logging + hard failure

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
If the Cryptocubo sign API responds with a status code other than 200, persists a CryptocuboError audit record (cpf=alias, message from response error detail, status_code) and raises a ValidationError surfacing the error message; on 200, processing continues.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| response | HTTP response object |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| CryptocuboError row | created on failure |  |

## Logic
```text
IF response.status_code != 200:
  error_message = response.json().get("error", {}).get("message", "N/A")
  CryptocuboError.objects.create(cpf=self.__ALIAS, message=error_message, status_code=response.status_code)
  RAISE ValidationError({"erro": f"Cryptocubo/Eval: {error_message}"})
```

## Edge cases (as implemented)
If response.json() itself fails (non-JSON error body), this would raise an unhandled exception rather than the intended ValidationError.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | utils/cryptocubo.py | 164-180 | 8166c07e | primary |
- Merged from: RULE-sign-BE-11-053
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-007, RULE-DOCUMENTACAO-FATURAMENTO-008, RULE-DOCUMENTACAO-FATURAMENTO-010

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
