# RULE-OPERACIONAL-INFRA-021 — Offline endpoints hardcode empresa lookup to whitelabel='homecare'

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

All four offline sync views (DadosOfflineView, EvolucoesOfflineView, PrescricoesOfflineView, BalancoHidricoOfflineView) set request.empresa by looking up Empresa.objects.get(whitelabel='homecare') unconditionally - regardless of which company the authenticated user actually belongs to. This means these offline endpoints are effectively hardcoded to a single company (the one whose whitelabel field equals the literal string 'homecare').

## Outputs

| Name | Type | Unit |
|---|---|---|
| request.empresa | object | - |

## Logic

```text
setattr(request, "empresa", Empresa.objects.get(whitelabel="homecare"))
```

## Edge cases (as implemented)

Empresa.objects.get() will raise DoesNotExist (uncaught, -> 500) if no Empresa row has whitelabel='homecare', or MultipleObjectsReturned if more than one does. No scoping by request.user's own company membership occurs anywhere in these four views.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/dados_offline.py` | 67, 97, 182, 214 | `8166c07e` | primary |

- Merged from: RULE-offline-BE-05-004
- Related rules: RULE-OPERACIONAL-INFRA-022, RULE-OPERACIONAL-INFRA-023

## Notes

Flagged as a likely single-tenant hardcoding left over from a homecare-specific deployment/pilot, rather than a general multi-tenant offline-sync feature - a verifier should confirm whether this repo instance is in fact only ever deployed for a single homecare customer.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
