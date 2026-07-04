# RULE-OPERACIONAL-INFRA-019 — Offline water balance shows the last 2 records for an occupied bed; a QTD attribute is defined but unused

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

BalancoHidricoOfflineSerializer.get_balanco_hidrico fetches only the 2 most recent (order_by('-dia')[:2]) BalancoHidrico (fluid balance) records for the bed, requiring leito__ocupado=True. A class attribute _QT_DIAS=5 is declared but never referenced anywhere in the method body - the actual limit is the hardcoded slice [:2], not _QT_DIAS.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| instance | Leito | - | leito__ocupado=True required |

## Outputs

| Name | Type | Unit |
|---|---|---|
| balanco_hidrico | object (day-string -> object) | - |

## Logic

```text
_QT_DIAS = 5   # declared, never used
payload = {}
for bh in BalancoHidrico.objects.prefetch_related("entradas","saidas","sinais_vitais").filter(
        leito=instance, nr_atendimento=instance.nr_atendimento, leito__ocupado=True
    ).order_by("-dia")[:2]:
    payload[str(bh.dia)] = BalancoHidricoCompletoSerializer(bh, context=context).data
return payload
```

## Edge cases (as implemented)

If the bed is currently unoccupied (leito__ocupado=False), the queryset returns nothing at all, even if historical balance records exist for a previous nr_atendimento.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/dados_offline.py` | 63-97 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-002

## Notes

The docstring ('Pegar os últimos 2 balanços hídricos') matches the actual [:2] slice, so behavior is internally consistent - the discrepancy is specifically the dead/unused _QT_DIAS=5 class attribute, which a verifier might mistake for the actual controlling parameter.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
