# RULE-SEDACAO-015 — Sedation manual C1 - sedoanalgesia overdose (any sedative >15 ml)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | care-pathway |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Flags any single sedative dose above 15 ml as overdose.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| sedativos.quantidade (max) | int | ml | 0-30 |

## Outputs

| name | type |
|---|---|
| criterio_1 | boolean |

## Logic

```text
verificar_quantidade_max_sedativos() = max(sedativos.values_list('quantidade')) if sedativos exist else 0
criterio_1 = verificar_quantidade_max_sedativos() > 15
```

## Edge cases (as implemented)

No sedatives -> max returns 0 -> False. Strict >15 (exactly 15 does not trigger).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 103-111 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-011`

**Related rules:**

- [RULE-SEDACAO-021](../alert-threshold/RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)
- [RULE-SEDACAO-026](../drug-dosing/RULE-SEDACAO-026-sedative-drug-enumeration-sedativo-nome-sedativo-choices.md)

## Notes

Test test_trilha_sedacao.py:47-53. Institutional 15ml threshold (no published anchor) -> verify false.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
