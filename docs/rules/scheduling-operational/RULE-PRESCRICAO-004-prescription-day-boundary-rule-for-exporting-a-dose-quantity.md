# RULE-PRESCRICAO-004 — Prescription day-boundary rule for exporting a dose quantity into fluid balance

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
When a nurse "exports" an administered dose's quantity into the fluid-balance (Entrada) ledger, the target balance-day is determined by a 07:00 shift boundary: if the export happens before 7 AM local time, the quantity is booked against the PREVIOUS calendar day's balance rather than the current one.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| current datetime (server local time) | datetime |  |  |
| instance.prescricao_continua.dia | date |  |  |
| qtd_exportada | number | mL (assumed) |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| Entrada record (tipo="outra_entrada") | object |  |

## Logic

```text
data = (
    instance.prescricao_continua.dia
    if datetime.now().astimezone().hour >= 7
    else instance.prescricao_continua.dia - timedelta(days=1)
)
balanco = BalancoHidrico.objects.filter(
    dia=data, nr_atendimento=instance.prescricao_continua.prescricao.NR_ATENDIMENTO,
).first()
nome = instance.prescricao_continua.prescricao.DS_ITEM_PRESCRITO
EntradaSerializer(data={
    "tipo": "outra_entrada", "nome": nome, "quantidade": qtd_exportada, "balanco": balanco.id,
}, context=self.context).save()
```

## Edge cases (as implemented)
Uses datetime.now().astimezone().hour (server/local time), not the encounter's or bed's timezone explicitly. If no matching BalancoHidrico row exists for the computed day, `balanco.id` will raise AttributeError (balanco would be None from .first()) — no explicit None-check before use.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 320-341 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-07-010

**Related rules:**

- RULE-PRESCRICAO-005
- RULE-PRESCRICAO-001
- RULE-PRESCRICAO-008

## Notes
The same 07:00 boundary concept recurs in RULE-prescricao-BE-07-015 (get_horarios' dia_real annotation in prescricao.py), applied there for a different purpose (display ordering rather than balance-day selection).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
