# RULE-ESTABILIDADE-025 — Estabilizacao v1 alert with criterio_6 combination clause

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
Color alert for estabilizacao v1 (TrilhaEstabilizacaoModel, db_table AMH_TM_SINTETICO_02_V); criterio_6 alone is insufficient unless combined with another set criterion.

## Inputs

| name | type |
|---|---|
| criterio_1..6 | int flag (1 = present) |

## Outputs

| name | type |
|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |

## Logic

```text
amarelo = [criterio_1, criterio_4].count(1)
vermelho = [criterio_2, criterio_3, criterio_5].count(1)
criterio_6 = [criterio_6].count(1)
if vermelho >= 1: return "VERMELHO"
elif amarelo >= 1 or (criterio_6 == 1 and criterio_6 + amarelo + vermelho >= 2): return "AMARELO"
else: return "NEUTRO"
```

## Edge cases (as implemented)

criterio_6 only escalates to AMARELO when at least one other counted criterion is also set (criterio_6 + amarelo + vermelho >= 2). If vermelho>=1 the criterio_6 clause is unreachable.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha2.py` | 78-97 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilizacao-BE-03-011`

**Related rules:**

- [RULE-ESTABILIDADE-024](../care-pathway/RULE-ESTABILIDADE-024-estabilizacao-trilha2-shock-work-up-vasopressor-escalation-t.md)
- [RULE-ESTABILIDADE-014](RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md)
- [RULE-ESTABILIDADE-023](RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)

## Notes

TrilhaEstabilizacaoTesteModel subclasses this unchanged (db_table AMH_TM_SINTETICO_02_V_TESTE). Internal count->color aggregation, no published anchor -> verify:false.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
