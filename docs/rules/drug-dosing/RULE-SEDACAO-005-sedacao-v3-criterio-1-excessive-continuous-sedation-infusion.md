# RULE-SEDACAO-005 — Sedacao v3 criterio_1 - excessive continuous sedation infusion

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Any of midazolam>=15 OR propofol>=20 OR fentanil>=15 OR cetamina>=15 OR dexmedetomidina>=15 ml/h recorded in the fluid balance in the last 4h. Wired VERMELHO criterion; also calls set_sedativo_em_uso to label the active drug.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_mid/pro/fen/cet/dex | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_1 | boolean |

## Logic

```text
balanco_4h = balancos(dt_atualizacao_balanco >= now - 4h)
set_sedativo_em_uso(balanco_4h.first())      # RULE-SEDACAO-013
return any([
  balanco_4h.filter(qt_vol_mid__gte=15),
  balanco_4h.filter(qt_vol_pro__gte=20),
  balanco_4h.filter(qt_vol_fen__gte=15),
  balanco_4h.filter(qt_vol_cet__gte=15),
  balanco_4h.filter(qt_vol_dex__gte=15),
]) if balanco_4h else False
```

## Edge cases (as implemented)

any() over QuerySet objects (truthy if non-empty). Thresholds use >= (REFATORADO). Prior "ANTERIOR" thresholds documented in code: mid>10, pro>16, fen>15, cet>10, precedex>14.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published clinical anchor exists for continuous-sedative infusion thresholds expressed in ml/h. Guideline dosing (SCCM PADIS 2018; product labels) is weight-based: propofol mcg/kg/min, midazolam mg/kg/h, fentanil mcg/kg/h, dexmedetomidine mcg/kg/h, ketamine mg/kg/h. Converting a ml/h volume threshold to a dose requires the institution's specific drug concentration, which is an internal/pharmacy standard, not a published value. ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/2018-pain-agitation-delirium))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | thresholds mid>=15, pro>=20, fen>=15, cet>=15, dex>=15 are ml/h volume rates - institutional, not weight-normalized |
| units | UNVERIFIABLE - ml/h cannot be mapped to published mcg/kg/min or mg/kg/h anchors without the institution's concentration and patient weight |
| ranges | n/a |
| rounding | n/a |
| cutoffs | >= thresholds (REFATORADO); prior ANTERIOR set mid>10/pro>16/fen>15/cet>10/precedex>14 documented in code |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_mid=15 | no published ml/h anchor to compare | qt_vol_mid>=15 -> non-empty queryset -> criterio_1 True (VERMELHO) | n/a |
| qt_vol_pro=18 | no published anchor | 18>=20 False -> that filter empty; criterio_1 driven by other drugs only | n/a |
| qt_vol_dex=20 | no published anchor | qt_vol_dex>=20>=15 -> True; set_sedativo_em_uso labels Precedex | n/a |

**Verifier notes**

Flag for internal review, NOT wrong. The criterion compares volumetric infusion rates (ml/h) against fixed cutoffs; without the institution's standardized drug concentrations these cannot be reconciled with any published weight-based dosing guideline (mcg/kg/min etc). This is an internal pharmacy/protocol business rule. Logic itself is coherent: any() over non-empty QuerySets, >= thresholds (REFATORADO), and it wires set_sedativo_em_uso (RULE-SEDACAO-013) to label the active drug. Wired VERMELHO criterion. Source lines 262-291 verified.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 262-291 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-042`

**Related rules:**

- [RULE-SEDACAO-013](RULE-SEDACAO-013-sedacao-v3-active-sedative-detection-set-sedativo-em-uso.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)
- [RULE-SEDACAO-025](RULE-SEDACAO-025-sedative-specific-reduction-recommendation-criterio-1-free-t.md)

## Notes

Wired VERMELHO criterion. Prior thresholds retained in docstring. Verified against source (lines 262-291).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
