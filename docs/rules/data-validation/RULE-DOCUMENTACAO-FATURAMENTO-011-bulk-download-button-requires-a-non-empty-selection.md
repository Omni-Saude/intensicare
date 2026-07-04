# RULE-DOCUMENTACAO-FATURAMENTO-011 — Bulk-download button requires a non-empty selection

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
The "Baixar Arquivos" bulk-download action button, and the selected-files list itself, only render when at least one file has been selected; with zero files selected a "select files" placeholder message is shown instead of the list, and the download button is entirely absent.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| selectedFiles | Models.Arquivo.Download[] |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| visibility of file list vs. placeholder message | UI branch |  |
| visibility of "Baixar Arquivos" button | boolean |  |

## Logic
```text
if selectedFiles && selectedFiles.length > 0:
  render each selected arquivo row (with a remove "x" button)
else:
  render placeholder text "Selecione os arquivos que deseja baixar."
if selectedFiles && selectedFiles.length > 0:
  render Button("Baixar Arquivos", onClick=onDownload)
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/DownloadMultiple/DownloadMultiple.tsx | 21-77 | f9656be2 | primary |
- Merged from: RULE-arquivo-FE-05-002
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-016, RULE-DOCUMENTACAO-FATURAMENTO-017

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
