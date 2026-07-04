# RULE-AUTH-USUARIOS-033 — Establishment membership auto-creates company membership; delete cleans groups

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | billing-administrative |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Assigning a user to an establishment auto-creates the parent company membership; removing it deletes that establishment's group memberships.

## Inputs

| name | type |
|---|---|
| usuario | Usuario FK |
| estabelecimento | Estabelecimento FK |

## Outputs

| name | type |
|---|---|
| UsuarioEmpresa / group memberships | side-effect |

## Logic

```text
UsuarioEstabelecimento unique_together(usuario, estabelecimento).
save(): if not UsuarioEmpresa.exists(usuario, estabelecimento.empresa):
           create UsuarioEmpresa(usuario, estabelecimento.empresa).save()
        super().save()
post_delete: delete UsuarioGrupoAcesso where usuario=... AND grupo.estabelecimento=instance.estabelecimento
```

## Edge cases (as implemented)

Creating UsuarioEmpresa here transitively triggers RULE-031 ('u' grant).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/usuario_estabelecimento.py` | 20-40 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-032`

**Related rules:**

- [RULE-AUTH-USUARIOS-032](RULE-AUTH-USUARIOS-032-user-company-membership-grants-u-access-and-cascades-group-c.md)
- [RULE-AUTH-USUARIOS-034](RULE-AUTH-USUARIOS-034-sector-membership-auto-creates-establishment-membership-dele.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
