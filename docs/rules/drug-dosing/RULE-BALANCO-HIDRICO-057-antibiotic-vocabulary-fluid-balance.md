# RULE-BALANCO-HIDRICO-057 — Antibiotic vocabulary (fluid balance)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | drug-dosing |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Controlled list of antibiotics/antifungals/antivirals selectable as an intake.

## Inputs

- nome

## Outputs

- valid antibiotic

## Logic

```text
options include Daptomicina, Zitromax, Ceftazidina, Torgena, Ambisome, Amplacilina, Anforicin B,
Bactrim, Cancidas, Cipro, Dalacin, Ecalta, Flagyl, Garamicina, Invanz, Kefazol, Keflin, Klaricid,
Levaquin, Meronem, Mycamine, Staficilin N, Targocid, Tazocin, Tygacil, Unasyn, Vancocina, Zoltec,
Zovirax, Zyvox, Rocefin, Maxcef, Avalox, Linezolida, Aciclovir, Metronidazol, Fluconazol, Zerbaxa,
Cefuroxima Sódica, Novamin, Bedfordpoly B.
```

## Edge cases (as implemented)

Several entries carry trailing whitespace in value strings (e.g. "Bedfordpoly B ", "Vancocina ").

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published reference — facility-specific antimicrobial pick-list (antibiotics + antifungals + antivirals) for the intake form. ([source](n/a))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | volume mL only |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nome=Vancocina | vancomycin selectable | stored value 'Vancocina ' WITH trailing space; a trimmed client value 'Vancocina' would NOT equal the option value | no |
| nome=Aciclovir | antiviral, present despite 'antibiótico' label | accepted — list mixes antivirals/antifungals under an antibiotic label | yes |
| nome=Bedfordpoly B | polymyxin B (Bedford) | stored 'Bedfordpoly B ' with trailing whitespace | no |

**Verifier notes**

Proprietary formulary vocabulary (dataFormBalancoHidrico.ts:191-247), 40 options — do NOT treat as wrong.
Data-quality observations for internal review:
(1) Trailing-whitespace values: 'Bedfordpoly B ', 'Novamin ', 'Staficilin N ', 'Vancocina '. Since value===label
    including the space, any consumer that trims/normalizes fails equality matching (1st & 3rd vectors) — a real
    value-integrity risk for downstream filtering/reporting.
(2) Label 'antibiótico' but list includes antifungals (Cancidas, Mycamine, Ecalta, Ambisome, Anforicin B, Zoltec)
    and antivirals (Aciclovir, Zovirax) — mislabeled category (cosmetic).
(3) Brand/generic duplicates (Flagyl/Metronidazol; Zoltec/Fluconazol; Zovirax/Aciclovir).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormBalancoHidrico.ts` | 191-247 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fluidbalance-FE-01-011`

**Related rules:**

- [RULE-BALANCO-HIDRICO-056](RULE-BALANCO-HIDRICO-056-drugs-hydration-in-bi-vocabulary.md)
- [RULE-BALANCO-HIDRICO-058](RULE-BALANCO-HIDRICO-058-electrolyte-replacement-vocabulary.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
