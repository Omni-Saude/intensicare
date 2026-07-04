# RULE-ESTABILIDADE-021 — Estabilidade manual C5 - antihypertensive with adequate pressure/noradrenaline

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Flags presence of antihypertensive together with (noradrenaline present OR PAS>90).

## Inputs

| name | type | unit |
|---|---|---|
| anti_hipertensivo | bool |  |
| noradrenalina_exists | bool |  |
| pas | float | mmHg |

## Outputs

| name | type |
|---|---|
| criterio_5 | bool |

## Logic

```text
anti_hipertensivo AND (verificar_objeto_existe(dados_prontuario, 'noradrenalina') OR pas > 90)
```

## Edge cases (as implemented)

Strict pas>90 (pas==90 -> needs noradrenaline). Test pas=95 -> True.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_estabilidade.py` | 132-134 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estab-BE-10-023`

**Related rules:**

- [RULE-ESTABILIDADE-010](../drug-dosing/RULE-ESTABILIDADE-010-estabilidade-v3-criterio-10-antihypertensive-with-active-vas.md)
- [RULE-ESTABILIDADE-023](../alert-threshold/RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)

## Notes

Variant of v3 criterio_10 (RULE-010, antihypertensive + noradrenaline>50 ml/h). Medication- conflict pathway trigger with a generic BP threshold -> verify:false. Unit test test_trilha_estabilidade.py:95-106.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
