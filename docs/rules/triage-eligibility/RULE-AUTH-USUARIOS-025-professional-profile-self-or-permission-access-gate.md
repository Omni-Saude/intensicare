# RULE-AUTH-USUARIOS-025 — Professional profile self-or-permission access gate

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
A user may view/edit a professional's profile page only if the profile belongs to themself, or if they hold the can_manage_usuario permission. Otherwise an "Acesso negado" (403) result is shown instead of the profile tabs. This check happens entirely client-side (getServerSideProps for this route has no permission requirement).

## Inputs

| name | type |
|---|---|
| id_profissional (route param) | string |
| user.usuario.id | string |
| permissions | string array |

## Outputs

| name | type |
|---|---|
| verifyUser | boolean |

## Logic

```text
verifyUser = (id_profissional === user.usuario?.id) || permissions?.includes("can_manage_usuario")
if (verifyUser && currentUser) {
  render profile Tabs
} else {
  render <Result status="403" title="Acesso negado" .../>
}
```

## Edge cases (as implemented)

currentUser must have loaded (async fetch) in addition to verifyUser being true, else the 403 branch is shown even for a permitted user while data is still loading.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/configuracoes/profissionais/[id_profissional]/index.tsx` | 49-101 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-profissional-FE-08-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-020](RULE-AUTH-USUARIOS-020-permission-string-ssr-route-guard-validateroute-incl-dead-co.md)
- [RULE-AUTH-USUARIOS-026](RULE-AUTH-USUARIOS-026-homecare-only-gestao-de-pacientes-tab.md)

## Notes

Because the server-side validateRoute(ctx) call for this route uses the default (no permission), this access boundary exists only client-side; see RULE-acesso-FE-08-001.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
