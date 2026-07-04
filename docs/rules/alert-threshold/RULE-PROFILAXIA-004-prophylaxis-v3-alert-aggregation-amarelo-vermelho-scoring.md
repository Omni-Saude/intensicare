# RULE-PROFILAXIA-004 — Prophylaxis v3 alert aggregation (amarelo/vermelho scoring)

| Field | Value |
|---|---|
| Cluster | profilaxia |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Profilaxia v3 alert severity aggregation - criterio_1 raises AMARELO, criterio_9 raises VERMELHO; on NEUTRO the record is marked unassisted.

## Inputs

| name | type | unit |
|---|---|---|
| criterio_1 (amarelo), criterio_9 (vermelho) | boolean |  |

## Outputs

| name | type | unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |  |

## Logic

```text
amarelo = [criterio_1].count(True)
vermelho = [criterio_9].count(True)
if vermelho >= 1: return "VERMELHO"
elif amarelo >= 1: return "AMARELO"
else: return "NEUTRO"
# save(): if alerta == "NEUTRO": assistido = False
```

## Edge cases (as implemented)

Only criterio_1 and criterio_9 are computed by calcular_criterios(); criteria 2..8 are commented out. criterio_4 remains in v1's vermelho tier but is commented out of v3's, so v3 vermelho depends on criterio_9 alone.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_profilaxia.py` | 123-140, 181-190 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-profilaxia-BE-03-091`

**Related rules:**

- [RULE-PROFILAXIA-003](RULE-PROFILAXIA-003-prophylaxis-v1-alert-aggregation-amarelo-vermelho-scoring.md)
- [RULE-PROFILAXIA-005](../care-pathway/RULE-PROFILAXIA-005-prophylaxis-v3-criterio-1-gi-stress-ulcer-lamgd-prophylaxis.md)
- [RULE-PROFILAXIA-006](../care-pathway/RULE-PROFILAXIA-006-prophylaxis-v3-criterio-9-invasive-device-prescribed-vermelh.md)
- [RULE-PROFILAXIA-008](../care-pathway/RULE-PROFILAXIA-008-prophylaxis-v3-reduced-active-criteria-set-facade-lamgd-inse.md)

## Notes

v3 variant of RULE-PROFILAXIA-003. balancos/evolucao/cpoe querysets are keyed by self.leito.nr_atendimento (not self.nr_atendimento) - noted as an implementation detail, not a rule divergence.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
