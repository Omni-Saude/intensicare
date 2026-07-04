# RULE-AUTH-USUARIOS-048 — Access group must belong to exactly one scope (empresa XOR estabelecimento XOR setor)

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A GrupoAcesso must be attached to exactly one of empresa, estabelecimento, or setor; its backing Django Group name is generated and must be unique.

## Inputs

| name | type |
|---|---|
| empresa | FK\|null |
| estabelecimento | FK\|null |
| setor | FK\|null |
| nome | string |

## Outputs

| name | type |
|---|---|
| grupo (Django Group) | Group |

## Logic

```text
three_xor(bool(empresa), bool(estabelecimento), bool(setor)) must be True, where
  three_xor(a,b,c) = (not a and (b ^ c)) or (a and not (b or c))  # exactly one truthy
else raise ValidationError({"data":"Inconsistência de dados!"}).
group_name = generate_group_name(pk_of_scope_model, nome) = "%s-%s" % (nome, pk)
  where pk_of_scope_model = the .get_pk of whichever of empresa/estabelecimento/setor is set.
if (not self.exists) and Group.objects.filter(name=group_name).exists():
    raise ValidationError({"nome":"Já existe outro grupo de acesso com este nome."})
if grupo_id is None: create Group(name=group_name) else rename existing grupo.
delete() always calls super().delete(force_delete=True).
```

## Edge cases (as implemented)

Uniqueness check only runs on create (not self.exists). Group name collision uses the composed "nome-pk" string, so uniqueness is scoped by the foreign object's pk.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/grupo_acesso.py` | 108-138 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-012`

**Related rules:**

- [RULE-AUTH-USUARIOS-010](RULE-AUTH-USUARIOS-010-grupoacesso-hierarchical-scope-resolution.md)
- [RULE-AUTH-USUARIOS-051](RULE-AUTH-USUARIOS-051-user-must-belong-to-a-group-s-scope-before-joining-that-acce.md)

## Notes

three_xor defined in core/utils.py:145 (out of partition). Also declares an (unused-by-Django) UniqueTogether helper listing (empresa,nome)/(estabelecimento,nome)/(setor,nome).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
