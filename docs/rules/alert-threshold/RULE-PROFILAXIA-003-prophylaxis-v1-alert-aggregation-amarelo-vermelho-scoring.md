# RULE-PROFILAXIA-003 — Prophylaxis v1 alert aggregation (amarelo/vermelho scoring)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | profilaxia |

## Rule
Profilaxias v1 alert severity aggregation - criterio_1 raises AMARELO, criterio_4 or criterio_9 raise VERMELHO.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_1 (amarelo); criterio_4, criterio_9 (vermelho) | int flag (truthy) | — | — |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} | — |

## Logic

```text
amarelo = [criterio_1].count(True)
vermelho = [criterio_4, criterio_9].count(True)
if vermelho >= 1: return "VERMELHO"
elif amarelo >= 1: return "AMARELO"
else: return "NEUTRO"
```

## Edge cases (as implemented)
Count-based aggregation; any single truthy criterio in a tier trips that tier. Vermelho evaluated before amarelo.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha8.py` | 124-141 | `8166c07e` | primary |

- Merged from: RULE-profilaxia-BE-03-019
- Related rules: RULE-PROFILAXIA-004, RULE-PROFILAXIA-002, RULE-PROFILAXIA-007

## Notes
v1 variant of RULE-PROFILAXIA-004 (v3 alert). Difference from v3 is a version-variant difference, NOT a discrepancy: v1 vermelho tier = {criterio_4, criterio_9}; v3 vermelho tier = {criterio_9} only (criterio_4 commented out). TrilhaOitoSintetico in the same file is labelled tipo=eficiencia - a name/label mismatch noted for downstream cleanup.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
