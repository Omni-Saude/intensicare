# RULE-DOCUMENTACAO-FATURAMENTO-021 — PDF export base64 flag uses raw truthy string check

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
Both PDF export endpoints (balanco hidrico and prescricao) decide whether to return a base64-encoded JSON payload instead of a raw PDF response by testing the truthiness of the raw 'b64' query-parameter string, not by comparing it against an expected value (e.g. "true"). Any non-empty string value for 'b64' (including the literal string "false" or "0") evaluates as truthy in Python and therefore triggers base64 mode.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| b64 (query param) | string |  | any non-empty string → truthy |

## Outputs
| Name | Type | Unit |
|---|---|---|
| response format | enum |  |

## Logic
```text
is_b64 = request.query_params.get("b64", False)   # returns string or False (bool)
...
if is_b64:   # truthy check, not equality check
    return Response({"b64": base64.b64encode(pdf).decode("UTF-8")})
else:
    return HttpResponse(pdf.decode("ISO-8859-1"), content_type="application/pdf")
```

## Edge cases (as implemented)
Absent 'b64' param → False → raw PDF. Any present value, even "false"/"0"/"no", → truthy → base64 JSON response. Contrast with the 'assinatura' param in pdf_balanco_hidrico.py, which is explicitly checked via `in ["true", "True"]`.

## Divergence
Both PDF-export endpoints (balanco hidrico and prescricao) decide base64-vs-raw response format by testing the raw truthiness of the 'b64' query-param STRING (`if is_b64:`), not by comparing it against an expected value. Any non-empty string — including the literal 'false' or '0' — is truthy in Python and triggers base64-JSON mode; only a genuinely ABSENT param (defaulting to the boolean False) yields the raw PDF response. This contrasts directly with the 'assinatura' query-param in the same balanco-hidrico view (RULE-DOCUMENTACAO-FATURAMENTO-004), which is explicitly checked via `in ["true", "True"]` — i.e. two boolean-ish query params in the same codebase (and in one case the same file) use incompatible parsing semantics for what should be equivalent 'true/false flag' inputs.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_balanco_hidrico.py | 31-31,102-113 | 8166c07e | primary |
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_prescricao.py | 25,93-104 | 8166c07e | duplicate |
- Merged from: RULE-pdf-BE-08-035
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-004, RULE-DOCUMENTACAO-FATURAMENTO-018

## Notes
Identical pattern in trilha_homecare/api/v1/views/pdf_prescricao.py:25,93-104.

Confirmed by direct source read: identical `is_b64 = request.query_params.get("b64", False)` + truthy-check pattern present verbatim in both trilha_homecare/api/v1/views/pdf_balanco_hidrico.py (lines 31, 102-113) and pdf_prescricao.py (lines 25, 93-104) — recorded as one rule with both source locations (see sources) rather than two, since it is the identical bug duplicated by copy-paste, not two independent implementations of a shared threshold.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
