# RULE-AUTH-USUARIOS-001 — GrupoAcesso permission catalog payload computation

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
get_permissoes builds a full permission-codename dict from the system's permission catalog (PermissionsChoices), defaulting every entry to False, then flips to True only permissions that are both assigned to the underlying Django group and present in the recognized system catalog.

## Inputs

| name | type |
|---|---|
| instance.grupo.permissions | queryset of Permission |

## Outputs

| name | type |
|---|---|
| permissoes | object (codename->bool) |

## Logic

```text
all_permissions = PermissionsChoices.permissions()   # list of (codename, label)
all_codenames = [p[0] for p in all_permissions]
payload = {codename: False for codename in all_codenames}
for perm in instance.grupo.permissions.all():
    if perm.codename in all_codenames:
        payload[perm.codename] = True
return payload
```

## Edge cases (as implemented)

Permissions assigned to the Django group that are NOT in PermissionsChoices.permissions() are silently ignored/omitted from the output entirely (neither True nor False key present).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published/clinical reference exists. Proprietary internal RBAC rule (Django Permission catalog -> codename->bool payload construction in GrupoAcessoSerializer.get_permissoes). Not a clinical calculation, guideline, or standard calculator. ([source](n/a))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a (no numeric coefficients; dict-construction logic only) |
| units | n/a (no physical units; codename strings and booleans) |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a (no score bands) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| system_catalog=["can_manage_usuario", "can_view_ocupacoes"]; group_permissions=["can_manage_usuario"] | n/a (no external reference); source-faithful expectation: {can_manage_usuario: true, can_view_ocupacoes: false} | {can_manage_usuario: true, can_view_ocupacoes: false} — payload seeded all-False then can_manage_usuario flipped True | yes |
| system_catalog=["can_manage_usuario", "can_view_ocupacoes"]; group_permissions=[] | n/a; source-faithful: {can_manage_usuario: false, can_view_ocupacoes: false} | {can_manage_usuario: false, can_view_ocupacoes: false} — all defaults retained | yes |
| system_catalog=["can_manage_usuario"]; group_permissions=["can_manage_usuario", "add_logentry"] | n/a; source-faithful edge case: {can_manage_usuario: true} — add_logentry silently omitted (not in system catalog) | {can_manage_usuario: true}; add_logentry produces NO key because 'if perm.codename in all_codename_permissions' fails at source line 101 | yes |

**Verifier notes**

Catalog logic verified byte-faithful against legacy source core/api/v1/serializers/grupo_acesso.py lines 95-103 (commit 8166c07). Behavior: payload = {codename: False for every system codename}; iterate the Django group's permissions; flip to True only when perm.codename is in the recognized system catalog (PermissionsChoices.permissions()). Group perms outside the catalog are silently dropped (documented edge case, confirmed at source line 101). No authoritative published reference exists for an internal Django RBAC payload builder; flagged for internal review, NOT treated as wrong. Extraction status was OK; nothing contradicts the source.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/grupo_acesso.py` | 95-103 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-05-003`

**Related rules:**

- [RULE-AUTH-USUARIOS-035](RULE-AUTH-USUARIOS-035-grupoacesso-update-replaces-entire-permission-set.md)
- [RULE-AUTH-USUARIOS-037](RULE-AUTH-USUARIOS-037-full-permission-catalog-exposure.md)
- [RULE-AUTH-USUARIOS-058](../access-control/RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

verify=true because Phase-1 type is 'formula' per audit criteria (non-clinical RBAC payload construction, not a clinical calculation).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
