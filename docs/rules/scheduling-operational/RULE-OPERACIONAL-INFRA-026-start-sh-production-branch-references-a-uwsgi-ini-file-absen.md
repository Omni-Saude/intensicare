# RULE-OPERACIONAL-INFRA-026 — start.sh production branch references a uwsgi ini file absent from the repository

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

start.sh selects the uwsgi config to launch based on the ENVIRONMENT variable: any value other than 'production' launches `uwsgi/uwsgi-homol.ini`; ENVIRONMENT=='production' launches `uwsgi/uwsgi.ini`. No file named `uwsgi/uwsgi.ini` is tracked in this repository (only uwsgi-demo.ini, uwsgi-homol.ini, uwsgi-homol-old.ini, uwsgi-old.ini, and uwsgi-prod.ini exist).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| ENVIRONMENT | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| uwsgi ini file launched | string | - |

## Logic

```text
IF os.environ["ENVIRONMENT"] != "production":
  RUN "uwsgi --ini uwsgi/uwsgi-homol.ini"
ELSE:
  RUN "uwsgi --ini uwsgi/uwsgi.ini"     # file not present in repo; uwsgi-prod.ini exists instead
```

## Edge cases (as implemented)

As committed, launching this container with ENVIRONMENT=production would fail at the uwsgi startup step (file not found) unless a file literally named uwsgi.ini is created/copied at deploy time by a process not visible in this repository.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `start.sh` | 10-16 | `8166c07e` | primary |

- Merged from: RULE-ops-BE-11-069
- Related rules: RULE-OPERACIONAL-INFRA-046, RULE-OPERACIONAL-INFRA-025, RULE-OPERACIONAL-INFRA-047

## Notes

Recorded verbatim; either the deployment pipeline renames/symlinks uwsgi-prod.ini to uwsgi.ini outside this repo, or this is a latent break in the startup script. Flag for verifier to check the actual deploy pipeline/CI config (out of this partition's scope).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
