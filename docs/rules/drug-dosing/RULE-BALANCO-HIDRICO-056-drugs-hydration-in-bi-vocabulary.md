# RULE-BALANCO-HIDRICO-056 — Drugs/hydration-in-BI vocabulary

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
Controlled list of continuous-infusion (BI/bomba de infusao) drugs and hydration selectable for an intake record.

## Inputs

- nome

## Outputs

- valid drug

## Logic

```text
options include: Sedação, Thiopental, Adrenalina, Heparina, Clanidina, Octeotride, Lidocaina,
Dimorf, Hidrocortizona, Propofol, Cisatracúrio, Insulina, Noradrenalina, Dobutamina, Amiodarona,
Milrinona, Dopamina, Nipride, Cetamina, Dormonid, Fentanil, Precedex, Ketamin, Encrise, Tridil,
Hidratação Venosa, Rocurônio, Sulfentanila, Remifentanila (32 options).
```

## Edge cases (as implemented)

Includes some spelling variants/brand names (Clanidina, Hidrocortizona, Ketamin vs Cetamina).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published reference — facility-specific formulary pick-list of continuous-infusion (BI/bomba de infusão) drugs + hydration for the intake form. No guideline dictates which agents appear on a given ICU's continuous-infusion menu. ([source](n/a))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a (vocabulary, no computation) |
| coefficients | n/a |
| units | volume mL only; no dose/rate/concentration captured (cannot represent mcg/kg/min infusions — by design) |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nome=Noradrenalina | valid member of facility BI list | accepted (present in options) | yes |
| nome=Clanidina | intended = Clonidina (spelling variant) | stored verbatim as 'Clanidina' | yes |
| nome=ketamine | single agent | TWO options 'Cetamina' and 'Ketamin' both present — duplicate for same drug | yes |

**Verifier notes**

Proprietary facility formulary vocabulary (dataFormBalancoHidrico.ts:146-190) — do NOT treat as wrong.
Data-quality observations for internal review (not reference discrepancies):
(1) Legacy source array has 29 options, but the catalog entry claims "32 options" — catalog metadata count is
    off by 3 (verified by direct count of the options array).
(2) Orthography variants vs standard INN/PT-BR: 'Clanidina'->Clonidina, 'Hidrocortizona'->Hidrocortisona,
    'Octeotride'->Octreotide.
(3) Same drug listed twice under different spellings: 'Cetamina' and 'Ketamin' (both ketamine).
(4) Volume-only capture (mL), no dose/rate — expected for a fluid-balance form.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormBalancoHidrico.ts` | 146-190 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fluidbalance-FE-01-010`

**Related rules:**

- [RULE-BALANCO-HIDRICO-029](../care-pathway/RULE-BALANCO-HIDRICO-029-fluid-balance-intake-type-decision-tree.md)
- [RULE-BALANCO-HIDRICO-057](RULE-BALANCO-HIDRICO-057-antibiotic-vocabulary-fluid-balance.md)
- [RULE-BALANCO-HIDRICO-058](RULE-BALANCO-HIDRICO-058-electrolyte-replacement-vocabulary.md)

## Notes

Only volume (ml) captured, no dose/rate.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
