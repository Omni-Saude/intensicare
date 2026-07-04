# RULE-EQUILIBRIO-003 — Equilibrio trilha alert-color aggregation (v1, TrilhaEquilibrioModel.calcular_alerta)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | equilibrio |

## Rule
Persisted alert-color for the Equilibrio trilha, computed from which specific criteria flags are set. Value is stored to self.alerta in save() and surfaced via get_payload()/get_detalhe().

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_3, criterio_6, criterio_8 (amarelo set) | int flag (truthy) | — | — |
| criterio_1, criterio_9 (vermelho set) | int flag (truthy) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} | — |

## Logic
```text
amarelo  = [criterio_3, criterio_6, criterio_8].count(True)
vermelho = [criterio_1, criterio_9].count(True)
if vermelho >= 1:   return "VERMELHO"
elif amarelo >= 1:  return "AMARELO"
else:               return "NEUTRO"
# criterios_mensagem (message-eligible criteria) = [criterio_1, criterio_9]
# get_detalhe() surfaces criteria in [1, 3, 6, 8, 9] only.
```

## Edge cases (as implemented)
In save(), when alerta == "NEUTRO" the model also resets assistido=False. Only criteria 1,3,6,8,9 influence the color; criteria 2,4,5,7,10 never change it.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilha7.py | 87-91, 124-143 | 8166c07e | primary |

- Merged from: RULE-equilibrio-BE-03-018
- Related rules: RULE-EQUILIBRIO-001, RULE-EQUILIBRIO-002, RULE-EQUILIBRIO-004

## Notes
Live/authoritative path is calcular_alerta() (specific-criteria) - used in save() and exposed through get_payload()/get_detalhe(). A second, COUNT-based path coexists in the same class (generate_view_data() -> define_tipo_alerta(conta_criterios_automatica(), _CRITERIOS_ALERTA={amarelo:2, vermelho:3}), i.e. NEUTRO<2, AMARELO=1-2, VERMELHO>=3 over all 10 flags) but is DEAD: its only caller is a commented-out line at trilha_automatica/api/v1/views/trilhas.py:59. Because it is not wired, this is NOT a live divergence and status stays OK (no DISCREPANCY manufactured from dead code). Separately, a version variant TrilhaSeteSintetico (db_table trilha_automatica7) computes the color count-based with _CRITERIOS_ALERTA={amarelo:4, vermelho:5} and surfaces ALL 10 criteria in get_detalhe() - a SEPARATE variant of the same pathway (not merged; no Phase-1 provisional ID was captured for it). verify=false: internal UI severity mapping, no published clinical anchor.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
