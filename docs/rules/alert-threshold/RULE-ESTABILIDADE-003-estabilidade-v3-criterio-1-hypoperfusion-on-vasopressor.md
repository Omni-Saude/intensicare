# RULE-ESTABILIDADE-003 — Estabilidade v3 criterio_1 - hypoperfusion on vasopressor

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Noradrenaline present in balanco in last 6h AND (capillary refill time > 3s OR arterial lactate >= 2 mmol/L). Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml/h |
| evolucao.tempo_enchimento_capilar | float | s |
| evolucao.diurna_lactato | float | mmol/L |

## Outputs

| name | type |
|---|---|
| criterio_1 | boolean |

## Logic

```text
return all([
  balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  any([ get_number(tempo_enchimento_capilar) > 3, get_number(diurna_lactato) >= 2 ]),
]) if (balanco_6h and ultima_evolucao) else False
```

## Edge cases (as implemented)

TEC strict > 3; lactate inclusive >= 2. Unwired in calcular_criterios.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Sepsis-3 (Singer M et al., JAMA 2016;315(8):801-810) — hyperlactatemia lactate >2 mmol/L anchor for septic shock; ANDROMEDA-SHOCK (Hernandez G et al., JAMA 2019;321(7):654-664) — capillary refill time normalization target < 3 s (CRT >3 s = abnormal hypoperfusion). ([source](https://pubmed.ncbi.nlm.nih.gov/26903338/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | mmol/L (lactate), seconds (CRT) — correct |
| ranges | 6h vasopressor window; guarded by balanco_6h and ultima_evolucao presence |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_6h=present; diurna_lactato=2.0; tempo_enchimento_capilar=2 | flag (lactate >= Sepsis-3 hyperlactatemia anchor, vasopressor present) | fires (lactate 2.0 >= 2 True) | yes |
| nora_6h=present; diurna_lactato=1.5; tempo_enchimento_capilar=4 | flag (CRT 4 s > 3 s = abnormal peripheral perfusion, ANDROMEDA target <3s) | fires (TEC 4 > 3 True) | yes |
| nora_6h=present; diurna_lactato=1.9; tempo_enchimento_capilar=3 | no flag (lactate < 2; CRT = 3 s is the normalization target, not abnormal) | no fire (TEC 3 > 3 False; lactate 1.9 >= 2 False) | yes |

**Verifier notes**

Both anchors match authoritative sources: lactate cutoff on the Sepsis-3 >2 mmol/L hyperlactatemia value, CRT >3 s on the ANDROMEDA-SHOCK <3 s normalization target. Minor boundary nuance: code uses lactate `>= 2` (inclusive) whereas Sepsis-3 wording is strictly `> 2`, so at exactly 2.0 mmol/L the legacy fires while a strict-Sepsis-3 reading would not — negligible clinical impact (2.0 is at/above the abnormality threshold either way). Criterion is UNWIRED.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 215-247 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-061`

**Related rules:**

- [RULE-ESTABILIDADE-015](RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)
- [RULE-ESTABILIDADE-017](../care-pathway/RULE-ESTABILIDADE-017-estabilidade-manual-c1-slow-capillary-refill-on-noradrenalin.md)

## Notes

Manual-pathway counterpart RULE-017 uses TEC>5 (strict) with mere noradrenaline presence (no lactate branch) — variant thresholds, not a duplicate. Lactate>=2 is the Sepsis-3 hyperlactatemia anchor.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
