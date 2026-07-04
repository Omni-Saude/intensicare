# RULE-PROFILAXIA-008 — Prophylaxis v3 - reduced active criteria set facade (LAMGD + insertion bundle only)

| Field | Value |
|---|---|
| Cluster | profilaxia |
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
profilaxia v3 facade recommendation catalog returning ONLY criterio_1 (LAMGD prophylaxis) and criterio_9 (invasive-procedure insertion bundle); criteria 2-8 are commented out in source.

## Inputs

| name | type | unit |
|---|---|---|
| criterio_1 / criterio_9 flags | bool |  |

## Outputs

| name | type | unit |
|---|---|---|
| alerta + recomendacoes | string |  |

## Logic

```text
criterio_1 ausencia de profilaxia LAMGD -> esomeprazol VO/SNE
           (preferencialmente) ou pantoprazol VO ou cimetidina EV ou
           omeprazol VO/EV.
criterio_9 procedimento invasivo -> preencher Bundle de prevencao de IRAs
           associado a dispositivo (presencial ou a distancia).
```

## Edge cases (as implemented)

The commented-out criteria 3-8 in this file are copy-pasted SEPSE thresholds (Falencia respiratoria VMI iniciada <24h, Hipotensao refrataria DVA <6h, PAS<90/PAM<60, TEC>3s, lactato>=3 mmol/L, oliguria diurese<=0.5 ml/kg/h) that do NOT belong to prophylaxis - dead code, ignored by runtime.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_profilaxia_v3.py` | 1-51 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-profilaxia-BE-01-008`

**Related rules:**

- [RULE-PROFILAXIA-007](RULE-PROFILAXIA-007-prophylaxis-v1-lamgd-stress-ulcer-prophylaxis-mobilization-i.md)
- [RULE-PROFILAXIA-004](../alert-threshold/RULE-PROFILAXIA-004-prophylaxis-v3-alert-aggregation-amarelo-vermelho-scoring.md)
- [RULE-PROFILAXIA-005](RULE-PROFILAXIA-005-prophylaxis-v3-criterio-1-gi-stress-ulcer-lamgd-prophylaxis.md)
- [RULE-PROFILAXIA-006](RULE-PROFILAXIA-006-prophylaxis-v3-criterio-9-invasive-device-prescribed-vermelh.md)

## Notes

Consumed by trilha_automatica/models/trilhas_v3/trilha_profilaxia.py (predicates RULE-PROFILAXIA-005/006). AMBIGUOUS because the v3 catalog is far sparser than the v1 catalog (RULE-PROFILAXIA-007) yet is the active payload for the v3 model - unclear whether intentional narrowing or incomplete migration. NOT merged with v1 (variant), NOT merged with the v3 predicates (facade covers two criteria; predicates are per-criterion) - cross-referenced via related instead.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
