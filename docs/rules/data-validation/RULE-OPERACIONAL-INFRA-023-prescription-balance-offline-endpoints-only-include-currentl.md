# RULE-OPERACIONAL-INFRA-023 — Prescription/balance offline endpoints only include currently-occupied homecare beds

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Both PrescricoesOfflineView.get and BalancoHidricoOfflineView.get restrict the candidate leitos to ocupado=True AND tipo='homecare' (in addition to the user-link filter), before building their respective offline payloads.

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
    paciente__usuarios_setores_pacientes__usuario=request.user, ocupado=True, tipo="homecare")
```

## Edge cases (as implemented)

Unlike DadosOfflineView (RULE-offline-BE-05-005), this filter does NOT require setor/estabelecimento/empresa user-membership - only the patient-link (usuarios_setores_pacientes) and the ocupado+tipo constraints.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/dados_offline.py` | 181-189, 213-221 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-008
- Related rules: RULE-OPERACIONAL-INFRA-022, RULE-OPERACIONAL-INFRA-021

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
