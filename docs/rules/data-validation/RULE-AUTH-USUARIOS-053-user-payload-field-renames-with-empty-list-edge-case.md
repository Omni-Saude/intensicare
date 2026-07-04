# RULE-AUTH-USUARIOS-053 — User payload field renames with empty-list edge case

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
UsuarioViewSet.manage_data renames incoming client fields for internal processing: 'setores' (list) -> 'setores_id'; 'foto_perfil' (string) -> 'foto_perfil_b64'; 'grupos_acessos' -> 'grupos_acessos_ids' but ONLY if truthy - an empty list [] for grupos_acessos is falsy in the check 'if data.get("grupos_acessos")', so it is never renamed/forwarded, meaning a client cannot use this endpoint to remove ALL of a user's access groups by sending an empty array.

## Inputs

| name | type |
|---|---|
| setores | array of uuid |
| foto_perfil | string (base64) |
| grupos_acessos | array of uuid |

## Outputs

| name | type |
|---|---|
| setores_id | array of uuid |
| foto_perfil_b64 | string |
| grupos_acessos_ids | array of uuid |

## Logic

```text
foto_perfil = data.pop("foto_perfil", None)
setores = data.pop("setores", None)
if isinstance(setores, list):
    data["setores_id"] = setores
if foto_perfil and isinstance(foto_perfil, str):
    data["foto_perfil_b64"] = foto_perfil
if data.get("grupos_acessos"):          # falsy for [] or None
    data["grupos_acessos_ids"] = data.pop("grupos_acessos", None)
```

## Edge cases (as implemented)

grupos_acessos=[] is silently dropped (never popped, never renamed) - it remains as an unrecognized 'grupos_acessos' key in the data dict, ignored by the serializer since only grupos_acessos_ids is a declared field. Contrast with setores=[] which DOES pass isinstance(list) and would be forwarded/synced.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/usuario.py` | 26-40 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-005`

**Related rules:**

- [RULE-AUTH-USUARIOS-036](RULE-AUTH-USUARIOS-036-grupoacesso-update-replaces-entire-usuarios-membership.md)

## Notes

Contrast with RULE-acesso-BE-05-005 where usuarios=[] DOES clear a GrupoAcesso's membership - here the equivalent operation on the Usuario side for grupos_acessos is unreachable via empty array.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
