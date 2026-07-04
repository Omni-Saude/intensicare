# RULE-SEDACAO-025 — Sedative-specific reduction recommendation (criterio_1 free text by active drug)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Maps the active continuous sedative (DS_SEDATIVO_CRITERIO_1) to a free-text recommendation to reduce that drug's infusion rate and optionally combine adjuncts. Appended to the crit1 detalhe payload.

## Inputs

| name | type |
|---|---|
| DS_SEDATIVO_CRITERIO_1 | string enum {Midazolam, Propofol, Cetamina, Precedex, Fentanil} |

## Outputs

| name | type |
|---|---|
| recomendacao | string |

## Logic

```text
if   DS_SEDATIVO_CRITERIO_1 == "Midazolam": reduce Midazolam rate; combine propofol/cetamina + adjuncts
elif DS_SEDATIVO_CRITERIO_1 == "Propofol":  reduce Propofol; combine midazolam/cetamina + adjuncts
elif DS_SEDATIVO_CRITERIO_1 == "Cetamina":  reduce Cetamina; combine midazolam/propofol + adjuncts
elif DS_SEDATIVO_CRITERIO_1 == "Precedex":  reduce Precedex; combine adjuncts (neurolepticos, clonidina, metadona...)
elif DS_SEDATIVO_CRITERIO_1 == "Fentanil":  reduce Fentanil; combine propofol/midazolam/cetamina + adjuncts
else: recomendacao = ""
```

## Edge cases (as implemented)

In the v1 TrilhaSedacaoModel (trilha1.py:175-204) this method is BROKEN: only the first (Midazolam) branch assigns; subsequent branches are bare string literals not concatenated into `recomendacao` (dead text). The v3 version (trilha_sedacao.py:209-246) fixes it with proper parenthesized concatenation.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published source prescribes these drug-specific free-text substitution strings (reduce active sedative + combine named alternative agents/adjuncts). It is an internal recommendation-text mapping keyed on DS_SEDATIVO_CRITERIO_1. The general direction (reduce the offending continuous sedative, favor multimodal/adjunct agents) is consistent with SCCM PADIS 2018 analgosedation principles but the exact per-drug wording is proprietary/institutional. ([source](https://journals.lww.com/ccmjournal/fulltext/2018/09000/clinical_practice_guidelines_for_the_prevention.29.aspx))

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
| DS_SEDATIVO_CRITERIO_1=Midazolam | reduce midazolam, offer alternative agent + adjuncts (proprietary text) | v3 (primary): assigns reduce-Midazolam text with concatenated adjuncts | yes |
| DS_SEDATIVO_CRITERIO_1=Propofol | reduce propofol, offer midazolam/cetamina + adjuncts | v3: correct; v1 variant (trilha1.py:175-204): branch is a bare string literal NOT concatenated -> dead text (bug) | yes |
| DS_SEDATIVO_CRITERIO_1=Precedex | reduce dexmedetomidine, offer neuroleptics/clonidine/methadone adjuncts | v3: correct concatenation; v1: dead text (bug) | yes |
| DS_SEDATIVO_CRITERIO_1=Fentanil | reduce fentanyl, offer propofol/midazolam/cetamina + adjuncts | v3: correct; v1: dead text; note 'Fentanill' spelling in both | yes |
| DS_SEDATIVO_CRITERIO_1= | no recommendation | recomendacao = '' (empty) | yes |

**Verifier notes**

Proprietary free-text drug-substitution recommendations; no citable equation/cutoff/coefficient to verify — flag for internal review, not treated as wrong. Documented implementation defect for internal attention: the v1 variant (trilha1.py:175-204) only assigns the first (Midazolam) branch; the Propofol/ Cetamina/Precedex/Fentanil branches are bare unconcatenated string literals (dead text). The v3 primary source (trilhas_v3/trilha_sedacao.py:209-246) fixes this with parenthesized concatenation. "Fentanill" misspelling present in both variants (cosmetic). Preserved verbatim per audit rules.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 209-246 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_automatica/models/trilha1.py` | 175-204 | `8166c07eae` | variant |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-021`

**Related rules:**

- [RULE-SEDACAO-013](RULE-SEDACAO-013-sedacao-v3-active-sedative-detection-set-sedativo-em-uso.md)
- [RULE-SEDACAO-005](RULE-SEDACAO-005-sedacao-v3-criterio-1-excessive-continuous-sedation-infusion.md)
- [RULE-SEDACAO-024](RULE-SEDACAO-024-sedation-analgesia-pathway-recommendation-catalog-facade-tex.md)

## Notes

v1 (trilha1.py:175-204) is the buggy variant of the same recommendation, kept as a second (role:variant) source rather than a separate rule. Precedex is the commercial name for dexmedetomidina (qt_vol_dex). set_sedativo_em_uso (RULE-SEDACAO-013) selects the drug. "Fentanill" spelling appears in both.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
