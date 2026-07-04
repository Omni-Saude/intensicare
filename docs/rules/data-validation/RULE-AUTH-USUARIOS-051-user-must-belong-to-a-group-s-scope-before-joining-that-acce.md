# RULE-AUTH-USUARIOS-051 — User must belong to a group's scope before joining that access group

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
Adding a user to an access group requires the user already be a member of the group's empresa/estabelecimento/setor scope; otherwise validation fails.

## Inputs

| name | type |
|---|---|
| usuario | Usuario FK |
| grupo | GrupoAcesso FK |

## Outputs

| name | type |
|---|---|
| valid_membership | bool |

## Logic

```text
UsuarioGrupoAcesso unique_together(usuario, grupo).
save():
  if grupo.empresa and not grupo.empresa.usuarios.filter(pk=usuario_pk).exists():
      raise ValidationError({"usuario":"Usuário não pertence a está empresa"})
  if grupo.estabelecimento and not grupo.estabelecimento.usuarios.filter(pk=usuario_pk).exists():
      raise ValidationError({"usuario":"Usuário não pertence a este estabelecimento"})
  if grupo.setor and not grupo.setor.usuarios.filter(pk=usuario_pk).exists():
      raise ValidationError({"usuario":"Usuário não pertence a este setor"})
  super().save(*args, *kwargs)   # <-- BUG: *kwargs (positional) instead of **kwargs
```

## Edge cases (as implemented)

DISCREPANCY: line 38 calls super().save(*args, *kwargs) — the second splat is *kwargs (positional unpacking of a dict yields its keys), not **kwargs; passing keyword save args (e.g. force_insert) would break. Functions correctly only when called with no kwargs.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/usuario_grupo_acesso.py` | 18-38 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-034`

**Related rules:**

- [RULE-AUTH-USUARIOS-048](RULE-AUTH-USUARIOS-048-access-group-must-belong-to-exactly-one-scope-empresa-xor-es.md)

## Notes

Recorded verbatim per instructions; the *kwargs typo is a latent defect.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
