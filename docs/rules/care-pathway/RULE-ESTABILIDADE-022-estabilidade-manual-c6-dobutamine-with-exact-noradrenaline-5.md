# RULE-ESTABILIDADE-022 — Estabilidade manual C6 - dobutamine with exact noradrenaline 50

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Flags dobutamine > 10 ml/h together with noradrenaline quantity EXACTLY equal to 50 ml.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| dobutamina | float | ml/h | 0-30 |
| noradrenalina.quantidade | float | ml | 0-200 |

## Outputs

| name | type |
|---|---|
| criterio_6 | bool |

## Logic

```text
dobutamina > 10 AND buscar_quantidade_noradrenalina() == 50
```

## Edge cases (as implemented)

Uses equality == 50 (not >=): noradrenaline 40 or 51 -> False. Test confirms 50->True, 40->False.

## Divergence

Code uses exact equality `== 50` on a continuous noradrenaline dose (clinically implausible; likely intended >= or > 50), while the _REGRAS text "Dobutamina > 10ml/h E Noradrenalina 50 ml/h" is ambiguous about the operator. Also the dobutamina model validator max is 30 yet the threshold is > 10.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published source defines a numeric infusion-volume rule of the form 'dobutamine >10 ml/h AND noradrenaline volume == 50 ml'. Closest clinical anchor: Surviving Sepsis Campaign 2021 (Evans L, et al. Crit Care Med 2021;49(11):e1063-e1143) supports adding dobutamine to norepinephrine in septic shock with cardiac dysfunction/persistent hypoperfusion, but specifies no device-volume thresholds and doses vasopressors by weight-rate (mcg/kg/min), not bag volume (ml). ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| dobutamina=15; noradrenalina.quantidade=50 | no published expected value (n/a) | TRUE (15>10 AND 50==50) | n/a |
| dobutamina=15; noradrenalina.quantidade=40 | n/a | FALSE (40 != 50) | n/a |
| dobutamina=15; noradrenalina.quantidade=51 | n/a — clinically a HIGHER noradrenaline exposure than 50, yet not flagged | FALSE (51 != 50) | n/a |
| dobutamina=10; noradrenalina.quantidade=50 | n/a | FALSE (10 not > 10) | n/a |

**Verifier notes**

Verified against legacy source (trilha_estabilidade.py:137): dobutamina > 10 AND buscar_quantidade_noradrenalina() == 50. The specific numeric thresholds (>10 ml/h dobutamine, exactly 50 ml noradrenaline) are proprietary/internal device-configuration rules with no authoritative published anchor, so they cannot be VERIFIED or refuted against a reference -> UNVERIFIABLE, flag for internal review (do not treat as clinically wrong). FLAGGED FOR INTERNAL REVIEW: the extraction-stage DISCREPANCY is a code-vs-intent anomaly, not a code-vs-reference one — exact equality '== 50' on a continuous noradrenaline volume is clinically implausible (49 or 51 ml -> False), so a genuinely refractory-shock patient at 60 ml would NOT set criterio_6; the sibling v3 criterio_9 uses '> 50', suggesting the intended operator was >= or >. Also the dobutamina model validator max (30) exceeds nothing problematic but the >10 gate sits well inside it. criterio_6 affects calcular_alerta (RULE-023) but is not surfaced by get_payload (iterates 1..5), so the equality bug silently perturbs the alert count only.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_estabilidade.py` | 136-137 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estab-BE-10-024`

**Related rules:**

- [RULE-ESTABILIDADE-009](../alert-threshold/RULE-ESTABILIDADE-009-estabilidade-v3-criterio-9-dobutamine-with-high-dose-noradre.md)
- [RULE-ESTABILIDADE-023](../alert-threshold/RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)

## Notes

Variant of v3 criterio_9 (RULE-009, noradrenaline>50 AND dobutamine>10). criterio_6 is NOT counted by get_payload (iterates only 1..total_criterios=5) but IS counted by calcular_alerta (RULE-023). Unit test test_trilha_estabilidade.py:108-121.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
