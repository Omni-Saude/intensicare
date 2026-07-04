# RULE-CLINICAL-SCORING-016 — Sinais de Dor (escala comportamental) - faixa valida (3-12)

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
Behavioral pain-scale score constrained to 3..12.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| sinais_dor | int | points (behavioral pain scale) | 3-12 |

## Outputs

| name | type | unit |
|---|---|---|
| validated sinais_dor | int | points |

## Logic

```text
PositiveSmallIntegerField(validators=[MinValueValidator(3), MaxValueValidator(12)])
```

## Edge cases (as implemented)

Inclusive 3..12. The 3-12 range matches a behavioral pain scale (e.g. BPS). This cap is why piora criterio_7 "3+" (sinais>12) is unreachable (RULE-piora-BE-06-007, piora-clinica cluster).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Payen JF, Bru O, Bosson JL, et al. Assessing pain in critically ill sedated patients by using a behavioral pain scale. Crit Care Med. 2001;29(12):2258-2263. BPS = sum of three subscales (facial expression, upper-limb movements, compliance with mechanical ventilation), each scored 1-4; total range 3 (no pain) to 12 (maximum pain). ([source](https://pubmed.ncbi.nlm.nih.gov/11801819/))

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
| sinais_dor=3 | valid - BPS 3 = no pain (all three subscales at 1) | accepted (>=3, <=12) | yes |
| sinais_dor=12 | valid - BPS 12 = maximum pain (all three subscales at 4) | accepted (>=3, <=12) | yes |
| sinais_dor=2 | invalid - below BPS minimum of 3 | rejected by MinValueValidator(3) | yes |
| sinais_dor=13 | invalid - above BPS maximum of 12 | rejected by MaxValueValidator(12) | yes |

**Verifier notes**

The 3-12 inclusive range exactly matches the Behavioral Pain Scale (BPS, Payen 2001), the standard behavioral pain scale for sedated/ventilated ICU patients (three subscales each 1-4). Field is a bare PositiveSmallIntegerField range validator with no sub-item weighting captured, so only the domain bounds are checkable; they are correct. (Note: an alternative behavioral scale, CPOT, spans 0-8; the 3-12 bounds unambiguously identify BPS, not CPOT.)

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/balanco_hidrico/sinais_vitais.py` | 65-70 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-pain-BE-06-002`

**Related rules:**

- [RULE-CLINICAL-SCORING-015](RULE-CLINICAL-SCORING-015-escala-de-dor-numerica-faixa-valida-0-10.md)

## Notes

Consumed by RULE-piora-BE-06-007 (piora-clinica cluster).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
