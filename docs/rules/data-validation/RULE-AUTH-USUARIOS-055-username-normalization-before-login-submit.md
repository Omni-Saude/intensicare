# RULE-AUTH-USUARIOS-055 — Username normalization before login submit

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
Before submitting login credentials, the username field is trimmed of leading/trailing whitespace and lower-cased; the password field is passed through unchanged.

## Inputs

| name | type |
|---|---|
| values.username | string |

## Outputs

| name | type |
|---|---|
| username (normalized) | string |

## Logic

```text
normalizedUsername = values.username?.trim().toLocaleLowerCase()
login({ ...values, username: normalizedUsername })
```

## Edge cases (as implemented)

If values.username is undefined, optional chaining yields undefined (no crash).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/index.tsx` | 61-67 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-login-FE-08-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-023](../triage-eligibility/RULE-AUTH-USUARIOS-023-redirect-authenticated-user-away-from-login-page.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
