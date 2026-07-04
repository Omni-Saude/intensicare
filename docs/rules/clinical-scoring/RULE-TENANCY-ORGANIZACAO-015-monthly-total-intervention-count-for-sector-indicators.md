# RULE-TENANCY-ORGANIZACAO-015 — Monthly total intervention count for sector indicators

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
As part of the indicadores action, the sector's total count of AssistidoPor (audit) records created within the CURRENT calendar month (1st through last day, inclusive) is computed and appended as a fifth indicator, labeled with the month/year.

## Inputs

| Name | Type | Unit |
|---|---|---|
| current month/year | date |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total_intervencoes | integer |  |

## Logic

```text
month, year = timezone.now().month, timezone.now().year
num_days = calendar.monthrange(year, month)[1]
data_inicio = date(year, month, 1)         # first day of month
data_fim = date(year, month, num_days)     # last day of month
total_intervencoes = AssistidoPor.objects.filter(
    leito__setor=setor, criado_em__range=(data_inicio, data_fim)
).count()
indicadores.append({"nome": f"Total de intervenções ({month}/{year})", "valor": total_intervencoes})
```

## Edge cases (as implemented)
Django's __range filter is inclusive on both ends. The source code's inline comments are swapped/backwards (data_inicio's comment says 'último dia do mês' [last day] and data_fim's says 'primeiro dia do mês' [first day]) even though the actual date values assigned are correct (1st, then last day) - a verbatim comment/code mismatch, not a logic bug.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal/proprietary business logic: current-calendar-month count of AssistidoPor (audit/intervention) records for a sector, appended as a fifth indicator. Calendar-month boundary math (calendar.monthrange, first/last day) is standard library behavior, not a clinical guideline; the only checkable dimension is the date-range boundary correctness.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/setor.py` | 145-176 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-016`
- Related rules: RULE-TENANCY-ORGANIZACAO-038

## Notes
timezone.now() is used without .astimezone(), so month/year are computed in whatever timezone Django's USE_TZ setting resolves to (typically UTC) - not necessarily the user's local calendar month at midnight boundaries. | Reconciliation: this indicator is appended as a fifth entry inside the same indicadores action documented in setor-BE-05-015; kept as a separate rule because it is a structurally distinct formula (AssistidoPor monthly count) computed alongside, not part of, the per-trilha aggregation.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
