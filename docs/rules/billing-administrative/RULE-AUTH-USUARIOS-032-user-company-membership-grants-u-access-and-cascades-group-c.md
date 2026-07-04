# RULE-AUTH-USUARIOS-032 — User-company membership grants 'u' access and cascades group cleanup

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
Linking a user to a company adds the 'u' access code; unlinking removes that company's access-group memberships and drops 'u' when the user belongs to no company.

## Inputs

| name | type |
|---|---|
| usuario | Usuario FK |
| empresa | Empresa FK |

## Outputs

| name | type |
|---|---|
| usuario.acessos / group memberships | side-effect |

## Logic

```text
UsuarioEmpresa unique_together(usuario, empresa).
save(): if "u" not in usuario.acessos: append "u"; save usuario.
post_delete(UsuarioEmpresa):
  delete UsuarioGrupoAcesso where usuario=instance.usuario AND grupo.empresa=instance.empresa
  if not usuario.empresas.exists():
      usuario.acessos = [a for a in acessos if a != "u"]; save
```

## Edge cases (as implemented)

Cascade only removes empresa-scoped groups; establishment/sector groups handled by their own signals.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/usuario_empresa.py` | 19-38 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-031`

**Related rules:**

- [RULE-AUTH-USUARIOS-033](RULE-AUTH-USUARIOS-033-establishment-membership-auto-creates-company-membership-del.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
