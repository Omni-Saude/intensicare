# RULE-FORMULARIOS-CLINICOS-042 — Vasopressor / inotrope / sedative dosing capture (movimentacao)

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | validation |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | formularios-clinicos |

## Rule
Continuous vasoactive and sedative drugs recorded with bounded quantities; noradrenaline and sedatives in nullable ("anulavel") groups with start datetime and multi-entry list.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dobutamina | number | null | 0-30 |
| noradrenalina.quantidade | number | null | 0-200 |
| noradrenalina.horario_inicio | datetime | null | null |
| sedativos[].nome_sedativo | enum | null | fentanil\|midazolam\|propofol\|cetamina\|empty |
| sedativos[].quantidade | number | null | 0-30 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| drug entries | object | null |

## Logic

```text
dobutamina: number 0-30 (in "Gerais")
Noradrenalina group (anulavel): quantidade 0-200 + horario_inicio datetime
Sedativos group (anulavel): list; each row = nome_sedativo enum {fentanil,midazolam,propofol,cetamina,""} + quantidade 0-30
```

## Edge cases (as implemented)

Groups flagged anulavel=true may be nulled entirely (drug not in use). Units not specified in code (likely ml/h or mcg/kg/min).

## Verification

- Verdict: UNVERIFIABLE
- Reference: Critical-care continuous-infusion dose ranges (drug monographs / SCCM Surviving Sepsis Campaign; NHS critical-care formulary; ICU sedation references). Approximate adult ranges: DOBUTAMINE 2.5-10 mcg/kg/min, up to ~20 (rarely 40); NOREPINEPHRINE (noradrenalina) 0.01-3.3 mcg/kg/min, i.e. up to ~200 mcg/min in a 70 kg adult for refractory shock; PROPOFOL 5-50 mcg/kg/min (0.3-3 mg/kg/h); MIDAZOLAM 0.02-0.25 mg/kg/h; FENTANYL ~0.7-10 mcg/kg/h (commonly 25-200+ mcg/h); KETAMINE (cetamina) ~0.06-1.5 mg/kg/h for analgosedation. Crucially, the legacy form specifies NO UNIT for any of these numeric fields.


## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormMovimentacao.ts | 234-262,353-385 | f9656be2 | primary |

- Merged from: RULE-drug-FE-01-028

## Notes

Missing units is a reimplementation risk; noradrenaline 0-200 vs sedatives/dobutamine 0-30 imply different unit bases. Reassigned from prescricao: field-group of dataFormMovimentacao (a clinical progress/round form under dados_prontuario) capturing continuous infusion doses as documentation, not a prescription-administration workflow. verify=true: Phase-1 category is drug-dosing.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
