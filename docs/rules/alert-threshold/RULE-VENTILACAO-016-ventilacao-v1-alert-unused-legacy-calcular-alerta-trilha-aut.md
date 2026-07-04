# RULE-VENTILACAO-016 — Ventilacao v1 alert (unused legacy - calcular_alerta, trilha_automatica)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Legacy ventilation alert defined but NOT called by save(); retained on class.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_1..10 (int flag) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alerta (enum {VERMELHO, AMARELO, NEUTRO}) | | |

## Logic

```text
criterios = [criterio_1..criterio_10].count(1)
if criterios >= 3 or (criterio_1 or criterio_8 or criterio_9): return "VERMELHO"
elif criterios > 0: return "AMARELO"
else: return "NEUTRO"
```

## Edge cases (as implemented)

The OR clause (criterio_1 or criterio_8 or criterio_9) uses truthiness of raw values, so any single of those criteria forces VERMELHO regardless of total count.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha3.py` | 104-122 | `8166c07e` | variant |

- Merged from: RULE-ventilacao-BE-03-013
- Related rules: RULE-VENTILACAO-014, RULE-VENTILACAO-015

## Notes

Dead code in the save() path (calcular_alerta_v2 is used instead); AMBIGUOUS which was intended clinically. Logic mirrors the trilha_manual alert (RULE-VENTILACAO-014) but lives in the separate trilha_automatica variant. Uses .count(1) (integer) whereas trilha_manual uses .count(True).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
