# RULE-DOCUMENTACAO-FATURAMENTO-003 — combinar_documentos — all-or-nothing PDF validation gate before merge/upload

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
Downloads each PDF url (10s timeout by default) and validates it is a parseable PDF with at least one page (validar_pdf via PyPDF2). Valid PDFs are appended to an in-memory merger. If ANY url is invalid (timeout, HTTP error, unparseable PDF, or any other exception during fetch/validate), the ENTIRE operation is aborted: a 400 response listing all invalid urls is returned, discarding any PDFs already merged in memory — no partial/best-effort merge is ever produced. Only if there are zero invalid urls does it merge, upload to S3 (public-read ACL, key `{s3_directory}/pdf_combinado_trilhas_{uuid4().hex}.pdf`, region default 'us-east-2'), and return the resulting public URL.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| urls | list of PDF URLs |  |  |
| bucket_name | string |  |  |
| s3_directory | string |  |  |
| timeout_validacao | integer | seconds | default 10 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| result | {url: str} on success, OR {errors, status, invalid_urls|exception} on failure |  |

## Logic
```text
pdf_invalidos = []
FOR url IN urls:
  TRY:
    response = GET(url, timeout=timeout_validacao, stream=True); response.raise_for_status()
    IF NOT validar_pdf(response.content): pdf_invalidos.append(url); CONTINUE
    merger.append(response.content)
  EXCEPT (ReadTimeout, RequestException, PdfReadError, Exception):
    pdf_invalidos.append(url); CONTINUE
IF pdf_invalidos:
  RETURN {"errors": {"detail": "PDFs corrompidos ou com timeout detectados"}, "status": 400, "invalid_urls": pdf_invalidos}
nome_arquivo = f"pdf_combinado_trilhas_{uuid4().hex}.pdf"
upload merged bytes to s3://{bucket_name}/{s3_directory}/{nome_arquivo} with ACL public-read
RETURN {"url": f"https://{bucket_name}.s3.{AWS_REGION or 'us-east-2'}.amazonaws.com/{s3_directory}/{nome_arquivo}"}
```

## Edge cases (as implemented)
validar_pdf itself only catches PyPDF2.errors.PdfReadError internally and returns True only if page count > 0; any other exception from validar_pdf propagates up and is caught by combinar_documentos's own broad except, still resulting in the url being marked invalid. AWS credential errors and generic S3 upload errors return distinct 500 payloads.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | utils/combinar_documentos.py | 11-94 | 8166c07e | primary |
- Merged from: RULE-doc-BE-11-054
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-016

## Notes
Backend endpoint is ArquivosAMHDocsViewSet.retrieve_multiple (core/api/v1/views/integracao_amhdocs.py, url_path 'agrupar-pdf'), which calls this combinar_documentos() and returns Response({'message':..., 'file_path': caminho_arquivo['url']}) directly (no extra '.res' wrapper). Confirmed by reconciliation against the frontend caller (RULE-DOCUMENTACAO-FATURAMENTO-016 / postAgruparPDFs): the FE's defensive `data.res || data` unwrap is benign/unnecessary for the current contract (data.res is always undefined so it falls through to data.file_path correctly) — not a functional divergence, just defensive-but-superfluous code, so no status change.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
