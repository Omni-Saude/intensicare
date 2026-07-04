# RULE-ALERTAS-004 — Single-criterion alert flag (esta_alerta)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A criterion is 'in alert' iff its value equals exactly 1.

## Inputs

- valor (integer; 0 | 1 as used)

## Outputs

- esta_alerta (boolean)

## Logic

```text
return valor == 1
# trilha_automatica/utils.py: if valor == 1: return True else: return False
# core/utils.py:            return valor == 1
```

## Edge cases (as implemented)

Strict equality to 1; any other value (0, 2, None) -> False.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/utils.py` | 1-5 | `8166c07eae` | primary |
| ahlabs-trilhas | `core/utils.py` | 14-15 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ALERT-BE-12-008`

**Related rules:**

- [RULE-ALERTAS-001](RULE-ALERTAS-001-count-triggered-criteria-contar-qtd-criterios-alerta.md)

## Notes

Two backend copies: trilha_automatica/utils.py uses an if/else returning True/False; core/utils.py uses `return valor == 1`. Functionally identical (both return the boolean valor == 1); no behavioral divergence.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
