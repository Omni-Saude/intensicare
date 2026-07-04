# RULE-CADASTROS-UI-009 — CPF input mask and unformatting

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
Wherever a CPF (Brazilian taxpayer ID) is captured - the user filter and the user registration form - input is masked as 000.000.000-00 for display/entry, then the mask punctuation is stripped (unformat) before the value is sent to the filter/submit handler.

## Inputs

| name | type | range |
|---|---|---|
| cpf (masked) | string | mask 000.000.000-00 |

## Outputs

| name | type |
|---|---|
| cpf (unformatted digits) | string |

## Logic

```text
MaskedInput(mask="000.000.000-00")
on submit/filter: cpf = values.cpf ? unformat(values.cpf) : values.cpf
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FilterUsuarios/FilterUsuarios.tsx` | 20-27,41-47 | `f9656be266` | primary |
| trilhas-frontend | `src/components/FormUsuario/FormUsuario.tsx` | 124-140 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-001`

**Related rules:**

- [RULE-CADASTROS-UI-005](RULE-CADASTROS-UI-005-new-user-password-auto-filled-from-cpf.md)
- [RULE-CADASTROS-UI-010](RULE-CADASTROS-UI-010-formusuario-submit-value-normalization.md)

## Notes

Same mask + unformat pattern also appears in FormUsuario.tsx (lines 124-140) for the professional's own CPF field.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
