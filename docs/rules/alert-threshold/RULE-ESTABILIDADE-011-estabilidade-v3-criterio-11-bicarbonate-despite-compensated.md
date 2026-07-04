# RULE-ESTABILIDADE-011 — Estabilidade v3 criterio_11 - bicarbonate despite compensated acidosis

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Bicarbonate > 16 mEq/L AND pH > 7.2 (flags inappropriate bicarbonate use). Bicarbonate- prescription precondition noted as missing in a code comment. Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| evolucao.diurna_bicabornato | float | mEq/L |
| evolucao.diurna_ph | float |  |

## Outputs

| name | type |
|---|---|
| criterio_11 | boolean |

## Logic

```text
return all([
  # code comment: "falta prescricao de bicarbonato" (bicarbonate-prescription check NOT implemented)
  get_number(evolucao.diurna_bicabornato) > 16,
  get_number(evolucao.diurna_ph) > 7.2,
]) if (ultima_evolucao and ultima_cpoe) else False
```

## Edge cases (as implemented)

The documented bicarbonate-prescription precondition is absent (comment only). Strict thresholds bicarbonato>16, pH>7.2. Unwired.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Surviving Sepsis Campaign 2021 (Evans et al., Crit Care Med 2021;49:e1063-e1143): "suggest against using sodium bicarbonate therapy to improve hemodynamics or reduce vasopressor requirements in patients with hypoperfusion-induced lactic acidemia and pH >= 7.15"; suggest bicarbonate for severe metabolic acidemia (pH <= 7.2) WITH AKIN 2-3 (BICAR-ICU, Jaber et al., Lancet 2018). ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | ok |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| diurna_bicabornato=20; diurna_ph=7.3 | bicarbonate NOT indicated (pH>7.15) -> flag inappropriate use = fire | 20>16 True AND 7.30>7.2 True -> criterio_11 = True (fires) | yes |
| diurna_bicabornato=14; diurna_ph=7.1 | severe acidemia pH<=7.15 (+AKI) may warrant bicarbonate -> do NOT flag | 14>16 False -> criterio_11 = False (does not fire) | yes |
| diurna_bicabornato=17; diurna_ph=7.18 | pH 7.18 > 7.15 -> bicarbonate not indicated -> should flag inappropriate use | 17>16 True AND 7.18>7.2 False -> criterio_11 = False (does NOT flag) | no |
| diurna_bicabornato=16; diurna_ph=7.25 | BIC exactly 16, pH>7.15 -> bicarbonate not indicated -> should flag | 16>16 False (strict >) -> criterio_11 = False | no |

**Verifier notes**

Concept (flag bicarbonate when acidosis not severe) is guideline-concordant. Cutoff diverges: code uses pH>7.2 whereas SSC-2021 (and the paired facade text RULE-015 criterio_11) use pH 7.15 as the "bicarbonate not indicated" boundary, so the code fails to flag inappropriate bicarbonate in the narrow 7.15<pH<=7.2 band, and never fires at BIC exactly 16 (strict >). Additionally the code comment "falta prescricao de bicarbonato" confirms the bicarbonate-PRESCRIPTION precondition is unimplemented, so the flag cannot actually confirm bicarbonate "use". Impact low: advisory-only, unwired criterion, narrow pH band, conservative (under-flags) direction.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 592-612 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-071`

**Related rules:**

- [RULE-ESTABILIDADE-015](RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)

## Notes

Complementary framing to facade criterio_11 ("Indicar apenas se pH<7,15 e BIC<16"): the facade states WHEN bicarbonate is appropriate, this predicate flags the inverse (BIC>16 & pH>7.2 = bicarbonate NOT indicated). SSC/acid-base bicarbonate anchor.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
