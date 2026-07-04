# RULE-OPERACIONAL-INFRA-047 — Celery beat scheduler — DatabaseScheduler, with a duplicate-beat-daemon discrepancy in demo/legacy configs

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | workflow |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
All active uwsgi configs run `celery -A trilhas beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler` as a standalone daemon, meaning periodic task schedules are stored in the Django DB (via django_celery_beat / admin) rather than in code (no in-code CELERYBEAT_SCHEDULE was found anywhere in this partition). However, uwsgi-demo.ini and uwsgi-homol-old.ini ALSO attach the embedded-beat flag (-B) to the 'atualizar_trilhas' worker line IN ADDITION TO the standalone beat daemon, meaning TWO beat schedulers would run concurrently against the same database-backed schedule in those environments — a known source of duplicate/double-fired periodic tasks. uwsgi-homol.ini and uwsgi-prod.ini (the current, non-'-old'/non-demo configs) do NOT have the -B flag on that worker line, keeping only the single standalone beat daemon.

## Inputs

_None._

## Outputs

| name | type | unit | range |
|---|---|---|---|
| active beat scheduler count per environment | integer |  | 2 for demo/homol-old (bug), 1 for homol/prod (correct) |

## Logic

```text
# demo.ini / homol-old.ini (BUGGY):
attach-daemon = celery -A trilhas beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
attach-daemon = celery -A trilhas worker -n <env>-trilhas@atualizar_trilhas -c 1 -E -Q <env>.trilhas.atualizar_trilhas -B
# homol.ini / prod.ini (CORRECT, single beat):
attach-daemon = celery -A trilhas beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
attach-daemon = celery -A trilhas worker -n <env>-trilhas@atualizar_trilhas -c 1 -E -Q <env>.trilhas.atualizar_trilhas   # no -B
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `uwsgi/uwsgi-demo.ini, uwsgi/uwsgi-homol-old.ini, uwsgi/uwsgi-homol.ini, uwsgi/uwsgi-prod.ini` | uwsgi-demo.ini:20-21; uwsgi-homol-old.ini:21-22; uwsgi-homol.ini:18-19; uwsgi-prod.ini:20-21 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ops-BE-11-068`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-046](RULE-OPERACIONAL-INFRA-046-celery-queue-naming-convention-environment-namespaced-routin.md)
- [RULE-OPERACIONAL-INFRA-025](RULE-OPERACIONAL-INFRA-025-per-queue-celery-worker-concurrency-assignment-serialize-pat.md)

## Notes

DISCREPANCY flagged for the demo environment specifically since uwsgi-demo.ini (unlike the '-old' homol file) does not carry an 'old'/deprecated naming signal and may still be an actively-used config; verify whether the demo environment is currently double-scheduling periodic tasks.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
