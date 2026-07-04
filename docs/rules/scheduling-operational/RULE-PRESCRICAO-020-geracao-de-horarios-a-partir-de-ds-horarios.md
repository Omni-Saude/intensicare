# RULE-PRESCRICAO-020 — Geracao de horarios a partir de DS_HORARIOS

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
When a continuous prescription is saved, medication administration time-slots are auto-generated from the prescription's DS_HORARIOS string (a "#"-delimited list of times), de-duplicated, formatted, and skipping slots that already exist.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| prescricao.DS_HORARIOS | string |  | #-delimited times |

## Outputs

| Name | Type | Unit |
|---|---|---|
| HorariosPrescricao rows | list |  |

## Logic

```text
super().save(...)
if prescricao.DS_HORARIOS:
    payload = [
        HorariosPrescricao(horario=format_horario(h), prescricao_continua_id=str(pk), horario_original=format_horario(h))
        for h in set(prescricao.DS_HORARIOS.split("#"))
        if h and (h not in self.horarios.values_list("horario", flat=True) if self.horarios else True)
    ]
    HorariosPrescricao.objects.bulk_create(payload)
```

## Edge cases (as implemented)
Empty-string tokens skipped. set() de-duplicates times. Dedup check compares the RAW token h against already-stored (format_horario'd) horario values, so formatting mismatches could allow duplicates. Runs inside transaction.atomic.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/prescricao_continua.py` | 32-52 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-06-001

**Related rules:**

- RULE-PRESCRICAO-032
- RULE-PRESCRICAO-010

## Notes
format_horario in utils.handlers (out of partition) defines the time-normalization.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
