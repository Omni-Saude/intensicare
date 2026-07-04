# RULE-AUTH-USUARIOS-034 — Sector membership auto-creates establishment membership; delete cleans groups

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
Assigning a user to a sector auto-creates the parent establishment membership; removing it deletes that sector's group memberships.

## Inputs

| name | type |
|---|---|
| usuario | Usuario FK |
| setor | Setor FK |

## Outputs

| name | type |
|---|---|
| UsuarioEstabelecimento / group memberships | side-effect |

## Logic

```text
UsuarioSetor unique_together(usuario, setor).
@transaction.atomic save():
  if not UsuarioEstabelecimento.exists(usuario, setor.estabelecimento):
      create UsuarioEstabelecimento(usuario, setor.estabelecimento).save()
  super().save()
post_delete: delete UsuarioGrupoAcesso where usuario=... AND grupo.setor=instance.setor
```

## Edge cases (as implemented)

Chains upward: sector -> establishment (RULE-032) -> company (RULE-031).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/usuario_setor.py` | 20-39 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-033`

**Related rules:**

- [RULE-AUTH-USUARIOS-033](RULE-AUTH-USUARIOS-033-establishment-membership-auto-creates-company-membership-del.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
