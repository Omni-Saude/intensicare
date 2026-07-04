# RULE-VENTILACAO-015 — Ventilacao v1 alert (used - calcular_alerta_v2, trilha_automatica)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Active ventilation alert used by trilha_automatica save(); NEUTRO also resets assistido=False.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_2 / criterio_5 / criterio_7 / criterio_10 (int flag, truthy) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alerta (enum {VERMELHO, AMARELO, NEUTRO}) | | |

## Logic

```text
amarelo = [criterio_10, criterio_2, criterio_7].count(True)
vermelho = [criterio_5].count(True)
if vermelho >= 1: return "VERMELHO"
elif amarelo >= 1: return "AMARELO"
else: return "NEUTRO"
# save(): alerta = calcular_alerta_v2(); if alerta == "NEUTRO": assistido = False
```

## Edge cases (as implemented)

count(True) matches only boolean True, not integer 1; criterio_* are IntegerFields so count(True) may under-match integer flags.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha3.py` | 82-86, 124-142 | `8166c07e` | variant |

- Merged from: RULE-ventilacao-BE-03-012
- Related rules: RULE-VENTILACAO-016, RULE-VENTILACAO-014

## Notes

trilha_automatica (v1/trilha3) pathway variant - SEPARATE from the trilha_manual pathway. See RULE-VENTILACAO-016 for the unused legacy calcular_alerta on the same class. Internal count convention, no published clinical anchor -> verify=false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
