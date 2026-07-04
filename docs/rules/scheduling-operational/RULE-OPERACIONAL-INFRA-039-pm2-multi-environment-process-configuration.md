# RULE-OPERACIONAL-INFRA-039 — PM2 multi-environment process configuration

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
ecosystem.config.js defines three named PM2 applications, one per deploy target: trilhas-demo (PORT 3002), trilhas-prod (PORT 3001), and trilhas-homol (PORT 3000). Each runs `yarn start` (i.e. a pre-built `next start`), uses `watch: true` (PM2 restarts the process whenever a file in the working directory changes), NODE_ENV is hardcoded to "production" for all three environment blocks (env_demo/env_prod/env_homol), and the shell interpreter is selected based on host platform (cmd.exe on win32, else sh).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| app_name | string | n/a | trilhas-demo \| trilhas-prod \| trilhas-homol |
| PORT | integer | port | 3000-3002 |

## Outputs

| name | type | unit |
|---|---|---|
| running_pm2_process | process | n/a |

## Logic

```text
FOR EACH env IN [demo(port=3002), prod(port=3001), homol(port=3000)]:
  pm2_app = {
    name: "trilhas-" + env,
    script: "yarn",
    args: "start",
    watch: true,               # auto-restart on filesystem change
    interpreter: (platform == "win32") ? "cmd.exe" : "sh",
    env_<env>: { PORT: port, NODE_ENV: "production" }
  }
```

## Edge cases (as implemented)

All three environments set NODE_ENV=production even for demo/homol, so any app code branching on NODE_ENV cannot distinguish staging/demo from real production at runtime — only the PORT and the externally-supplied --env flag (see RULE-DEPLOY-FE-09-002) differ. `watch: true` in a production-style deployment means any incidental file write to the working directory (e.g. log files written under the project root) could trigger an unplanned process restart.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `ecosystem.config.js` | 1-40 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-DEPLOY-FE-09-001`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-040](RULE-OPERACIONAL-INFRA-040-per-environment-deploy-script-workflow-with-asymmetric-env-f.md)
- [RULE-OPERACIONAL-INFRA-014](RULE-OPERACIONAL-INFRA-014-android-twa-digital-asset-links-restricted-to-a-single-homol.md)
- [RULE-OPERACIONAL-INFRA-041](RULE-OPERACIONAL-INFRA-041-environment-secret-files-excluded-from-version-control-per-d.md)

## Notes

Verbatim as coded; no correction applied.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
