# RULE-SEDACAO-014 — Sedacao v3 alert (calcular_alerta_v2 used; legacy calcular_alerta present but unused)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Active sedation v3 alert (save -> calcular_alerta_v2). A legacy calcular_alerta variant also exists but is not called.

## Inputs

| name | type |
|---|---|
| criterio_1, criterio_5, criterio_7, criterio_8 | boolean |

## Outputs

| name | type |
|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |

## Logic

```text
# USED (save -> calcular_alerta_v2):
amarelo  = [criterio_5, criterio_7].count(True)
vermelho = [criterio_1, criterio_8].count(True)
if vermelho >= 1: return "VERMELHO"
elif amarelo  >= 1: return "AMARELO"
else: return "NEUTRO"
# UNUSED legacy calcular_alerta: amarelo=[c4,c7,c9,c10,c11,c12] (>=2), vermelho=[c1,c2,c3,c6,c5,c8] (>=1)
```

## Edge cases (as implemented)

Only c1,c5,c7,c8 are computed in calcular_criterios; other criteria remain null. save() also resets assistido=False when alerta==NEUTRO.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 120-166, 248-260 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-040`

**Related rules:**

- [RULE-SEDACAO-005](../drug-dosing/RULE-SEDACAO-005-sedacao-v3-criterio-1-excessive-continuous-sedation-infusion.md)
- [RULE-SEDACAO-009](../drug-dosing/RULE-SEDACAO-009-sedacao-v3-criterio-5-no-morning-sedation-reduction-1-2.md)
- [RULE-SEDACAO-001](../clinical-scoring/RULE-SEDACAO-001-sedacao-v3-criterio-7-moderate-pain-analog-4-6-bps-7-9-two-c.md)
- [RULE-SEDACAO-002](../clinical-scoring/RULE-SEDACAO-002-sedacao-v3-criterio-8-severe-pain-analog-7-10-bps-10-12-two.md)
- [RULE-SEDACAO-021](RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)
- [RULE-SEDACAO-023](RULE-SEDACAO-023-sedacao-v1-alert-trilhasedacaomodel-calcular-alerta.md)

## Notes

Confirmed at source: save() (lines 65-70) -> calcular_criterios() then calcular_alerta_v2(). Legacy calcular_alerta (lines 120-146) requires amarelo>=2 and references criteria never computed; unused. Alert-count aggregation with no published clinical anchor -> verify false. Variant of RULE-SEDACAO-021 (manual) and RULE-SEDACAO-023 (v1).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
