# RULE-EVOLUCOES-008 — Signed PDF takes precedence over draft PDF

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When exposing the downloadable PDF URL for a clinical evolution document, the signed version (pdf_assinado) is returned if it exists; otherwise the unsigned draft (pdf) is returned.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.pdf_assinado |  |  |  |
| instance.pdf |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| pdf |  |  |

## Logic
```text
if instance.pdf_assinado or instance.pdf:
    pdf = instance.pdf_assinado or instance.pdf
    return pdf.url
return None
```

## Edge cases (as implemented)
Returns None (falls through implicitly) if neither PDF exists.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 117-125 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-001
- Related rules: RULE-EVOLUCOES-025

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
