# RULE-CADASTROS-UI-005 — New-user password auto-filled from CPF

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
In the user registration/edit form, while creating a brand-new user (no initialValues supplied at all), typing into the CPF field also writes the unformatted CPF digits into the password field as its value.

## Inputs

| name | type |
|---|---|
| cpf (masked input onChange target value) | string |
| rawValues (initialValues prop) | Models.Usuario |

## Outputs

| name | type |
|---|---|
| form field "password" | string |

## Logic

```text
MaskedInput("cpf").onChange(e):
  if Object.entries(rawValues).length === 0:     // true only for a new/blank user
    form.setFieldsValue({ password: unformat(e.target.value) })
```

## Edge cases (as implemented)

The guard checks rawValues (the original initialValues prop), not the current live form state, so it only ever fires for genuinely new users; once any initialValues are supplied (editing an existing user) this auto-fill never triggers, even if the CPF field is changed.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormUsuario/FormUsuario.tsx` | 126-139 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-002`

**Related rules:**

- [RULE-CADASTROS-UI-006](RULE-CADASTROS-UI-006-hardcoded-default-signature-pin-for-all-users.md)
- [RULE-CADASTROS-UI-009](RULE-CADASTROS-UI-009-cpf-input-mask-and-unformatting.md)

## Notes

Security-relevant: for new users, the initial account password defaults to their own CPF number (a semi-public/guessable identifier) unless manually overridden before submit. Recorded as implemented; status AMBIGUOUS because intent (a convenience default vs. a security gap) cannot be determined from the code alone.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
