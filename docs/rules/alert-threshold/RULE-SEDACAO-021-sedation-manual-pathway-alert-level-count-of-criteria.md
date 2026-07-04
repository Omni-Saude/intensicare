# RULE-SEDACAO-021 — Sedation manual pathway alert level (count of criteria)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Maps count of satisfied sedation criteria (criterio_1..6) to a 3-level alert.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| criterios_true_count | int | count of criterio_1..6 == True | 0-6 |

## Outputs

| name | type |
|---|---|
| alerta | str enum {VERMELHO, AMARELO, NEUTRO} |

## Logic

```text
n = [criterio_1..criterio_6].count(True)
if n >= 3: return 'VERMELHO'
elif n > 0: return 'AMARELO'
else: return 'NEUTRO'
```

## Edge cases (as implemented)

Exactly 3+ -> red; 1-2 -> yellow; 0 -> neutral.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 174-188 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-017`

**Related rules:**

- [RULE-SEDACAO-014](RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)
- [RULE-SEDACAO-023](RULE-SEDACAO-023-sedacao-v1-alert-trilhasedacaomodel-calcular-alerta.md)

## Notes

Same count->color scheme as Estabilidade. Distinct from v3 (RULE-SEDACAO-014) and v1 (RULE-SEDACAO-023) alert logics (variant, not duplicate). Alert-count aggregation, no published anchor -> verify false. Test test_trilha_sedacao.py:170-189.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
