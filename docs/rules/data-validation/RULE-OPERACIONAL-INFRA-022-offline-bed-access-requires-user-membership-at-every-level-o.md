# RULE-OPERACIONAL-INFRA-022 — Offline bed access requires user membership at every level of the ownership chain

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

DadosOfflineView.get requires the requesting user to be linked simultaneously at every level: the patient (via usuarios_setores_pacientes), the sector (setor__usuarios), the establishment (setor__estabelecimento__usuarios), and the company (setor__estabelecimento__empresa__usuarios) - all four relationships must independently include the user for a bed to appear in the offline payload.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.user | object | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| leitos | queryset of Leito | - |

## Logic

```text
leitos = Leito.objects.filter(
    paciente__usuarios_setores_pacientes__usuario=request.user,
    setor__usuarios=usuario,
    setor__estabelecimento__usuarios=usuario,
    setor__estabelecimento__empresa__usuarios=usuario,
).order_by("paciente__nome")
```

## Edge cases (as implemented)

This is a stricter (AND-of-four) access rule than most other views in this partition, which typically only check setor__usuarios=user.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/dados_offline.py` | 69-80 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-005
- Related rules: RULE-OPERACIONAL-INFRA-023, RULE-OPERACIONAL-INFRA-021

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
