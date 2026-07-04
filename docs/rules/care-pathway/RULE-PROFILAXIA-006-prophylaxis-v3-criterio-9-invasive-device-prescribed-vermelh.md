# RULE-PROFILAXIA-006 — Prophylaxis v3 criterio_9 - invasive device prescribed (VERMELHO)

| Field | Value |
|---|---|
| Cluster | profilaxia |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
criterio_9 predicate: prescription of double-lumen central venous puncture OR double-lumen hemodialysis catheter OR indwelling bladder catheter (device-associated infection risk trigger).

## Inputs

| name | type | unit |
|---|---|---|
| cpoe.puncao_cateter_duplo, cpoe.cateter_duplo_hemod, cpoe.sonda_vesical_demora | float |  |

## Outputs

| name | type | unit |
|---|---|---|
| criterio_9 | boolean |  |

## Logic

```text
ultima_prescricao = cpoe_leito.first()
return any([
  get_number(cpoe.puncao_cateter_duplo),
  get_number(cpoe.cateter_duplo_hemod),
  get_number(cpoe.sonda_vesical_demora),
]) if ultima_prescricao else False
```

## Edge cases (as implemented)

Uses the latest CPOE prescription only (cpoe_leito.first()).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_profilaxia.py` | 540-563 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-profilaxia-BE-03-093`

**Related rules:**

- [RULE-PROFILAXIA-004](../alert-threshold/RULE-PROFILAXIA-004-prophylaxis-v3-alert-aggregation-amarelo-vermelho-scoring.md)
- [RULE-PROFILAXIA-008](RULE-PROFILAXIA-008-prophylaxis-v3-reduced-active-criteria-set-facade-lamgd-inse.md)
- [RULE-PROFILAXIA-007](RULE-PROFILAXIA-007-prophylaxis-v1-lamgd-stress-ulcer-prophylaxis-mobilization-i.md)

## Notes

VERMELHO criterion. Verified verbatim against source. In v3 the criteria 2-8 exist only as commented-out algorithms (documented but inactive). Recommendation/action text for this criterio_9 lives in the v3 facade RULE-PROFILAXIA-008; the v1 facade equivalent is criterio_9 in RULE-PROFILAXIA-007.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
