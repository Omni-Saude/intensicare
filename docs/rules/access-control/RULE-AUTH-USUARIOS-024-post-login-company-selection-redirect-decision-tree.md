# RULE-AUTH-USUARIOS-024 — Post-login company-selection redirect decision tree

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
After a successful login, the app decides where to send the user based on how many companies (empresas) the account is associated with — zero companies is treated as an error and forces logout; exactly one company auto-selects it and skips the selector screen; more than one sends the user to the company-selection screen.

## Inputs

| name | type | range |
|---|---|---|
| usuario.empresas.length | integer | 0, 1, or >1 |

## Outputs

| name | type |
|---|---|
| redirect route | string (route path) |

## Logic

```text
if usuario.empresas.length == 0:
  show error "Você não tem nenhuma permissão nesse perfil"
  logout()
else if usuario.empresas.length == 1:
  refreshToken(token)
  router.push(`/empresa/${usuario.empresas[0].id}`)
else:  // > 1
  refreshToken(token)
  router.push(`/empresa/`)
```

## Edge cases (as implemented)

The refreshToken(token) call happens for both the ==1 and >1 branches but NOT for the ==0 branch (which logs out instead). Errors thrown inside the try block (including from the API login call itself) are caught and shown as a generic "Algo deu errado no login." message.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/contexts/AuthContext/AuthContext.tsx` | 128-160 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-auth-FE-07-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-023](../triage-eligibility/RULE-AUTH-USUARIOS-023-redirect-authenticated-user-away-from-login-page.md)
- [RULE-AUTH-USUARIOS-041](RULE-AUTH-USUARIOS-041-session-cookie-lifetimes-and-token-verify-refresh-workflow.md)

## Notes

Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
