# RULE-DOCUMENTACAO-FATURAMENTO-026 — PDF upload MIME-type validation

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
When a user uploads a document via the PDF picker, the file is accepted only if the base64 data-URI's declared MIME segment equals "application/pdf"; otherwise the value is cleared and an error modal is shown.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| b64 (base64 data URI of uploaded file) | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| accepted | boolean |  |

## Logic
```text
b64 = await getBase64(file)
isPdf = b64.substring(5, 20) === "application/pdf"
if (isPdf) { onChange(b64) }
else {
  onChange("")
  show Modal.error({ title: "Formato de arquivo invalido!", content: "Por favor! Envie um arquivo PDF." })
}
```

## Edge cases (as implemented)
Validation relies on a fixed character offset (5-20) into the data-URI string (`data:application/pdf;base64,...`), not a robust MIME parse; a differently-prefixed data URI of the same length window could pass or fail incorrectly. A fake progress bar increments 5% every 300ms and is force-cleared after 8000ms regardless of actual upload completion (not tied to real network progress).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/PDFB64Convert/PDFB64Convert.tsx | 47-75 | f9656be2 | primary |
- Merged from: RULE-upload-FE-06-021
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-012

## Notes
Phase-1 capture omitted a `status` field; the fixed-offset MIME check is a documented edge case, not a cross-implementation divergence (no backend/other counterpart to compare in this cluster), so status is set to OK on reconciliation. Confirmed this component (PDFB64Convert) is used only by FilesPickContent.tsx (RULE-DOCUMENTACAO-FATURAMENTO-012's leito document upload), not shared with the misrouted FileB64Convert (RULE-upload-FE-05-001, avatar/logo uploader) despite both implementing an identical fake setInterval-based progress bar (5%/300ms, force-cleared at 8000ms) — a shared UI anti-pattern across two otherwise-unrelated components, not the same business rule, so not merged.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
