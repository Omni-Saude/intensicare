# RULE-OPERACIONAL-INFRA-061 — Request-body upload size cap (DATA_UPLOAD_MAX_MEMORY_SIZE = 100 MiB)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Django DATA_UPLOAD_MAX_MEMORY_SIZE is set to 104857600 bytes (100 MiB = 100 * 1024 * 1024), capping the maximum size of an incoming request body Django will read before raising RequestDataTooBig. Governs clinical PDF/attachment and formulario file uploads (handled via utils/pdfs.py and formulario file inputs).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request body size | number | bytes | cap 104857600 (100 MiB) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| accept / reject (RequestDataTooBig) | decision | - |

## Logic

```text
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600   # bytes = 100 * 1024 * 1024 = 100 MiB
```

## Edge cases (as implemented)

Per Django semantics this caps the aggregate request body (notably non-file form data and the total upload); requests exceeding 100 MiB are rejected before view code runs. FILE_UPLOAD_MAX_MEMORY_SIZE (the in-memory vs temp-file streaming threshold) is not set here, so it keeps its Django default.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/settings.py` | 236 | `8166c07e` | primary |

- Merged from: RULE-gap6-11
- Related rules: RULE-AUTH-USUARIOS-062

## Notes

Only settings.py lines 173-181 and 183 were previously cited for this file (plus 245 PIN_DEFAULT via RULE-AUTH-USUARIOS-062); this upload-size validation constraint was uncovered.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
