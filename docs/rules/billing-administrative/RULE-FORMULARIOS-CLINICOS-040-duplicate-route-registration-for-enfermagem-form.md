# RULE-FORMULARIOS-CLINICOS-040 — Duplicate route registration for enfermagem form

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | formularios-clinicos |

## Rule
Two distinct URL path segments ('formulario-enfermagem' and 'formulario-enfermagem-novo') are registered against the exact same viewset (FormularioEnfermagemViewSet) using the identical DRF router basename ('formulario-enfermagem').

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| url path segment | string | null | 'formulario-enfermagem' \| 'formulario-enfermagem-novo' |

## Outputs

| Name | Type | Unit |
|---|---|---|
| routed viewset | viewset | null |

## Logic

```text
omni_router.register("formulario-enfermagem", FormularioEnfermagemViewSet, basename="formulario-enfermagem")
omni_router.register("formulario-enfermagem-novo", FormularioEnfermagemViewSet, basename="formulario-enfermagem")
# both map to the same viewset/basename
```

## Edge cases (as implemented)

Registering two prefixes under the same basename can cause DRF/Django reverse() name collisions (last registration for a name typically wins client-visible URL naming); functionally both paths serve identical behavior since the same viewset class is used.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/urls.py | 12-21 | 8166c07e | primary |

- Merged from: RULE-rotas-BE-08-001

## Notes

Likely an artifact of a frontend migration (old vs "novo" endpoint alias) rather than a deliberate versioning scheme; no behavioral difference is implemented between the two paths. Reassigned from auth-usuarios: a clinical-form (enfermagem) DRF routing artifact with no auth content.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
