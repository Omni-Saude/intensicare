# RULE-NUTRICAO-004 — Nutrition alert computation (calcular_alerta) - AMARELO branch unreachable

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | nutricao |

## Rule
TrilhaNutricaoModel.calcular_alerta aggregates the nutrition criteria into an alert color. AMARELO requires amarelo > 2 but the amarelo list has only 2 entries, so AMARELO is unreachable.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_4, criterio_7 (amarelo list); criterio_10 (vermelho list) | IntegerField (nullable) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |  |

## Logic
```text
# trilha6.py TrilhaNutricaoModel.calcular_alerta (lines 123-142)
escores = {"amarelo": [criterio_4, criterio_7], "vermelho": [criterio_10]}
amarelo  = escores["amarelo"].count(True)     # max possible value = 2
vermelho = escores["vermelho"].count(True)     # max possible value = 1
if vermelho == 1:   return "VERMELHO"
elif amarelo > 2:   return "AMARELO"            # 2 > 2 is False -> never AMARELO
else:               return "NEUTRO"
# on save(): if alerta == "NEUTRO": assistido = False
```

## Edge cases (as implemented)
amarelo can be at most 2, so `amarelo > 2` is never true -> AMARELO is unreachable (dead branch). VERMELHO uses `== 1` (would miss a hypothetical count of 2, but the vermelho list has a single entry so max is 1). count(True) matches only values exactly == 1 (Python 1 == True); criterio_* are IntegerFields, so any truthy value other than 1 (e.g. 2) would NOT be counted -- criteria are expected to be 0/1/None. NEUTRO clears the assistido flag on save.

## Divergence
Internal inconsistency (single backend source, not a cross-copy divergence). The class defines _CRITERIOS_ALERTA = {"amarelo": 2, "vermelho": 3} implying intended thresholds of 2 and 3, but calcular_alerta ignores that dict and hardcodes `amarelo > 2` and `vermelho == 1`. Combined with an amarelo list of length 2, AMARELO can never fire. Status DISCREPANCY carried from Phase 1.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilha6.py | 123-142 | 8166c07e | primary |

- Merged from: RULE-nutricao-BE-03-017
- Related rules: none

## Notes
Verified against source lines 123-142. Commented-out criterio_11/criterio_12 remain in the amarelo list, hinting the boundary `> 2` predates their removal (with 4 entries, `> 2` would have been reachable). Same file also defines TrilhaNutricaoTasyModel (identical _CRITERIOS_ALERTA, no calcular_alerta) and TrilhaSeisSintetico ("Profilaxias", different scheme amarelo:3/vermelho:4) -- those are not this rule. verify:false: the alert coloring is an internal product heuristic with no published clinical anchor. Related to RULE-NUTRICAO-003 (shares the payload for criterion detail).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
