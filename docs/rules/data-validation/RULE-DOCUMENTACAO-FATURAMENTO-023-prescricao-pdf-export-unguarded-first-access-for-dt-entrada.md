# RULE-DOCUMENTACAO-FATURAMENTO-023 — Prescricao PDF export - unguarded first() access for dt_entrada

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
The prescription PDF export retrieves dt_entrada via `prescricoes.first().prescricao.DT_ENTRADA` with no check that the queryset is non-empty. If no PrescricaoContinua rows match the given leito/dia, `.first()` returns None and the subsequent `.prescricao` access raises an unhandled AttributeError, unlike the balanco hidrico PDF export which checks `.exists()` first.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| prescricoes queryset | queryset |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| dt_entrada | datetime |  |

## Logic
```text
"dt_entrada": prescricoes.first().prescricao.DT_ENTRADA,   # no None-check on .first()
```

## Edge cases (as implemented)
Empty queryset (e.g. no prescriptions for that day) → unhandled AttributeError (500).

## Divergence
The prescription PDF export retrieves dt_entrada via `prescricoes.first().prescricao.DT_ENTRADA` with NO check that the queryset is non-empty — an empty queryset (no PrescricaoContinua rows for that leito/dia) makes `.first()` return None and the subsequent `.prescricao` access raises an unhandled AttributeError (500). The balanco-hidrico PDF export's equivalent dt_entrada lookup (RULE-DOCUMENTACAO-FATURAMENTO-005, same subsystem) explicitly guards the identical kind of lookup with `.exists()` before calling `.first()` and falls back to None — the two PDF-export endpoints handle the identical 'lookup first related record for dt_entrada' concern with different safety guarantees.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_prescricao.py | 61-61 | 8166c07e | primary |
- Merged from: RULE-pdf-BE-08-041
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-005, RULE-DOCUMENTACAO-FATURAMENTO-006, RULE-DOCUMENTACAO-FATURAMENTO-022

## Notes
Contrast with RULE-pdf-BE-08-037, which guards the equivalent lookup with .exists().

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
