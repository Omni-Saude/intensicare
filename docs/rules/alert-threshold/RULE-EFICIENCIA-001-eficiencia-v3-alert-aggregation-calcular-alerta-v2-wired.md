# RULE-EFICIENCIA-001 — Eficiencia v3 alert aggregation (calcular_alerta_v2, wired)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Maps the computed criteria booleans of the Eficiencia v3 model to the final alert enum. The wired path (save() -> calcular_criterios() -> calcular_alerta_v2()) uses only criterio_10 and criterio_3 for AMARELO and criterio_5 for VERMELHO. A legacy calcular_alerta() with a different criteria mapping is defined but never called.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_3 | boolean | | |
| criterio_5 | boolean | | |
| criterio_10 | boolean | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} | |

## Logic
```text
# save():
#   self.calcular_criterios()
#   self.alerta = self.calcular_alerta_v2()
#   if self.alerta == "NEUTRO": self.assistido = False
#
# calcular_criterios() ONLY computes:
#   self.criterio_3  = calcular_criterio_3()
#   self.criterio_5  = calcular_criterio_5()
#   self.criterio_10 = calcular_criterio_10()
#   (criterio_1,2,4,6,7,8,9 are commented out -> remain null)
#
# calcular_alerta_v2() (USED):
amarelo = [criterio_10, criterio_3].count(True)
vermelho = [criterio_5].count(True)
if vermelho >= 1: return "VERMELHO"
elif amarelo >= 1: return "AMARELO"
else:            return "NEUTRO"
#
# calcular_alerta() (UNUSED legacy):
#   amarelo = [criterio_1, criterio_5, criterio_6, criterio_7, criterio_9].count(True)
#   vermelho = [criterio_2, criterio_3, criterio_4, criterio_8].count(True)
```

## Edge cases (as implemented)
Only criterio_3, criterio_5, criterio_10 are ever computed; all other criteria stay null and never contribute. Because criterio_5 (the sole VERMELHO trigger) is permanently False in code (see RULE-EFICIENCIA-004), the wired alert can in practice only reach AMARELO (via c3 or c10) or NEUTRO. conta_criterios_automatica() (counts truthy c1..c10) also exists but is not used by the alert.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 60-65, 115-157, 206-216 | 8166c07e | primary |
- Merged from: RULE-eficiencia-BE-03-080
- Related rules: RULE-EFICIENCIA-002, RULE-EFICIENCIA-004, RULE-EFICIENCIA-006, RULE-EFICIENCIA-012

## Notes
Wired production alert path for the v3 model. The three feeding criteria are RULE-EFICIENCIA-002 (c3, AMARELO), RULE-EFICIENCIA-004 (c5, VERMELHO), RULE-EFICIENCIA-006 (c10, AMARELO).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
