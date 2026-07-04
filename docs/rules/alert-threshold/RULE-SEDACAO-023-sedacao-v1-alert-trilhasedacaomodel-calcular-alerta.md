# RULE-SEDACAO-023 — Sedacao v1 alert (TrilhaSedacaoModel.calcular_alerta)

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
Color alert for the v1 sedation trilha from a fixed subset of integer-flag criteria.

## Inputs

| name | type |
|---|---|
| criterio_1, criterio_2, criterio_4, criterio_6 | int flag (1 = present) |

## Outputs

| name | type |
|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |

## Logic

```text
amarelo  = [criterio_1, criterio_2].count(1)
vermelho = [criterio_4, criterio_6].count(1)
if vermelho >= 1: return "VERMELHO"
elif amarelo  >= 1: return "AMARELO"
else: return "NEUTRO"
```

## Edge cases (as implemented)

Counts only the exact integer value 1 (not other truthy ints). Runs on every save().

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha1.py` | 108-123 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-010`

**Related rules:**

- [RULE-SEDACAO-014](RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)
- [RULE-SEDACAO-021](RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)
- [RULE-SEDACAO-024](../drug-dosing/RULE-SEDACAO-024-sedation-analgesia-pathway-recommendation-catalog-facade-tex.md)
- [RULE-SEDACAO-025](../drug-dosing/RULE-SEDACAO-025-sedative-specific-reduction-recommendation-criterio-1-free-t.md)

## Notes

Persisted to alerta field in save() (lines 96-98). Superseded conceptually by TrilhaSedacaoV3Model (RULE-SEDACAO-014). Variant, not duplicate. Alert-count aggregation, no published anchor -> verify false.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
