# RULE-AUTH-USUARIOS-041 — Session cookie lifetimes and token verify/refresh workflow

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On sign-in, the auth token cookie ("trilhas.token") is set with a 30-day lifetime; on permission fetch, the permissions cookie ("trilhas.permissions") is set with a 1-day (86400s) lifetime. On every mount, if a token cookie exists it is verified against the backend; on verification failure the app attempts a token refresh, and if no token cookie exists at all the user is logged out immediately.

## Inputs

| name | type |
|---|---|
| trilhas.token cookie | string |

## Outputs

| name | type |
|---|---|
| session state | authenticated / refreshed / logged-out |

## Logic

```text
// cookie lifetimes:
trilhas.token maxAge = 30 * 24 * 60 * 60 seconds (30 days), path "/"
trilhas.permissions maxAge = 86400 seconds (1 day), path "/"

// on mount:
token = cookie("trilhas.token")
if token:
  _getAllPermissions()
  try:
    POST /verify-token/ {token} -> user data -> setUser(data)
    if id_empresa in route query:
      _getPermissions(id_empresa); _getEmpresaTipo(id_empresa)
  catch:
    show "Erro ao recuperar sessão"
    refreshToken(token)   // POST /refresh-token/ {token}; on failure -> logout()
else:
  logout()
```

## Edge cases (as implemented)

refreshToken destroys the "trilhas.token" cookie before attempting the refresh POST; if the refresh call itself fails, the catch handler both shows an error message AND calls logout() — a double-notification (verify-failure message, then implicitly whatever logout()'s own side effects are).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/contexts/AuthContext/AuthContext.tsx` | 39-126 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-auth-FE-07-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-024](RULE-AUTH-USUARIOS-024-post-login-company-selection-redirect-decision-tree.md)
- [RULE-AUTH-USUARIOS-057](RULE-AUTH-USUARIOS-057-authorization-header-format.md)

## Notes

Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
