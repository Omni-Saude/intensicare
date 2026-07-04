# RULE-BALANCO-HIDRICO-004 — Balanco Hidrico diurno (day-shift balance 07:00-19:00)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Day-shift fluid balance = (intake - output) for entries/outputs created between 07:00 and 19:00 local time on the balance day.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| entradas.quantidade in [07:00,19:00], deletado_em null | — | mL | — |
| saidas.quantidade in [07:00,19:00], deletado_em null | — | mL | — |
| self.dia | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| balanco_diurno | — | mL |

## Logic
```text
dia = strptime(self.dia,"%Y-%m-%d").date() if isinstance(self.dia, str) else self.dia
horario_inicio = datetime.combine(dia, time(7,0,0)).astimezone()
horario_fim    = datetime.combine(dia, time(19,0,0)).astimezone()
entradas_qs = entradas.filter(criado_em__range=[inicio,fim], deletado_em__isnull=True)
saidas_qs   = saidas.filter(criado_em__range=[inicio,fim], deletado_em__isnull=True)
entradas = Sum(entradas_qs.quantidade) if exists else 0
saidas   = Sum(saidas_qs.quantidade)   if exists else 0
return entradas - saidas
```

## Edge cases (as implemented)
Day shift is defined as 07:00-19:00 inclusive range (__range is inclusive on both ends) in the server's local timezone via .astimezone(). Overlap boundary 19:00 counts as diurno (and would double-count with noturno if noturno were also range-based, but noturno is derived by subtraction - see RULE-balanco-BE-06-005).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference defines a fluid-balance 'day shift' as 07:00-19:00. Nursing 12h day/night shift boundaries (and the 07:00-07:00 nursing day) are institutional scheduling conventions that vary by facility, not validated clinical cutoffs (contrast Sepsis-3, KDIGO, ASPEN). The underlying arithmetic (intake - output within a window) is the ADQI/Malbrain standard. (https://pmc.ncbi.nlm.nih.gov/articles/PMC10133509/)
- Test vectors: 3/3 match
- The (intake - output) arithmetic within a time window is standard and correct; the specific
definition of the day shift as 07:00-19:00 is a hard-coded institutional/nursing convention with no
authoritative published source to verify against - flagged for internal review, NOT treated as wrong.
Boundary note (verified against source): criado_em__range is inclusive on BOTH ends, so an entry at
exactly 19:00:00 counts as day shift; combined with noturno-by-subtraction (RULE-005) this does not
double-count. Uses server local tz via .astimezone() with no explicit zone, so results depend on the
deployment timezone - an operational consideration, not a reference discrepancy. Confirmed at
balanco.py:87-117.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/balanco_hidrico/balanco.py | 87-117 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-004
- Related rules: RULE-BALANCO-HIDRICO-005, RULE-BALANCO-HIDRICO-006

## Notes
Shift window hardcoded 07:00-19:00.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
