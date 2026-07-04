# RULE-DOCUMENTACAO-FATURAMENTO-029 — PDF grouping (agrupar-pdf) requires a non-empty array of ids

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
retrieve_multiple (the 'agrupar-pdf' action) validates that the request body's 'ids' is a non-empty list before proceeding; otherwise raises a ValidationError.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| request.data.ids | array of uuid |  | must be a non-empty list |

## Outputs
| Name | Type | Unit |
|---|---|---|
| eligible | boolean |  |

## Logic
```text
ids = request.data.get("ids", [])
if not isinstance(ids, list) or not ids:
    raise ValidationError({"error": "Um array de UUIDs deve ser fornecido."})
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/integracao_amhdocs.py | 73-76 | 8166c07e | primary |
- Merged from: RULE-integracao-BE-05-003
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-030, RULE-DOCUMENTACAO-FATURAMENTO-003, RULE-DOCUMENTACAO-FATURAMENTO-016

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
