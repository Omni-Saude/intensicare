# RULE-CADASTROS-UI-003 — Delete-professional action gated on edit mode + permission

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The "Excluir usuario" delete action for a professional's own data page is only rendered when the page is in editing mode AND the current user holds the can_manage_usuario permission.

## Inputs

| name | type |
|---|---|
| editing | boolean |
| can_manage_usuario | boolean |

## Outputs

| name | type |
|---|---|
| AlertDelete visibility | boolean |

## Logic

```text
render AlertDelete(idSelecionado=id_profissional, onDelete=_deleteUsuario) if (editing && can_manage_usuario)
```

## Edge cases (as implemented)

On confirmed delete, the flow calls deleteUsuario then redirects to /empresa/{id_empresa}/configuracoes/profissionais regardless of which professional's page it was invoked from.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/DadosProfissionalContent/DadosProfissionalContent.tsx` | 42,67-84,151-160 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-009`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
