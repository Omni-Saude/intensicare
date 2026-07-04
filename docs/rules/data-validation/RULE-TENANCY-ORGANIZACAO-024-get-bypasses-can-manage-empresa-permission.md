# RULE-TENANCY-ORGANIZACAO-024 — GET bypasses can_manage_empresa permission

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
EmpresaViewSet declares permission_trilhas=('can_manage_empresa',) with exceto_metodo='GET', so only mutating requests require this permission.

## Inputs

| Name | Type | Unit |
|---|---|---|
| request.method | string |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| permission_required | boolean |  |

## Logic

```text
escopo = "empresa"
permission_trilhas = ("can_manage_empresa",)
exceto_metodo = "GET"
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/empresa.py` | 30-32 | `8166c07e` | primary |

- Merged from: `RULE-empresa-BE-05-003`

## Notes
Enforcement mechanism (TrilhasPermissaoMixin) is out of this partition's scope; configuration values recorded as observed.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
