# RULE-SEPSE-051 — Sepsis C14 (minor) - leukocytosis in last 24h

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | low |

## Rule
Minor criterion - most-recent 24h leukocytes > 12000/mm3.

## Inputs

- leucocitos (float, /mm3, 0-40000)

## Outputs

- criterio_14 (bool)

## Logic

```text
leucocitos = filter(lookback, criado_em>now-24h).order_by('-criado_em').values_list('leucocitos').first()
(leucocitos > 12000) if leucocitos else False
```

## Edge cases (as implemented)

Strict >12000. From lookback chain. Test 12000->False, 12001->True.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** low
- **Reference:** Bone RC et al. ACCP/SCCM Consensus Conference (1992) Chest 101:1644; Levy MM et al. 2001 SCCM/ESICM/ACCP/ATS/SIS International Sepsis Definitions Conference, Crit Care Med 2003;31:1250. SIRS WBC criterion: >12,000/mm3 OR <4,000/mm3 OR >10% immature (band) forms. ([source](https://www.mdcalc.com/calc/1096/sirs-sepsis-septic-shock-criteria))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | leukocytosis cutoff 12,000/mm3 matches SIRS exactly |
| units | /mm3 (cells/uL) - correct, no unit mismatch |
| ranges | 0-40000 plausible; strict > comparison |
| rounding | n/a (integer count, strict >) |
| cutoffs | > 12000 strict matches SIRS leukocytosis arm; leukopenia (<4000) and bandemia (>10%) arms of the SIRS WBC criterion are NOT implemented (commented out) - scoped to leukocytosis only |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| leucocitos=12000 | not leukocytosis (>12000 strict) -> False | 12000>12000 -> False | yes |
| leucocitos=12001 | leukocytosis -> True | 12001>12000 -> True | yes |
| leucocitos=13000 | leukocytosis -> True | True | yes |
| leucocitos=3000 | SIRS WBC criterion POSITIVE via leukopenia (<4000) | 3000>12000 -> False (leukopenia arm not implemented) | no |

**Verifier notes**

Leukocytosis threshold 12,000/mm3 matches the SIRS/Sepsis-2 WBC criterion exactly (equation, units, cutoff all correct). The rule is deliberately scoped to leukocytosis as a single MINOR criterion; the full SIRS WBC criterion also fires on WBC<4000 or >10% bands, which this active version omits (older leukopenia/delta variant present but commented out, lines 427-456). Missing the leukopenia arm could under-detect neutropenic/immunosuppressed sepsis, but as one minor among many two-axis criteria the impact is low. Falsy guard: leucocitos 0/None -> False. Test test_trilha_sepse.py:226-238.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 392-402 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-039`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

_ANTIGAS_REGRAS C17 was ">15000 OR <4000"; current active version only checks >12000 (no leukopenia branch). The leukopenia/delta variant is commented out (lines 427-456). Test test_trilha_sepse.py:226-238.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
