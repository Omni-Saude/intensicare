# RULE-OPERACIONAL-INFRA-062 — Per-environment uWSGI worker capacity and recycling thresholds

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Per-environment uWSGI worker/process capacity and recycling thresholds. Production runs workers=4/processes=4; demo runs workers=2/processes=2; old runs workers=2/processes=4. All three set max-requests=1000 (recycle a worker after 1000 requests) and idle=3600 (recycle idle workers after 3600s). harakiri (request timeout) is 360s in prod and demo, and is DISABLED in old (the ';harakiri=60' line is commented out).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| environment | enum | - | prod | demo | old |

## Outputs

| Name | Type | Unit |
|---|---|---|
| workers / processes / max-requests / harakiri / idle | config values | - |

## Logic

```text
# param          prod (uwsgi-prod.ini:6-16)   demo (uwsgi-demo.ini:6-16)   old (uwsgi-old.ini:6-15)
workers        = 4                            2                            2
processes      = 4                            2                            4
max-requests   = 1000                         1000                         1000
harakiri       = 360                          360                          (;harakiri=60 -> disabled)
idle           = 3600                         3600                         3600
```

## Edge cases (as implemented)

harakiri is disabled in uwsgi-old.ini (the line is commented out), so a hung request there is never force-killed, unlike the 360s cap in prod/demo. old.ini is asymmetric (workers=2 but processes=4) vs prod (4/4) and demo (2/2). max-requests=1000 recycles each worker after 1000 requests (leak mitigation); idle=3600 recycles workers idle for more than one hour; harakiri=360 kills any request exceeding 360 seconds.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `uwsgi/uwsgi-prod.ini` | 6-16 | `8166c07e` | primary |
| ahlabs-trilhas | `uwsgi/uwsgi-demo.ini` | 6-16 | `8166c07e` | duplicate |
| ahlabs-trilhas | `uwsgi/uwsgi-old.ini` | 6-15 | `8166c07e` | duplicate |

- Merged from: RULE-gap6-12
- Related rules: RULE-OPERACIONAL-INFRA-025, RULE-OPERACIONAL-INFRA-047

## Notes

Only the attach-daemon queue/worker list (lines ~20-33) was previously cited (RULE-OPERACIONAL-INFRA-025/047); the per-environment worker/process capacity and recycling thresholds (workers/processes/max-requests/harakiri/idle) were uncovered.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
