# RULE-DOCUMENTACAO-FATURAMENTO-007 — Cryptocubo __get_formato_assinatura — signature-format mapping

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
Maps a requested document format to the Cryptocubo signature envelope type: 'cms' -> 'detached', 'xml' -> 'enveloping', 'pdf' -> 'detached'; any other format raises a validation error.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| formato | string |  | cms | xml | pdf | other |

## Outputs
| Name | Type | Unit |
|---|---|---|
| formato_assinatura | string |  |

## Logic
```text
IF formato == "cms": RETURN "detached"
ELIF formato == "xml": RETURN "enveloping"
ELIF formato == "pdf": RETURN "detached"
ELSE: RAISE ValidationError("Formato de assinatura não suportado")
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | utils/cryptocubo.py | 74-82 | 8166c07e | primary |
- Merged from: RULE-sign-BE-11-051
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-008, RULE-DOCUMENTACAO-FATURAMENTO-009, RULE-DOCUMENTACAO-FATURAMENTO-010

## Notes
Confirmed: assinar_xml_cryptocubo (called from RULE-DOCUMENTACAO-FATURAMENTO-010) always passes formato="xml" -> "enveloping"; the default formato="pdf" (-> "detached") path is not exercised by that caller.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
