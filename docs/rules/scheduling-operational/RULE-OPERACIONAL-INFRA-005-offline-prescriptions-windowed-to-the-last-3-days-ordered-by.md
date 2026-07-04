# RULE-OPERACIONAL-INFRA-005 — Offline prescriptions windowed to the last 3 days, ordered by day then item-type priority

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

_get_prescricoes restricts PrescricaoContinua rows to those whose 'dia' is on or after (today - PrescricaoOfflineEnum.QTD_DIAS) - i.e. QTD_DIAS=2, giving an inclusive 3-day window (today, yesterday, day-before). Results are ordered by day descending, then by a computed 'prioridade' reflecting prescription item type: DIETA=1, MEDICAMENTO_SOLUÇÃO=2, SN_ACM=3, RECOMENDACAO_ENFERMAGEM=4, RECOMENDACAO=5 (any other DS_TIPO_ITEM_PRESCR value gets no case match, i.e. a NULL/None priority).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| prescricao.DS_TIPO_ITEM_PRESCR | string enum | - | - |
| dia | date | - | >= today - 2 days |

## Outputs

| Name | Type | Unit |
|---|---|---|
| prioridade | integer \| null | - |

## Logic

```text
QTD_DIAS = 2   # PrescricaoOfflineEnum.QTD_DIAS
qs = PrescricaoContinua.objects.filter(
    prescricao__NR_ATENDIMENTO__in=leitos.nr_atendimento,
    dia__gte=today() - timedelta(days=QTD_DIAS),
).annotate(
    prioridade=Case(
        When(prescricao__DS_TIPO_ITEM_PRESCR="DIETA", then=1),
        When(prescricao__DS_TIPO_ITEM_PRESCR="MEDICAMENTO_SOLUÇÃO", then=2),
        When(prescricao__DS_TIPO_ITEM_PRESCR="SN_ACM", then=3),
        When(prescricao__DS_TIPO_ITEM_PRESCR="RECOMENDACAO_ENFERMAGEM", then=4),
        When(prescricao__DS_TIPO_ITEM_PRESCR="RECOMENDACAO", then=5),
        output_field=IntegerField(),
    )
).order_by("-dia", "prioridade")
```

## Edge cases (as implemented)

dia__gte uses a closed lower bound with no upper bound - future-dated 'dia' values (if any exist) would also be included, not just past/present days. Item types outside the 5 named ones get a NULL 'prioridade', and NULLs sort per the database's NULL-ordering convention within the ascending 'prioridade' secondary sort (typically last in PostgreSQL ascending order).

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative clinical reference. The 3-day retention window (QTD_DIAS=2, inclusive) and the item-type priority ordering (DIETA=1, MEDICAMENTO_SOLUCAO=2, SN_ACM=3, RECOMENDACAO_ENFERMAGEM=4, RECOMENDACAO=5) are proprietary offline-sync display business rules. Only the window arithmetic and NULL-ordering are externally checkable (Python/Django date math; PostgreSQL default ASC NULLS LAST).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/dados_offline.py` | 144-172 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-007
- Related rules: RULE-OPERACIONAL-INFRA-003

## Notes

PrescricaoOfflineEnum.QTD_DIAS=2 is defined in core/enum.py, out of this partition's scope, but its value was confirmed by inspection and is required to reproduce this rule precisely.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
