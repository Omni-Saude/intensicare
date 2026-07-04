# RULE-PRESCRICAO-005 — 07:00 shift-boundary reordering of scheduled dose times for display

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
When listing all scheduled dose times for a continuous prescription, doses timed at or after 07:00 are grouped/sorted under their nominal prescription day, while doses timed before 07:00 are grouped/sorted under the FOLLOWING calendar day — reflecting a home-care "day" that begins at 07:00 rather than midnight.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario (scheduled time-of-day, "HH:MM") | string |  |  |
| prescricao_continua.dia | date |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| dia_real (annotated sort key) | date |  |
| ordered horarios list | list[object] |  |

## Logic

```text
.annotate(dia_real=Case(
    When(horario__gte="07:00", then=F("prescricao_continua__dia")),
    When(horario__lt="07:00", then=F("prescricao_continua__dia") + timedelta(days=1)),
    output_field=DateField(),
)).order_by("dia_real", "horario")
```

## Edge cases (as implemented)
String comparison ("07:00") on the "horario" field assumes a zero-padded 24h "HH:MM" format; boundary is inclusive at exactly "07:00" (>= keeps it on the nominal day).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/prescricao.py` | 153-175 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/prescricao.py` | 234-256 | `8166c07e` | duplicate |

**Merged from:**

- RULE-prescricao-BE-07-015

**Related rules:**

- RULE-PRESCRICAO-004

## Notes
Byte-identical duplicate in PrescricaoContinuaPdfSerializer.get_horarios, same file, lines 234-256. Conceptually consistent with the 07:00 boundary used for fluid-balance day selection in RULE-prescricao-BE-07-010 (horario_prescricao.py).  Second byte-identical copy in PrescricaoContinuaPdfSerializer.get_horarios (same file, lines 234-256), recorded as a duplicate source.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
