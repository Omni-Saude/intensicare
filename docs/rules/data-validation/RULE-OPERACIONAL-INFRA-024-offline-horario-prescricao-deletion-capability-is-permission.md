# RULE-OPERACIONAL-INFRA-024 — Offline horario-prescricao deletion capability is permission-gated

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

PrescricoesOfflineView exposes a 'can_delete_horario' context flag to the serializer, computed from whether the user's company-level permission set includes 'can_delete_horario_prescricao'.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.user | object | - | - |
| request.empresa | object | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| can_delete_horario | boolean | - |

## Logic

```text
return "can_delete_horario_prescricao" in get_permissoes_empresa(usuario, empresa)
```

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/dados_offline.py` | 174-179 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-009

## Notes

get_permissoes_empresa implementation lives in core/utils, out of this partition's scope.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
