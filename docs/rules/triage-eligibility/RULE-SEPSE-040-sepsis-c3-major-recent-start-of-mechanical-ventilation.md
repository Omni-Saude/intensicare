# RULE-SEPSE-040 — Sepsis C3 (major) - recent start of mechanical ventilation

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
Major criterion - mechanical ventilation started less than 1 day ago.

## Inputs

- ventilacao_mecanica.horario_inicio (datetime)

## Outputs

- criterio_3 (bool)

## Logic

```text
(vm.horario_inicio > now - 1day) if verificar_objeto_existe(dp,'ventilacao_mecanica') else False
```

## Edge cases (as implemented)

Strict > (exactly 24h ago -> False). Test 23h->True, 24h->False, 2d->False.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published equation defines a fixed <24h-from-ventilation-start window as a sepsis criterion. New acute respiratory failure requiring mechanical ventilation is a recognized organ-dysfunction/sepsis marker (Sepsis-3, Singer et al. JAMA 2016; SOFA respiratory component; Surviving Sepsis Campaign 2021), but the specific '<1 day since ventilation start' cutoff is institutional. Internal business rule. ([source](https://pubmed.ncbi.nlm.nih.gov/26903338/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | 1-day (24h) window is institutional, not from a published sepsis criterion |
| units | timedelta(days=1) = 24h; horario_inicio is a datetime; timezone.now() aware comparison |
| ranges | n/a |
| rounding | none; exact datetime comparison |
| cutoffs | strict > (horario_inicio > now - 1day); exactly 24h ago -> False |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| vm_exists=true; horario_inicio=23h ago | n/a (no published cutoff) | 23h-ago > now-24h -> True | yes |
| vm_exists=true; horario_inicio=24h ago exactly | n/a | now-24h > now-24h -> False (boundary excluded) | yes |
| vm_exists=true; horario_inicio=2 days ago | n/a | 48h-ago > now-24h -> False | yes |
| vm_exists=false | n/a | verificar_objeto_existe False -> False | yes |

**Verifier notes**

Internal business rule capturing recently-initiated mechanical ventilation as an acute organ-dysfunction trigger. Logic hand-traces correctly against its documented strict-> boundary (contrast RULE-SEPSE-041 noradrenalina which uses inclusive >=). No authoritative source fixes the 24h window; flag for internal clinical review, not a defect.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 251-257 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-028`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:90-101.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
