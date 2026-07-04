# RULE-BALANCO-HIDRICO-058 — Electrolyte replacement vocabulary

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | drug-dosing |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | none |

## Rule
Controlled list of electrolytes for a replacement intake.

## Inputs

- nome

## Outputs

- valid electrolyte

## Logic

```text
options = { Sódio (Na+), Potássio (K+), Cloreto (Cl-), Cálcio (Ca2+), Magnésio (Mg2+),
            Bicarbonato (HCO3-), Fosfato (PO42-), Sulfato (SO42-) }
```

## Edge cases (as implemented)

Volume in ml only.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** none
- **Reference:** Ion valence/charge notation is chemically verifiable. Standard inorganic chemistry: orthophosphate PO4^3− (charge 3−); hydrogen phosphate HPO4^2−; sulfate SO4^2−; bicarbonate HCO3−; Na+, K+, Cl−, Ca2+, Mg2+. ([source](https://pubchem.ncbi.nlm.nih.gov/compound/Phosphate))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a (vocabulary) |
| coefficients | n/a |
| units | volume mL only (no mEq/mmol dose) |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nome=Sulfato (SO42-) | SO4^2− (charge 2−) | label 'SO42-' = SO4^2− — correct | yes |
| nome=Fosfato (PO42-) | orthophosphate PO4^3− (charge 3−) | label 'PO42-' reads as PO4^2− — chemically incorrect for orthophosphate | no |
| nome=Bicarbonato (HCO3-) | HCO3− (charge 1−) | label 'HCO3-' correct | yes |

**Verifier notes**

Proprietary electrolyte pick-list (dataFormBalancoHidrico.ts:248-271), 8 options, volume-only capture — do NOT
treat as wrong. One chemically-verifiable observation: the phosphate label 'Fosfato (PO42-)' renders the charge as
2− whereas orthophosphate is PO4^3−; sulfate 'SO42-' (2−) and all other ions are correct. This is a DISPLAY-LABEL
notation error only — the field captures a volume in mL, no valence/dose math is performed on the label — so
clinical impact is none. Flagged for internal review as a cosmetic data-quality fix.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormBalancoHidrico.ts` | 248-271 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fluidbalance-FE-01-012`

**Related rules:**

- [RULE-BALANCO-HIDRICO-056](RULE-BALANCO-HIDRICO-056-drugs-hydration-in-bi-vocabulary.md)
- [RULE-BALANCO-HIDRICO-057](RULE-BALANCO-HIDRICO-057-antibiotic-vocabulary-fluid-balance.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
