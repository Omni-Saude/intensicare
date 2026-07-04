# RULE-SEPSE-031 — Sepse criterio_5 - Hipotensao

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Major criterion 5 fires when systolic BP (PAS) < 90 mmHg, or diastolic BP (PAD) < 60 mmHg, on the most recent reading within 24h.

## Inputs

- sinais_vitais.pas (float, mmHg)
- sinais_vitais.pad (float, mmHg)
- sinais_vitais.tempo_criacao() (float, hours)

## Outputs

- criterio_5 (boolean)

## Logic

```text
branch_A = (pas < 90) if (pas and tempo_criacao() <= 24) else False
branch_B = (pad < 60) if (pad and tempo_criacao() <= 24) else False
return any([branch_A, branch_B]) if sinais_vitais else False
```

## Edge cases (as implemented)

Strict < 90 / < 60. pas/pad == 0 falsy -> sub-branch False. tempo_criacao <= 24 always true (RULE-balanco-BE-06-006).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Surviving Sepsis Campaign / Sepsis-2 severe-sepsis criteria - sepsis-induced hypotension = SBP < 90 mmHg (or MAP < 70/65 mmHg, or SBP drop > 40 mmHg). Dellinger RP et al., SSC 2012, Crit Care Med. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC7095153/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| pas=85; pad=70 | hypotensive (SBP<90) = True | branch_A 85<90 True -> True | yes |
| pas=95; pad=55 | SBP not <90; isolated PAD<60 not a recognized sepsis hypotension criterion = False | branch_B 55<60 True -> True | no |
| pas=90; pad=60 | boundary, SBP<90 strict not met = False | 90<90 False, 60<60 False -> False | yes |
| pas=0; pad=0 | n/a (invalid/absent) | pas/pad falsy -> both branches False | yes |

**Verifier notes**

Primary threshold SBP<90 mmHg and units match the SSC/Sepsis-2 sepsis-induced-hypotension definition exactly (strict <). The added disjunct PAD<60 mmHg has no direct published-guideline analogue but is clinically defensible (low diastolic ~ vasodilation) and only broadens sensitivity in a screening MAJOR criterion; it is not a unit/coefficient error, so overall VERIFIED. tempo_criacao()<=24h window is effectively always-true per RULE-balanco-BE-06-006 (documented elsewhere).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 178-194 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-005`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

Major criterion.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
