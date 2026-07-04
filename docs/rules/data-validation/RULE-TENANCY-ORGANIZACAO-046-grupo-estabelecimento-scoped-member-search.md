# RULE-TENANCY-ORGANIZACAO-046 — Grupo/estabelecimento-scoped member search

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
The autocomplete searches used to add sectors or users to an access "grupo" (permission group) scope their server-side results to the target grupo id (sectors are additionally scoped to the target estabelecimento), so only sectors/users eligible for that group/establishment are offered as candidates.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| idEmpresa | string (id) |  |  |
| idEstabelecimento | string (id) |  |  |
| grupo | string (id) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| searchResults | array of {label, value} |  |

## Logic
```text
// sectors:
getSetores(idEmpresa, idEstabelecimento)({ grupo })
// users:
getAllUsuariosByGroup(idEmpresa, grupo)()
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/SetoresGrupoManager/SetoresGrupoManager.tsx | 42-51 | f9656be2 | primary |

- Merged from: RULE-grupo-FE-06-029
- Related rules: RULE-TENANCY-ORGANIZACAO-045

## Notes
Mirrored in src/components/UsuariosGrupoManager/UsuariosGrupoManager.tsx (lines 45-53) for the user-search variant. Actual filter enforcement happens server-side (out of scope); this rule documents the client query parameters sent.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
