# RULE-CADASTROS-UI-012 — Default required-field rule

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
Shared antd-style rule object marking a field mandatory with Portuguese error message "Este campo e obrigatorio!".

## Inputs

| name | type | unit | range |
|---|---|---|---|
| field value | any |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| valid | boolean |  |

## Logic

```text
defaultFormRules = [ { required: true, message: "Este campo é obrigatório!" } ]
// a value that is empty/undefined fails validation.
```

## Edge cases (as implemented)

Empty string / undefined fails; whitespace handling delegated to antd form engine (not in this file).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/defaultFormRules.ts` | 1-5 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-01-001`

**Related rules:**

- [RULE-CADASTROS-UI-011](RULE-CADASTROS-UI-011-formusuario-required-fields-only-enforced-in-modal-creation.md)

## Notes

Applied wherever `required:true` appears on a field across all forms.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
