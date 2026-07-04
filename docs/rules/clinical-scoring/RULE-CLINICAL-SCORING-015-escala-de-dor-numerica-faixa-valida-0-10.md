# RULE-CLINICAL-SCORING-015 — Escala de Dor numerica - faixa valida (0-10)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Numeric pain-rating score constrained to 0..10.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| escala_dor | int | points (numeric rating scale) | 0-10 |

## Outputs

| name | type | unit |
|---|---|---|
| validated escala_dor | int | points |

## Logic

```text
PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
```

## Edge cases (as implemented)

Inclusive 0..10. This cap is why piora criterio_6 "3+" (dor>10) is unreachable (RULE-piora-BE-06-006, piora-clinica cluster).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Numeric Rating Scale (NRS-11) for pain intensity, 0 (no pain) to 10 (worst pain imaginable); single-item verbal numeric scale, validated against VAS (r=0.86-0.95). Standard 0-10 integer range. ([source](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5043012/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| escala_dor=0 | valid (no pain) | accepted (>=0) | yes |
| escala_dor=10 | valid (worst pain) | accepted (<=10) | yes |
| escala_dor=11 | invalid (above 10) | rejected (MaxValueValidator 10) | yes |
| escala_dor=-1 | invalid (below 0) | rejected (PositiveSmallInteger + MinValueValidator 0) | yes |

**Verifier notes**

Inclusive 0..10 integer bounds match the standard 11-point Numeric Rating Scale for pain. PositiveSmallIntegerField plus MinValueValidator(0)/MaxValueValidator(10) correctly constrains the field. The downstream unreachability of piora criterio_6 (dor>10) is a consequence of this correct cap, not a defect in this rule.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/balanco_hidrico/sinais_vitais.py` | 59-64 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-pain-BE-06-001`

**Related rules:**

- [RULE-CLINICAL-SCORING-016](RULE-CLINICAL-SCORING-016-sinais-de-dor-escala-comportamental-faixa-valida-3-12.md)

## Notes

Consumed by RULE-piora-BE-06-006 (piora-clinica cluster).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
