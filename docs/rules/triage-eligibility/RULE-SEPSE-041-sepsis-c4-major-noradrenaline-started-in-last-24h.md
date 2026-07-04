# RULE-SEPSE-041 — Sepsis C4 (major) - noradrenaline started in last 24h

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
Major criterion - noradrenaline infusion started within the last 24h.

## Inputs

- noradrenalina.horario_inicio (datetime)

## Outputs

- criterio_4 (bool)

## Logic

```text
(noradrenalina.horario_inicio >= now - 1day) if verificar_objeto_existe(dp,'noradrenalina') else False
```

## Edge cases (as implemented)

Inclusive >= (contrast with C3 strict >). Test 23h->True, 20h->True.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** Singer M et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA 2016;315(8):801-810. Septic shock = vasopressor requirement to maintain MAP>=65 mmHg + lactate >2 mmol/L. No published calculator defines 'noradrenaline started within the last 24h' as a discrete weighted screening item; this is an institutional Trilha-Sepse screening-tool design element. ([source](https://jamanetwork.com/journals/jama/fullarticle/2492881))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| noradrenalina.horario_inicio=23h ago | vasopressor in use -> shock marker (concept-consistent, no numeric ref) | true | yes |
| noradrenalina.horario_inicio=20h ago | vasopressor in use (concept-consistent) | true | yes |
| noradrenalina.horario_inicio=25h ago | n/a (lookback window is internal) | false | yes |
| noradrenalina=object absent | no vasopressor -> False | false | yes |

**Verifier notes**

Vasopressor use as a shock/organ-dysfunction marker is consistent with Sepsis-3, but the specific "noradrenaline started within 24h counts as a MAJOR screening criterion" with an inclusive >= now-1day window is a proprietary institutional rule with no authoritative published equation or cutoff to check against. Legacy (lines 259-267) matches its own docstring (inclusive >=, contrast C3 strict >). Flag for internal clinical review; not treated as wrong.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 259-267 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-029`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:103-113.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
