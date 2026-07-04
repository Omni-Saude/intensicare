# RULE-OPERACIONAL-INFRA-038 — PWA service-worker generation disabled only in local development

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
next.config.js wraps the Next config with `withPwa({ dest: "public", disable: process.env.NODE_ENV === "development" })`. The generated service worker (public/sw.js) and workbox chunks (public/workbox-*.js) are explicitly gitignored, confirming they are build-time artifacts produced by next-pwa and are expected to be absent from source control and regenerated on every non-development build (demo/homol/prod, all of which set NODE_ENV=production per RULE-DEPLOY-FE-09-001).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| NODE_ENV | string | n/a | development \| production |

## Outputs

| name | type | unit |
|---|---|---|
| service_worker_generation_enabled | boolean | n/a |

## Logic

```text
pwa.disable = (NODE_ENV == "development") ? true : false
IF NOT disable:
  generate public/sw.js and public/workbox-*.js at build time
```

## Edge cases (as implemented)

Because all three PM2 environments (demo/homol/prod) set NODE_ENV="production", the PWA/service-worker is generated and active in all deployed environments, including demo/homol — there is no separate "staging" behavior for PWA caching.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `next.config.js` | 37-41 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-BUILD-FE-09-003`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-039](RULE-OPERACIONAL-INFRA-039-pm2-multi-environment-process-configuration.md)
- [RULE-OPERACIONAL-INFRA-042](RULE-OPERACIONAL-INFRA-042-pwa-app-identity-and-installed-app-display-behavior.md)

## Notes

Cross-referenced with .gitignore lines 38-40 (public/sw.js, public/workbox-*.js).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
