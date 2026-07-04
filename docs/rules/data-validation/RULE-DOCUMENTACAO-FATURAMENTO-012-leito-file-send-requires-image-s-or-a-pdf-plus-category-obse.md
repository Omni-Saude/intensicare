# RULE-DOCUMENTACAO-FATURAMENTO-012 — Leito file-send requires image(s) or a PDF plus category/observation

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
Before a "send file" request to a leito's document store (AmhDoc) is allowed to proceed, the user must have picked at least one image or a PDF, and the form additionally marks "Categoria" and "Observação" as required fields.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| imageList | Models.LocalImage[] |  |  |
| file (pdf base64) | string | undefined |  |  |
| categoria | string (required) |  |  |
| observacao | string (required) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| postImagensLeito request body | { imagens?, pdf_base64?, file_name?, observacao?, categoria? } |  |

## Logic
```text
on submit:
  if imageList.length > 0 OR file is set:
    send { imagens: imageList.map(...) or undefined,
           pdf_base64: file or undefined,
           file_name: fileName or undefined,
           observacao: value.observacao or undefined,
           categoria: value.categoria or undefined }
  else:
    show error message "Adicione imagens ou um PDF"   // request is NOT sent
Form.Item("categoria") and Form.Item("observacao") both carry `required` + defaultFormRules.
```

## Edge cases (as implemented)
Switching the Radio.Group between "pdf" and "imagens" clears both imageList and file/fileName (mutually exclusive input modes) via the shared clear() callback. If neither images nor a PDF is present the network call is skipped entirely (guarded client-side before hitting the API).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FilesLeitoComponent/FilesPickContent/FilesPickContent.tsx | 51-81,155-184 | f9656be2 | primary |
- Merged from: RULE-upload-FE-05-002
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-013, RULE-DOCUMENTACAO-FATURAMENTO-026, RULE-DOCUMENTACAO-FATURAMENTO-020

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
