# RULE-OPERACIONAL-INFRA-048 — Backend CI gate covers only trilha_manual tests

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
Continuous integration for the backend runs on pushes to master and homologacao, provisions Python 3.8 + Postgres 10 + RabbitMQ, runs makemigrations+migrate, and then executes ONLY the trilha_manual test suite. No other app (core, trilha_automatica, trilha_homecare, log) is tested in CI; migration generation happens at CI time rather than being committed.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| push event branch | string |  | master \| homologacao |

## Outputs

| name | type | unit |
|---|---|---|
| CI pass/fail | boolean |  |

## Logic

```text
on push to [master, homologacao]:
  setup python 3.8, postgres:10 (db 'dev-trilhas'), rabbitmq
  pip install -r requirements.txt + psycopg2-binary
  python manage.py makemigrations && python manage.py migrate
  python manage.py test trilha_manual        # ONLY this app
```

## Edge cases (as implemented)

makemigrations at CI time can generate migrations that differ from any committed state; a hardcoded Postgres password ('DA-amh-2019') is embedded in the workflow file (security observation for the escalation report, not a functional rule).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `.github/workflows/trilhas.yml` | 1-63 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ops-COORD-001`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-056](../data-validation/RULE-OPERACIONAL-INFRA-056-diagnosis-list-checks-are-non-functional-vars-fromkeys-misus.md)

## Notes

Clinical-risk relevance: the automated ICU pathway engine (trilha_automatica) and homecare scoring engines (trilha_homecare) have NO CI test gate; only the manual-pathway app is regression-tested. Cross-reference BE-10 (trilha_manual tests encode parameter-range rules).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
