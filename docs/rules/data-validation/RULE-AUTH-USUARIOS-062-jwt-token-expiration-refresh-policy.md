# RULE-AUTH-USUARIOS-062 — JWT token expiration/refresh policy

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Authentication JWT access tokens and refresh tokens are both valid for 30 days; expiration is enforced (JWT_VERIFY_EXPIRATION=True) and refresh is allowed (JWT_ALLOW_REFRESH=True).

## Inputs

_None._

## Outputs

| name | type | unit | range |
|---|---|---|---|
| JWT_EXPIRATION_DELTA | timedelta | days | 30 |
| JWT_REFRESH_EXPIRATION_DELTA | timedelta | days | 30 |

## Logic

```text
JWT_AUTH = {
  "JWT_VERIFY": True,
  "JWT_VERIFY_EXPIRATION": True,
  "JWT_EXPIRATION_DELTA": timedelta(days=30),
  "JWT_ALLOW_REFRESH": True,
  "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=30),
}
```

## Edge cases (as implemented)

Both the original token and its refresh token share the same 30-day validity window; there is no sliding/shorter-lived access-token pattern here (fairly long-lived tokens for a clinical system).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/settings.py` | 173-181 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-settings-BE-11-064`

**Related rules:**

- [RULE-AUTH-USUARIOS-041](../access-control/RULE-AUTH-USUARIOS-041-session-cookie-lifetimes-and-token-verify-refresh-workflow.md)

## Notes

Categorized as data-validation for lack of a better-fitting category in the given taxonomy; this is really a security/session-policy rule rather than input validation — flagged for the rebuild's auth design to reconsider token lifetimes for a clinical system.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
