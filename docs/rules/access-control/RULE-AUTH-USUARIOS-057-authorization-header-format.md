# RULE-AUTH-USUARIOS-057 — Authorization header format

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
All authenticated API requests carry a bearer-style Authorization header formatted as the literal string "JWT" followed by a space and the raw token value (not the more common "Bearer" scheme).

## Inputs

| name | type |
|---|---|
| token | string |

## Outputs

| name | type |
|---|---|
| Authorization header | string |

## Logic

```text
api.defaults.headers.common["Authorization"] = `JWT ${token}`
```

## Edge cases (as implemented)

On sign-in, the Authorization header is first explicitly cleared to "" before the login POST is made, then set to `JWT ${token}` once login succeeds.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/contexts/AuthContext/AuthContext.tsx` | 47-47,132-138 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-auth-FE-07-003`

**Related rules:**

- [RULE-AUTH-USUARIOS-029](../data-validation/RULE-AUTH-USUARIOS-029-login-cascade-local-auth-first-incl-http-202-status.md)
- [RULE-AUTH-USUARIOS-041](RULE-AUTH-USUARIOS-041-session-cookie-lifetimes-and-token-verify-refresh-workflow.md)

## Notes

Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001). API-layer request-transformation rule per scope instructions.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
