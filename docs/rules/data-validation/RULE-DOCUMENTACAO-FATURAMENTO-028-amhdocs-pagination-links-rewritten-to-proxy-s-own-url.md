# RULE-DOCUMENTACAO-FATURAMENTO-028 — AMHDocs pagination links rewritten to proxy's own URL

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
When listing external AMHDocs files, the external API's 'next'/'previous' pagination URLs are rewritten to point back at this API's own base URL (stripped of any existing query string) with the external response's query string appended.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| payload.next | string (url) | null |  |  |
| payload.previous | string (url) | null |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| payload.next | string (url) |  |
| payload.previous | string (url) |  |

## Logic
```text
original_url = request.build_absolute_uri().split("?")[0]
if payload.get("next"):
    payload["next"] = f'{original_url}?{payload["next"].split("?")[1]}'
if payload.get("previous"):
    payload["previous"] = f'{original_url}?{payload["previous"].split("?")[1]}'
```

## Edge cases (as implemented)
split('?')[1] assumes the external URL always contains a '?' - if AMHDocs ever returns a next/previous URL with no query string at all, this raises an uncaught IndexError.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative clinical/standards reference for the rewrite policy itself (proprietary DRF proxy behavior). Adjacent standards used only to confirm the documented edge case: RFC 3986 sec. 3.4 defines the URI query component as OPTIONAL (introduced by '?'), so a next/previous URL need not contain '?'; Django REST Framework pagination (LimitOffset/PageNumber) in practice always emits absolute next/previous URLs that DO carry a '?<query>'.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/integracao_amhdocs.py | 41-66 | 8166c07e | primary |
- Merged from: RULE-integracao-BE-05-002
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-027

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
