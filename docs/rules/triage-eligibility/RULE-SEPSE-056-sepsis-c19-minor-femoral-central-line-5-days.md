# RULE-SEPSE-056 — Sepsis C19 (minor) - femoral central line > 5 days

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Minor criterion - CVC/CDL in femoral site for more than 5 days (boolean flag).

## Inputs

- cvc_cdl_femoral_5_dias (bool)

## Outputs

- criterio_19 (bool)

## Logic

```text
return dp.cvc_cdl_femoral_5_dias
```

## Edge cases (as implemented)

Direct boolean passthrough. Test False->False, True->True.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No validated published equation/cutoff. Directional support: CDC/HICPAC Guidelines for the Prevention of Intravascular Catheter-Related Infections (2011) — femoral CVC site carries higher colonization/CLABSI risk; and Sepsis-3 (Singer et al., JAMA 2016) uses source identification but no femoral-dwell-time criterion. The specific '>5 days femoral CVC = minor sepsis screening criterion' is an institutional (Albert Einstein / trilhas) screening rule. ([source](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infection/index.html))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a (boolean flag; the '5 dias' threshold is applied upstream in the data layer, out of this rule's scope) |
| ranges | n/a |
| rounding | n/a |
| cutoffs | unverifiable — 5-day femoral dwell cutoff is institutional, no authoritative source |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| cvc_cdl_femoral_5_dias=false | false (institutional passthrough) | false | yes |
| cvc_cdl_femoral_5_dias=true | true (institutional passthrough) | true | yes |
| cvc_cdl_femoral_5_dias= | n/a (no null handling; predicate out of scope) | null (returns flag unchanged) | yes |

**Verifier notes**

Legacy calcular_criterio_19 (trilha_sepse.py:477-482) is a pure boolean passthrough of dados_prontuario.cvc_cdl_femoral_5_dias; the passthrough logic is trivially faithful to source. The clinical validity lies entirely in the upstream 5-day femoral-catheter flag, which is an institutional infection-source screening criterion with no primary published derivation. Flag for internal clinical review, not a defect.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 477-482 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-044`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:279-282.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
