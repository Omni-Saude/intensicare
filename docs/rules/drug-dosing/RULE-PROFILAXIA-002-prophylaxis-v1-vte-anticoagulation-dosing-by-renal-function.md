# RULE-PROFILAXIA-002 — Prophylaxis v1 - VTE anticoagulation dosing by renal function and BMI

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | profilaxia |

## Rule
Pharmacologic VTE (venous thromboembolism) prophylaxis dosing surfaced by profilaxia v1 criterio_4 (high VTE risk) and criterio_5 (formal indication without prophylaxis).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| creatinina | float | mg/dl | — |
| TRS (renal replacement therapy) | bool | — | — |
| IMC (BMI) | float | kg/m2 | — |

## Outputs

| Name | Type | Unit |
|---|---|---|
| anticoagulant regimen | string | — |

## Logic

```text
criterio_4 (alto risco TEV): enoxaparina 40 mg 1x/dia;
  IF creatinina > 2.0 OR paciente em TRS -> heparina 5000 U 8/8h;
  IF IMC > 40 -> enoxaparina 60 mg 1x/dia.
criterio_5 (indicacao formal sem profilaxia): enoxaparina 40 mg 1x/dia;
  IF creatinina > 2.0 OR TRS -> heparina 5000 U 12/12h.
```

## Edge cases (as implemented)
Creatinine cutoff strictly > 2.0 mg/dl. BMI cutoff strictly > 40 kg/m2. INTERNAL INCONSISTENCY (recorded verbatim, NOT reconciled): for the same renal condition (creatinina > 2.0 or TRS) the heparin frequency differs between the two criteria - criterio_4 prescribes heparina 5000 U 8/8h while criterio_5 prescribes heparina 5000 U 12/12h. These are two distinct clinical indications in source, so the difference may be intentional; kept exactly as written.

## Verification
- Verdict: VERIFIED, impact: none
- Reference: ACCP/CHEST Antithrombotic Therapy for VTE Prophylaxis and ASH 2018 Guidelines for VTE prophylaxis in hospitalized medical patients: enoxaparin 40 mg SC once daily standard prophylaxis; unfractionated heparin (UFH) 5000 U SC q8h or q12h accepted for severe renal impairment (CrCl <30 mL/min, where LMWH is avoided/UFH preferred); increased/weight-adjusted LMWH dosing for morbid obesity (BMI >= 40).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_profilaxia.py` | 23-36 | `8166c07e` | primary |

- Merged from: RULE-profilaxia-BE-01-005
- Related rules: RULE-PROFILAXIA-001, RULE-PROFILAXIA-003, RULE-PROFILAXIA-007

## Notes
Status kept OK per Phase 1 - the 8/8h vs 12/12h difference is an intra-rule difference between two separate criteria (criterio_4 vs criterio_5), not a cross-implementation copy divergence, so it is not a reconciliation DISCREPANCY. v1-only: criteria 4/5 are commented out of the v3 pathway (RULE-PROFILAXIA-008), so there is no v3 counterpart.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
