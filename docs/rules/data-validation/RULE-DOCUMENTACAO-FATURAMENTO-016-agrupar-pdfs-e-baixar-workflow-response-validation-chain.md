# RULE-DOCUMENTACAO-FATURAMENTO-016 — "Agrupar PDFs e baixar" workflow response-validation chain

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
When merging selected files into a single downloadable PDF (agrupar PDFs), the client validates the API response step by step before proceeding: it must be non-empty, must contain a data payload, and that payload must include a file_path - failing any step raises a distinct guard error before any download is attempted; on success the selection is cleared and the resulting file is opened in a new browser tab.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ids (selected arquivo ids) | string[] |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| window.open(file_path) | side effect |  |
| selectedFiles reset to [] | side effect |  |

## Logic
```text
res = await postAgruparPDFs(idEmpresa, idEstabelecimento, idSetor, idOcupacao, { ids })
if !res: throw Error("Resposta vazia da API")
data = res.data || res
if !data: throw Error("Dados não encontrados na resposta")
{ file_path, message } = data.res || data
if !file_path: throw Error("Nenhum arquivo gerado")
// success path:
setVisibleDownloadMultiple(false); setSelectedFiles([]); antdMessage.success(message || "Download pronto!")
window.open(file_path, "_blank")
// any thrown error is caught and surfaced via handleApiError(...) with a generic content message
```

## Edge cases (as implemented)
The response shape is defensively unwrapped through two optional levels (res.data || res, then data.res || data) to tolerate more than one API response envelope shape, suggesting the backend contract for this endpoint was not fully stable/consistent at implementation time.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ArquivosContent/ArquivosContent.tsx | 86-119 | f9656be2 | primary |
- Merged from: RULE-arquivo-FE-05-003
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-003, RULE-DOCUMENTACAO-FATURAMENTO-011, RULE-DOCUMENTACAO-FATURAMENTO-017

## Notes
postAgruparPDFs targets the backend 'agrupar-pdf' action (RULE-DOCUMENTACAO-FATURAMENTO-003); reconciliation confirms the backend's actual {message, file_path} response shape is a strict subset of what this defensive unwrap chain handles — no functional mismatch found. [audit-coordinator: category normalized from invalid "workflow" to data-validation; type remains workflow.]

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
