# RULE-OPERACIONAL-INFRA-003 — Offline prescriptions grouped by day, keyed by patient atendimento number

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

PrescricoesOfflineSerializer.get_prescricoes looks up the bed's prescriptions from a context-supplied dict (keyed by nr_atendimento, pre-filtered/pre-windowed by the view - see RULE-offline-BE-05-007) and groups them by calendar day (obj.dia) into a payload dict keyed by day-string.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| context.prescricoes[instance.nr_atendimento] | array of PrescricaoContinua | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| prescricoes | object (day-string -> array) | - |

## Logic

```text
prescricoes = context.get("prescricoes", {}).get(instance.nr_atendimento, [])
payload = {}
for dia, objs in groupby(prescricoes, key=lambda o: str(o.dia)):
    payload[dia] = PrescricaoContinuaOfflineSerializer(list(objs), many=True, context=context).data
return payload
```

## Edge cases (as implemented)

Like RULE-reacao-BE-05-003, this uses itertools.groupby which only merges CONSECUTIVE same-key items - correctness depends on the upstream queryset already being ordered by 'dia' (confirmed in RULE-offline-BE-05-007: the source queryset IS ordered by '-dia' first, so this usage is safe, unlike the reacao case).

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative clinical reference. This is offline-sync data-shaping (group prescriptions by calendar day). The only external correctness contract is Python's itertools.groupby semantics: it groups only CONSECUTIVE equal keys, so input must be pre-sorted by the grouping key.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/dados_offline.py` | 31-60 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-001
- Related rules: RULE-OPERACIONAL-INFRA-005

## Notes

Docstring claims 'últimos 3 dias' (last 3 days) - this matches the view-side window of today minus PrescricaoOfflineEnum.QTD_DIAS=2 days inclusive (RULE-offline-BE-05-007), confirmed consistent, not a discrepancy.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
