# RULE-OPERACIONAL-INFRA-040 — Per-environment deploy script workflow with asymmetric env-file loading

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
package.json defines paired "init-deploy:<env>" (first deploy, `pm2 start`) and "deploy:<env>" (redeploy, `pm2 restart ... --update-env`) scripts for prod/homol/demo. All variants do `git pull && yarn install` then build and then start/restart via `ecosystem.config.js --only trilhas-<env> --env <env>`. However, only the homol and demo variants wrap the `next build` (and `next dev`) command with `env-cmd -f ./.homol.env` / `env-cmd -f ./.demo.env` to inject environment variables; the prod variants call `next build`/`next dev` directly with no env-cmd wrapper.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| target_env | string | n/a | prod \| homol \| demo |
| env_file | file | n/a | .homol.env \| .demo.env (prod has none) |

## Outputs

| name | type | unit |
|---|---|---|
| deployed_app | process | n/a |

## Logic

```text
# first-time deploy
init-deploy:prod  = git pull && yarn install && next build && pm2 start ecosystem.config.js --only trilhas-prod  --env prod
init-deploy:homol = git pull && yarn install && env-cmd -f ./.homol.env next build && pm2 start ecosystem.config.js --only trilhas-homol --env homol
init-deploy:demo  = git pull && yarn install && env-cmd -f ./.demo.env  next build && pm2 start ecosystem.config.js --only trilhas-demo  --env demo
# redeploy (adds --update-env, uses pm2 restart instead of start)
deploy:prod  = git pull && yarn install && next build && pm2 restart ecosystem.config.js --only trilhas-prod  --env prod  --update-env
deploy:homol = git pull && yarn install && env-cmd -f ./.homol.env next build && pm2 restart ecosystem.config.js --only trilhas-homol --env homol --update-env
deploy:demo  = git pull && yarn install && env-cmd -f ./.demo.env  next build && pm2 restart ecosystem.config.js --only trilhas-demo  --env demo  --update-env
```

## Edge cases (as implemented)

AMBIGUOUS: it is unclear from this partition whether prod relies on Next.js's own automatic loading of a `.env.production` file (which Next supports natively, unlike the non-standard "homol"/"demo" suffixes which require the explicit `env-cmd` wrapper), or whether this is a genuine gap where prod could build with stale/missing environment variables if no `.env.production` file is present on the deploy host. `.gitignore` only lists `.env.local`, `.homol.env`, `.demo.env`, and the three `.env.<stage>.local` variants — it does NOT list `.env.production`, so it is not clear a `.env.production` file is even expected to exist locally.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `package.json` | 5-17 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-DEPLOY-FE-09-002`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-039](RULE-OPERACIONAL-INFRA-039-pm2-multi-environment-process-configuration.md)
- [RULE-OPERACIONAL-INFRA-041](RULE-OPERACIONAL-INFRA-041-environment-secret-files-excluded-from-version-control-per-d.md)

## Notes

Verbatim as coded; flagged AMBIGUOUS per ground rules rather than corrected.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
