# RULE-CADASTROS-UI-007 — Group-edit autosave guards partial "usuarios" updates

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
While editing an access group (Grupo), the form autosaves on every field change (onValuesChange), but the "usuarios" (member list) field is only forwarded to the parent submit handler when every entry in it is already a plain string ID; otherwise "usuarios" is omitted from that autosave call. On both the value-change autosave and the explicit name-tab submit, "cargo" is coerced to null whenever it is falsy.

## Inputs

| name | type |
|---|---|
| usuarios (form array value) | string[] \| object[] |
| cargo | string \| null \| undefined |

## Outputs

| name | type |
|---|---|
| submitToFather payload | Partial<Models.Grupo> |

## Logic

```text
onEditValues(_, { usuarios, ...values }):
  if usuarios && usuarios.every(item => typeof item === "string"):
    submitToFather({ ...values, cargo: values.cargo ? values.cargo : null, usuarios })
  else:
    submitToFather(values)     // usuarios omitted entirely from this autosave call
onEditName(values):     // explicit "Dados do grupo" tab submit
  submitToFather({ ...values, cargo: values.cargo ? values.cargo : null, usuarios: undefined })
onValuesChange is wired to onEditValues ONLY when editingName (the "disabled" prop) is true.
```

## Edge cases (as implemented)

onValuesChange is bound to onEditValues only while the `disabled`/editingName prop is true; when false, no autosave-on-change handler is attached at all (onValuesChange is undefined). Because the guard checks the freshly changed "usuarios" value's item types, a group manager component briefly holding full user objects (mid-selection) will have "usuarios" silently dropped from that particular autosave call instead of being submitted with objects.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormEditGrupo/FormEditGrupo.tsx` | 44-68,76-78 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-007`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
