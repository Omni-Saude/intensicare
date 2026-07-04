# RULE-DOCUMENTACAO-FATURAMENTO-018 — PDF report filename pattern

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
PDF export filenames are built from the patient's name (spaces replaced by underscores) plus the report day, in a "<nome>-dia:<dia>.pdf" pattern, and set via a raw (unquoted, non-attachment) Content-Disposition header.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| leito.paciente.nome | string |  |  |
| dia | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| nome_arquivo | string |  |

## Logic
```text
nome_arquivo = f"{leito.paciente.nome.replace(' ', '_')}-dia:{dia}.pdf"
response["Content-Disposition"] = f"filename={nome_arquivo}"
```

## Edge cases (as implemented)
Content-Disposition lacks the "attachment;" directive and quoting, and the filename contains a literal ':' character - both can cause inconsistent browser/HTTP-client handling (inline display vs download, or header parsing issues) though this is recorded as-implemented, not corrected.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_balanco_hidrico.py | 40-40,97-100 | 8166c07e | primary |
- Merged from: RULE-pdf-BE-08-038
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-004, RULE-DOCUMENTACAO-FATURAMENTO-005, RULE-DOCUMENTACAO-FATURAMENTO-021

## Notes
Identical filename/header pattern used in trilha_homecare/api/v1/views/pdf_prescricao.py:53,100-103.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
