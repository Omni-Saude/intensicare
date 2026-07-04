# RULE-SEPSE-043 — Sepsis C6 (major) - hypotension (PAS<90 or PAD<90 in 24h)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | high |

## Rule
Major criterion - current PAS < 90 OR the most recent 24h diastolic (PAD) < 90.

## Inputs

- pas (float, mmHg)
- pad_em_24hrs (float, mmHg)

## Outputs

- criterio_6 (bool)

## Logic

```text
queryset = DadosProntuario.filter(pk__in=buscar_ultimos_dados).order_by('-criado_em')
pad_em_24hrs = queryset.filter(criado_em__gt=now-24h).values_list('pad').first()
any([ (pas < 90) if pas else False, (pad_em_24hrs < 90) if pad_em_24hrs else False ])
```

## Edge cases (as implemented)

pas/pad falsy -> excluded. pad drawn from most recent record in the lookback chain within 24h.

## Divergence

DISCREPANCY: _REGRAS text says "PAS < 90 OU PAD < 60"; code compares PAD < 90 (not 60). _ANTIGAS_REGRAS also mentioned PAM<65. Test test_trilha_sepse.py:124-137 (pas=89 dominates).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** high
- **Reference:** Sepsis-3 / SSC 2021 and prior severe-sepsis criteria (Dellinger/Levy ACCP-SCCM): sepsis-related hypotension = systolic BP < 90 mmHg, MAP < 70 mmHg, or SBP decrease > 40 mmHg from baseline; qSOFA uses SBP <= 100 mmHg. Diastolic BP is not a standard sepsis hypotension trigger; a low diastolic threshold, when used, is ~ < 60 mmHg (physiologic normal diastolic ~ 60-80 mmHg). ([source](https://jamanetwork.com/journals/jama/fullarticle/2492881))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| pas=89; pad=75 | SBP<90 -> hypotension True | true | yes |
| pas=120; pad=75 | SBP normal, diastolic 75 normal -> False | true | no |
| pas=120; pad=85 | normotensive -> False | true | no |
| pas=120; pad=95 | normotensive -> False | false | yes |

**Verifier notes**

Confirmed against reference: the SBP<90 disjunct is correct, but the diastolic disjunct compares PAD < 90 (lines 283-284) instead of the documented PAD < 60. Because a normal diastolic BP is ~60-80 mmHg, PAD < 90 is satisfied by essentially every patient with a recorded diastolic value, so this MAJOR criterion is nearly always True and ceases to discriminate. High impact: it pushes the major-criterion count toward the 2-major alert bar for almost all patients, degrading specificity and driving false-positive sepsis alerts. Matches the extraction's DISCREPANCY status (_REGRAS text says PAD < 60).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 272-286 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-031`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

DISCREPANCY: _REGRAS text says "PAS < 90 OU PAD < 60"; code compares PAD < 90 (not 60). _ANTIGAS_REGRAS also mentioned PAM<65. Test test_trilha_sepse.py:124-137 (pas=89 dominates).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
