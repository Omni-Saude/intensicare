# RULE-SEDACAO-003 — Sedacao v3 criterio_9 - deep sedation RASS -3..-5 (defined, unwired)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | clinical-scoring |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | none |

## Rule
Intended: RASS between -3 and -5 on the daytime medical evolution AND sedoanalgesia justification in {Outros, Fase aguda de choque septico}.

## Inputs

| name | type | unit |
|---|---|---|
| evolucao.rass | int | RASS |
| evolucao.diurna_sedoanalgesia | string |  |

## Outputs

| name | type |
|---|---|
| criterio_9 | boolean |

## Logic

```text
return all([
  (-3 <= int(evolucao.rass) <= -5) if evolucao.rass else False,
  evolucao.diurna_sedoanalgesia in ["Outros", "Fase aguda de choque septico"],
]) if ultima_evolucao else False
```

## Edge cases (as implemented)

Compound comparison -3 <= x <= -5 is unsatisfiable (requires x>=-3 AND x<=-5); criterion always False when reached. Unwired anyway.

## Divergence

Code (line 698) writes `-3 <= int(rass) <= -5`, which no RASS value can satisfy (needs rass>=-3 AND rass<=-5). Intended per docstring is RASS -3 to -5, i.e. `-5 <= rass <= -3`. As written the criterion is always False. Bug is inert because criterio_9 is not called by calcular_criterios (unwired).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** none
- **Reference:** Richmond Agitation-Sedation Scale (Sessler CN et al. Am J Respir Crit Care Med 2002), range +4 to -5; deep sedation defined as RASS -3 to -5 (-3 moderate, -4 deep, -5 unarousable). ([source](https://clinicaltoolslibrary.com/richmond-agitation-sedation-scale-rass/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | intended band RASS -5..-3 matches reference deep-sedation band exactly |
| units | ok (RASS integer) |
| ranges | reference band -5..-3 valid; code interval -3<=x<=-5 is empty (unsatisfiable) |
| rounding | n/a |
| cutoffs | code bound order reversed -> criterion can never be True |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| rass=-5; diurna_sedoanalgesia=Outros | deep sedation, justification match -> True | -3<=-5 is False -> criterion False | no |
| rass=-4; diurna_sedoanalgesia=Fase aguda de choque septico | deep sedation -> True | -3<=-4 is False -> False | no |
| rass=-3; diurna_sedoanalgesia=Outros | moderate/deep boundary -> True | -3<=-3 True but -3<=-5 False -> False | no |

**Verifier notes**

Reference-confirmed: the intended band (RASS -5 to -3) is exactly the published deep-sedation band. The legacy code writes `-3 <= int(rass) <= -5`, an empty interval, so criterio_9 is always False for every valid RASS value. This is a confirmed reversed-bound bug. Clinical impact = none because criterio_9 is UNWIRED (not called by calcular_criterios); were it wired, impact would be moderate (deep-oversedation flag would never fire). Preserved verbatim per instructions; source lines 687-707.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 687-707 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-050`

**Related rules:**

- [RULE-SEDACAO-004](RULE-SEDACAO-004-sedacao-v3-criterio-12-weaning-readiness-defined-unwired-bad.md)

## Notes

DISCREPANCY - bound order reversed. Preserve verbatim, do not correct. Unwired.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
