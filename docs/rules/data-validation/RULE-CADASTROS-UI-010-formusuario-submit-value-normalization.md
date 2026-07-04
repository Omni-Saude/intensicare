# RULE-CADASTROS-UI-010 — FormUsuario submit-value normalization

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Before calling the parent onFinish handler, the user form trims the name, trims+lowercases the username, reduces the profile photo to its base64 payload only if present, strips the CPF mask, and only forwards the "setores" (sector access) field when the current user has the can_manage_usuario permission.

## Inputs

| name |
|---|
| values.nome, values.username, values.foto_perfil, values.cpf, values.setores |

## Outputs

| name | type |
|---|---|
| normalized submit payload | Models.Usuario |

## Logic

```text
submitToFather({
  ...values,
  nome: values.nome ? values.nome.trim() : undefined,
  setores: (can_manage_usuario && values.setores) ? values.setores : undefined,
  username: values.username ? values.username.trim().toLocaleLowerCase() : undefined,
  foto_perfil: (values.foto_perfil && values.foto_perfil.b64) ? values.foto_perfil.b64 : undefined,
  cpf: values.cpf ? unformat(values.cpf) : values.cpf,
})
```

## Edge cases (as implemented)

If can_manage_usuario is false, "setores" is dropped from the submit payload entirely (set to undefined) even if the field held a value in the form - effectively read-only enforcement of sector assignment client-side for users without the manage permission.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormUsuario/FormUsuario.tsx` | 49-67 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-004`

**Related rules:**

- [RULE-CADASTROS-UI-009](RULE-CADASTROS-UI-009-cpf-input-mask-and-unformatting.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
