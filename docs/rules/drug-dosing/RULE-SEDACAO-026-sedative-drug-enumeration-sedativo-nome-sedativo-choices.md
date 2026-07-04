# RULE-SEDACAO-026 — Sedative drug enumeration (Sedativo.nome_sedativo choices)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Allowed sedative drug choices on the manual-model Sedativo.nome_sedativo field.

## Inputs

| name | type |
|---|---|
| nome_sedativo | str enum |

## Outputs

| name | type |
|---|---|
| stored value | str |

## Logic

```text
choices (stored key -> display label):
  fentanil  -> Fentanil
  midazolam -> Midazolan   # label typo: "Midazolan" (key is "midazolam")
  propofol  -> Propofol
  cetamina  -> Cetamina
  ''        -> Nao informado
```

## Edge cases (as implemented)

Tests create with the display value 'Fentanil'/'Midazolan' rather than the stored key 'fentanil'/'midazolam' (choices not enforced at .create()).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** Devlin JW, Skrobik Y, Gelinas C, et al. Clinical Practice Guidelines for the Prevention and Management of Pain, Agitation/Sedation, Delirium, Immobility, and Sleep Disruption in Adult Patients in the ICU (PADIS). Crit Care Med. 2018;46(9):e825-e873. Used only as a soft clinical-plausibility anchor for the drug list; there is NO authoritative published reference that governs a software field's allowed-choice enumeration (this is an internal data-model / UI validation list). ([source](https://journals.lww.com/ccmjournal/fulltext/2018/09000/clinical_practice_guidelines_for_the_prevention.29.aspx))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | n/a - enum of 5 choices (fentanil, midazolam, propofol, cetamina, ''); source lines 4-13 confirmed verbatim. All four named drugs are recognized ICU sedative/analgesic agents in PADIS 2018. Notable omission: dexmedetomidine (Precedex), which PADIS 2018 recommends over benzodiazepines and which the v3 model DOES track (qt_vol_dex, RULE-SEDACAO-013) - but its absence here is a product-scope decision, not a computational error. |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nome_sedativo=fentanil | Fentanil is a valid ICU analgesic (PADIS 2018) - accepted; stored key 'fentanil', display 'Fentanil' | stored 'fentanil' -> label 'Fentanil' (line 8) | yes |
| nome_sedativo=midazolam | Midazolam is a valid ICU benzodiazepine sedative (PADIS 2018) - accepted; display label should read 'Midazolam' | stored 'midazolam' -> label 'Midazolan' (line 9, spelling typo in display label, verbatim in source) | yes |
| nome_sedativo=cetamina | Ketamine (cetamina) is a recognized ICU analgesic/sedative adjunct (PADIS 2018) - accepted | stored 'cetamina' -> label 'Cetamina' (line 11) | yes |
| nome_sedativo=dexmedetomidina | Dexmedetomidine is a first-line ICU sedative per PADIS 2018 (suggested over benzodiazepines) | NOT an allowed choice in this manual-model enum (absent from lines 4-13); Django choices not enforced at .create() so value could still be stored, but it is not an offered/validated option | no |
| nome_sedativo= | n/a (sentinel 'not informed' value - product convention, no clinical anchor) | stored '' -> label 'Nao informado' (line 12) | yes |

**Verifier notes**

Internal data-model enumeration (SedativoChoices.tipo, trilha_manual/models/choices/sedativos.py:4-13) - proprietary product/UI validation rule with no authoritative published reference; flagged for internal review, not treated as wrong. Two observations for internal review (neither is a verifiable clinical computation error): (1) display-label typo 'Midazolan' for stored key 'midazolam' (cosmetic, verbatim in source per rule notes); (2) dexmedetomidine (Precedex) is offered/tracked in the v3 model (RULE-SEDACAO-013) but is absent from this manual-model choice list, so the two sedation variants have divergent supported-drug sets - a scope inconsistency, not a guideline violation. All four listed drugs (fentanil, midazolam, propofol, cetamina) are clinically valid ICU sedative/analgesic agents under SCCM PADIS 2018. The RULE-SEDACAO-015 overdose criterion (>15 ml) applies drug-agnostically regardless of which of these enum values is selected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/choices/sedativos.py` | 4-13 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-choice-BE-10-071`

**Related rules:**

- [RULE-SEDACAO-013](RULE-SEDACAO-013-sedacao-v3-active-sedative-detection-set-sedativo-em-uso.md)
- [RULE-SEDACAO-015](../care-pathway/RULE-SEDACAO-015-sedation-manual-c1-sedoanalgesia-overdose-any-sedative-15-ml.md)

## Notes

Value 'midazolam' key vs 'Midazolan' label (label typo, verbatim in source). Overdose criterion (RULE-SEDACAO-015) applies regardless of drug. category drug-dosing -> verify true per taxonomy rule.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
