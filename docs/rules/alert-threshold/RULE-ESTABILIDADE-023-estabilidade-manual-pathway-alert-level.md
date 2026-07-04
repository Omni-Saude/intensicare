# RULE-ESTABILIDADE-023 — Estabilidade manual pathway alert level

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Maps count of satisfied manual stability criteria (1..6) to a 3-level alert.

## Inputs

| name | type | range |
|---|---|---|
| criterios_true_count | int | 0-6 |

## Outputs

| name | type |
|---|---|
| alerta | str enum {VERMELHO, AMARELO, NEUTRO} |

## Logic

```text
n = count(True among criterio_1..6)
if n >= 3: 'VERMELHO'
elif n > 0: 'AMARELO'
else: 'NEUTRO'
```

## Edge cases (as implemented)

calcular_alerta counts all 6 criteria (including criterio_6). get_payload, however, iterates only criterio_1..5 (_REGRAS total_criterios=5), so criterio_6 is invisible in the payload yet still affects the alert. Test reaches VERMELHO with c2+c4+c5.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_estabilidade.py` | 139-153 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estab-BE-10-025`

**Related rules:**

- [RULE-ESTABILIDADE-017](../care-pathway/RULE-ESTABILIDADE-017-estabilidade-manual-c1-slow-capillary-refill-on-noradrenalin.md)
- [RULE-ESTABILIDADE-018](../care-pathway/RULE-ESTABILIDADE-018-estabilidade-manual-c2-noradrenaline-started-in-last-24h.md)
- [RULE-ESTABILIDADE-019](../care-pathway/RULE-ESTABILIDADE-019-estabilidade-manual-c3-high-noradrenaline-without-rescue-the.md)
- [RULE-ESTABILIDADE-020](../care-pathway/RULE-ESTABILIDADE-020-estabilidade-manual-c4-elevated-arterial-lactate.md)
- [RULE-ESTABILIDADE-021](../care-pathway/RULE-ESTABILIDADE-021-estabilidade-manual-c5-antihypertensive-with-adequate-pressu.md)
- [RULE-ESTABILIDADE-022](../care-pathway/RULE-ESTABILIDADE-022-estabilidade-manual-c6-dobutamine-with-exact-noradrenaline-5.md)
- [RULE-ESTABILIDADE-014](RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md)
- [RULE-ESTABILIDADE-025](RULE-ESTABILIDADE-025-estabilizacao-v1-alert-with-criterio-6-combination-clause.md)

## Notes

Internal count->color aggregation, no published anchor -> verify:false. get_alerta/get_payload label the manual trilha nome='Estabilizacao', tipo='estabilizacao'. Unit test test_trilha_estabilidade.py:123-138.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
