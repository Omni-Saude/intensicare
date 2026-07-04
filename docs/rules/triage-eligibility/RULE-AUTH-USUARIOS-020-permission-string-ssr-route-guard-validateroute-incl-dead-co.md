# RULE-AUTH-USUARIOS-020 — Permission-string SSR route guard (validateRoute), incl. dead-code token check

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
validateRoute(ctx, ignorePermission=true, permission='') is the shared getServerSideProps guard used across the app. It parses the 'trilhas.token' and 'trilhas.permissions' cookies and redirects to '/' unless the permission check passes. For pages that pass an explicit permission string (ignorePermission=false), the page is rendered only if the parsed 'trilhas.permissions' array (JSON-decoded) includes that exact permission string; otherwise the request is redirected. However, the local `token` variable used in the guard's OTHER clause is initialized as `{} as string` (a plain, always-truthy object literal) rather than an empty string or null, so the `!token` half of the guard condition can never be true and never contributes to the redirect decision, regardless of whether a real 'trilhas.token' cookie is present. Combined with the common call pattern validateRoute(ctx) (defaults: ignorePermission=true, permission=''), pages that call it with no explicit permission perform NO effective server-side authentication check at all.

## Inputs

| name | type | range |
|---|---|---|
| ignorePermission | boolean | true \| false |
| permission | string (Models.Permission enum) | one of the app's permission slugs |
| ctx.req.cookies["trilhas.permissions"] | JSON-encoded string array |  |
| ctx.req.cookies["trilhas.token"] | string \| undefined |  |

## Outputs

| name | type |
|---|---|
| redirect-or-render | decision |

## Logic

```text
export const validateRoute = (ctx, ignorePermission = true, permission = "" as Models.Permission) =>
  async (callback) => {
    const { "trilhas.token": userToken } = parseCookies(ctx)
    const { "trilhas.permissions": userPermissions } = parseCookies(ctx)
    const { "theme.light": light } = parseCookies(ctx)
    const isLight = light === "true"

    let token = {} as string        // <-- BUG: truthy object, not "" or null
    let permissions = [] as Models.Permission[]

    if (userToken) token = userToken
    if (userPermissions) permissions = JSON.parse(userPermissions)

    if (!token || (!permissions.includes(permission) && !ignorePermission)) {
      return { redirect: { destination: "/", permanent: false } }
    }
    return callback({ token, isLight } as Models.ReturnWithProps)
  }
// !token is ALWAYS false (object literal is truthy) -> the token-presence half of the
// guard is dead code; only the (!permissions.includes(permission) && !ignorePermission)
// half can ever trigger a redirect. With default args (no permission passed), that half
// is also always false, so the whole condition is always false.
```

## Edge cases (as implemented)

No cookie at all: token stays {} (truthy) -> !token is false -> guard relies entirely on the second clause. With the common call pattern validateRoute(ctx) (ignorePermission defaults to true), !ignorePermission is always false, so the whole condition is false and the page renders with no server-side authentication check whatsoever.

Malformed/missing "trilhas.permissions" cookie => permissions = [] => guard always fails closed (redirects) whenever ignorePermission is false, regardless of the token bug in RULE-acesso-FE-08-001.

## Divergence

Not a BE/FE reconciliation — an intra-file merge of two Phase-1 captures of the same function (src/hocs/validateRoute.ts:5-38 fully contains :17-35). The 'no permission' code path (token-presence guard) is unreachable dead code due to `let token = {} as string` being always truthy; only the explicit permission-string branch (RULE-acesso-FE-08-002's original capture) is behaviorally live.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hocs/validateRoute.ts` | 5-38 | `f9656be266` | primary |
| trilhas-frontend | `src/hocs/validateRoute.ts` | 17-35 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-FE-08-001`
- `RULE-acesso-FE-08-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-021](RULE-AUTH-USUARIOS-021-bed-management-page-reuses-access-group-permission.md)
- [RULE-AUTH-USUARIOS-022](RULE-AUTH-USUARIOS-022-automatica-only-shortcuts-not-enforced-server-side.md)
- [RULE-AUTH-USUARIOS-023](RULE-AUTH-USUARIOS-023-redirect-authenticated-user-away-from-login-page.md)
- [RULE-AUTH-USUARIOS-025](RULE-AUTH-USUARIOS-025-professional-profile-self-or-permission-access-gate.md)
- [RULE-AUTH-USUARIOS-026](RULE-AUTH-USUARIOS-026-homecare-only-gestao-de-pacientes-tab.md)

## Notes

Concrete (permission-string, page) pairs observed in this partition: can_manage_empresa -> configuracoes/empresa/index.tsx (lines 131-143),
                       configuracoes/estabelecimentos/index.tsx (lines 348-360);
can_manage_grupo_acesso -> configuracoes/grupos/index.tsx (lines 211-223),
                            configuracoes/grupos/[id_grupo]/index.tsx (lines 232-244),
                            configuracoes/leitos/index.tsx (lines 364-376) [see RULE-acesso-FE-08-003];
can_manage_usuario -> configuracoes/profissionais/index.tsx (lines 216-228); can_access_camera -> setor/[id_setor]/cameras/index.tsx (lines 112-124); can_access_relatorio_evolucao -> relatorio-evolucao/index.tsx (lines 53-65).

---
This is the single highest-impact finding in this partition: every page that calls validateRoute(ctx) with default arguments (no explicit permission) performs NO effective server-side authentication check. Affected pages in this partition: src/pages/empresa/index.tsx, src/pages/empresa/[id_empresa].tsx, configuracoes/index.tsx, configuracoes/profissionais/[id_profissional]/index.tsx, configuracoes/setores/index.tsx, estabelecimento/[id_estabelecimento].tsx, chats/index.tsx, chats/[id_setor]/[id_usuario].tsx, setor/[id_setor].tsx, setor/[id_setor]/dashboard/index.tsx, setor/[id_setor]/inconsistencias/index.tsx, setor/[id_setor]/auditoria/index.tsx, setor/[id_setor]/auditoria/[id_ocupacao]/index.tsx, leito/.../ocupacao/[id_ocupacao].tsx, .../balanco/index.tsx, .../prescricao/index.tsx, .../sepse/[id_trilha]/index.tsx, feed/index.tsx. Rendering still depends on client-side API calls succeeding (which presumably enforce auth server-side in the backend), so real-world exposure depends on backend API behavior, which is out of scope for this partition. Recorded verbatim per ground rules; not corrected.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
