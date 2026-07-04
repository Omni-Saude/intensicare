# RULE-OPERACIONAL-INFRA-004 — Continuous prescription 'real day' rolls over at 07:00 (shift boundary)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

For offline prescription schedule display, each scheduled administration time (horario) is bucketed into a 'dia_real' (real/effective day): times at or after 07:00 belong to the prescription's own recorded day; times before 07:00 belong to the NEXT calendar day (the prescription day + 1). This reflects a clinical shift boundary at 07:00.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario | time | - | - |
| prescricao_continua.dia | date | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| dia_real | date | - |

## Logic

```text
dia_real = Case(
    When(horario__gte="07:00", then=F("prescricao_continua__dia")),
    When(horario__lt="07:00", then=F("prescricao_continua__dia") + timedelta(days=1)),
    output_field=DateField(),
)
# ordered by (dia_real, horario)
```

## Edge cases (as implemented)

Boundary is inclusive on the >=07:00 side (exactly 07:00:00 stays on the same day); exactly one tick before is the < branch, rolling to the next day.

## Verification

- Verdict: UNVERIFIABLE
- Reference: No universal published standard fixes the shift boundary at 07:00. A ~07:00 day-shift change is a common Brazilian/institutional nursing-shift convention, but the specific cutoff is a proprietary operational business rule. Only the Django Case/When boundary logic (inclusive at 07:00) is externally checkable.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/dados_offline.py` | 118-142 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-006
- Related rules: RULE-OPERACIONAL-INFRA-034, RULE-OPERACIONAL-INFRA-035

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
