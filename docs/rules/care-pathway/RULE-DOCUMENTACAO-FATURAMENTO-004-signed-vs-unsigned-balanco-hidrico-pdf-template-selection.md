# RULE-DOCUMENTACAO-FATURAMENTO-004 — Signed vs unsigned balanco hidrico PDF template selection

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
The fluid-balance PDF report uses the "with signature" HTML template when the 'assinatura' query parameter is exactly the string "true" or "True"; otherwise it uses the standard (unsigned) template.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| assinatura (query param) | string |  | 'true' | 'True' | other |

## Outputs
| Name | Type | Unit |
|---|---|---|
| template used | enum |  |

## Logic
```text
if request.query_params.get("assinatura", None) in ["true", "True"]:
    template = "arquivos/pdf_balanco_hidrico_com_assinatura.html"
else:
    template = "arquivos/pdf_balanco_hidrico.html"
```

## Edge cases (as implemented)
Case-sensitive; only "true"/"True" trigger the signed template - "TRUE", "1", etc. do not.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_balanco_hidrico.py | 65-72 | 8166c07e | primary |
- Merged from: RULE-pdf-BE-08-036
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-005, RULE-DOCUMENTACAO-FATURAMENTO-021

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
