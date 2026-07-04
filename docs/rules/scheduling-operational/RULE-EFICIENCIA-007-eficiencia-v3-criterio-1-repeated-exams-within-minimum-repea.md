# RULE-EFICIENCIA-007 — Eficiencia v3 criterio_1 - repeated exams within minimum-repeat windows (defined, unwired)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | eficiencia |

## Rule
Flags when more than one exam is re-ordered inside its minimum-repeat window. Each exam class has a window in days; if more than one distinct window-sum is positive across all windows combined, the criterion fires and exames_repetidos is set to the human-readable list of offending exams.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| cpoe exam columns aggregated (Sum) per window over cpoe(dt >= now - window) | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_1 | boolean | |
| exames_repetidos | string | |

## Logic
```text
# Minimum-repeat windows (days) as implemented in the aggregate calls:
#   5d : endoscopia_digestiva, tomo_abdome, tomo_abdome_contraste, tomo_torax
#   7d : usg_urinaria, coagulograma, hemocultura_bacterias, hemocultura_fungos,
#        cultura_urina, cultura_swab_perianal
#  14d : ferritina, angio_torax
#  21d : ecg_transtoracico, ecg_transesofagico, colonoscopia, fibrinogenio,
#        dimero, usg_partes_moles, usg_abdome, broncoscopia
#  30d : eletroencefalograma, rm_cranio
# For each window w: Sum(column) over cpoe(dt >= now.astimezone() - w)
resultado = len([v for v in all_window_sums.values() if v is not None and v > 0]) > 1
if resultado: exames_repetidos = ", ".join(labels of positive sums)
```

## Edge cases (as implemented)
Threshold is >1 positive exam-sum across ALL windows COMBINED (not a per-exam count). Docstring lists additional exams (tomo_cranio<48h, eletroneuromiografia<30d, etc.) that the implemented aggregate OMITS; the aggregate call list is authoritative over the docstring. Uses datetime.now().astimezone(). Unwired.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 218-354 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 96-102 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-081
- Related rules: RULE-EFICIENCIA-012

## Notes
Unwired. Window/exam mapping captured verbatim from the aggregate calls. In get_detalhe(), the facade criterio_1 alert label is suffixed with exames_repetidos.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
