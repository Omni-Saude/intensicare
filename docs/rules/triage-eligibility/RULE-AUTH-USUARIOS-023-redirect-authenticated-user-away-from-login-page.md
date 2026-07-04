# RULE-AUTH-USUARIOS-023 — Redirect authenticated user away from login page

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On the login page's getServerSideProps, if the "trilhas.token" cookie is present, the user is redirected to /empresa instead of seeing the login form.

## Inputs

| name | type |
|---|---|
| ctx.req.cookies["trilhas.token"] | string \| undefined |

## Outputs

| name | type |
|---|---|
| redirect-or-props | decision |

## Logic

```text
if (token) {
  redirect -> "/empresa", permanent: false
} else {
  props = { light: light === "true" }
}
```

## Edge cases (as implemented)

Empty-string token cookie is falsy in JS, so an empty token does not redirect.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/index.tsx` | 81-99 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-login-FE-08-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-020](RULE-AUTH-USUARIOS-020-permission-string-ssr-route-guard-validateroute-incl-dead-co.md)
- [RULE-AUTH-USUARIOS-024](../access-control/RULE-AUTH-USUARIOS-024-post-login-company-selection-redirect-decision-tree.md)

## Notes

Uses a plain string cookie check (unlike validateRoute's buggy object-typed token), so this particular guard behaves correctly.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
