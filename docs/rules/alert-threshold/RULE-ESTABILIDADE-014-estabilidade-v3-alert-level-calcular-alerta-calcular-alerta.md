# RULE-ESTABILIDADE-014 — Estabilidade v3 alert level (calcular_alerta == calcular_alerta_v2)

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
v3 stability alert: VERMELHO if criterio_7 or criterio_10 set; else AMARELO if criterio_12 or criterio_13 set; else NEUTRO. calcular_alerta and calcular_alerta_v2 are byte-identical; save() uses calcular_alerta_v2.

## Inputs

| name | type |
|---|---|
| criterio_7, criterio_10 (vermelho); criterio_12, criterio_13 (amarelo) | boolean |

## Outputs

| name | type |
|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |

## Logic

```text
amarelo = [criterio_12, criterio_13].count(True)
vermelho = [criterio_7, criterio_10].count(True)
if vermelho >= 1: return "VERMELHO"
elif amarelo >= 1: return "AMARELO"
else: return "NEUTRO"
```

## Edge cases (as implemented)

Only criteria 7, 10, 12, 13 are computed by calcular_criterios (1-6, 8, 9, 11 stay null and never influence the alert). If alerta == "NEUTRO", save() also resets assistido=False.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 117-155, 200-213 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-060`

**Related rules:**

- [RULE-ESTABILIDADE-007](RULE-ESTABILIDADE-007-estabilidade-v3-criterio-7-high-dose-noradrenaline-without-a.md)
- [RULE-ESTABILIDADE-010](../drug-dosing/RULE-ESTABILIDADE-010-estabilidade-v3-criterio-10-antihypertensive-with-active-vas.md)
- [RULE-ESTABILIDADE-012](RULE-ESTABILIDADE-012-estabilidade-v3-criterio-12-antihypertensive-with-recurrent.md)
- [RULE-ESTABILIDADE-013](RULE-ESTABILIDADE-013-estabilidade-v3-criterio-13-recurrent-hypertension-off-vasop.md)
- [RULE-ESTABILIDADE-023](RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)
- [RULE-ESTABILIDADE-025](RULE-ESTABILIDADE-025-estabilizacao-v1-alert-with-criterio-6-combination-clause.md)

## Notes

Model property tipo == 'estabilizacao' and nome == 'Estabilizacao' despite the class being TrilhaEstabilidadeV3Model (naming overlap between the estabilidade and estabilizacao pathways).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
