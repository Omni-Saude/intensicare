# RULE-OPERACIONAL-INFRA-041 — Environment secret files excluded from version control per deploy target

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
.gitignore excludes .env.local, .homol.env, .demo.env, .env.development.local, .env.test.local, and .env.production.local from the repository. Cross-referenced with package.json (RULE-DEPLOY-FE-09-002), the homol and demo deploy scripts explicitly load .homol.env / .demo.env via env-cmd — meaning each deploy target's secrets file must be provisioned directly on that target's server/host out-of-band, since it is never committed to git and would not arrive via `git pull`.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| env_filename | string | n/a | .homol.env \| .demo.env \| .env.local \| .env.*.local |

## Outputs

| name | type | unit | range |
|---|---|---|---|
| tracked_in_git | boolean | n/a | false |

## Logic

```text
GITIGNORED = [".env.local", ".homol.env", ".demo.env",
              ".env.development.local", ".env.test.local", ".env.production.local"]
FOR file IN GITIGNORED: file NOT tracked by git
=> deploy scripts referencing these files (env-cmd -f ./.homol.env, ./.demo.env)
   require the file to pre-exist on the deploy host already; `git pull`
   alone cannot supply it.
```

## Edge cases (as implemented)

If a fresh server is provisioned without the corresponding .homol.env/ .demo.env already present, `init-deploy:homol`/`init-deploy:demo` (which run `env-cmd -f ./.<env>.env next build`) would fail at build time for missing the file.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `.gitignore` | 27-34 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-DEPLOY-FE-09-008`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-040](RULE-OPERACIONAL-INFRA-040-per-environment-deploy-script-workflow-with-asymmetric-env-f.md)

## Notes

Cross-referenced with package.json lines 7,13,14,16,17.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
