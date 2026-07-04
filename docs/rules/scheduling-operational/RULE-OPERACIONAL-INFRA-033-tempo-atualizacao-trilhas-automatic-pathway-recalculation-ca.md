# RULE-OPERACIONAL-INFRA-033 — TEMPO_ATUALIZACAO_TRILHAS — automatic pathway recalculation cadence

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Defines (via environment variable, default 7200) the cadence in seconds at which automatic care pathways (trilhas) are expected to be recalculated/refreshed — i.e. a default 2-hour update interval.

## Inputs

_None._

## Outputs

| name | type | unit | range |
|---|---|---|---|
| TEMPO_ATUALIZACAO_TRILHAS | integer | seconds | default 7200 (2 hours), overridable via env var |

## Logic

```text
TEMPO_ATUALIZACAO_TRILHAS = os.environ.get("TEMPO_ATUALIZACAO_TRILHAS", 7200)
```

## Edge cases (as implemented)

When read from the environment, the value is a STRING (os.environ.get returns str), not cast to int here — any consumer must cast it; when the env var is unset, the Python int literal 7200 is used instead (a type-inconsistency between the default and the overridden path, though not necessarily a bug if the consumer always casts).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/settings.py` | 183 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-settings-BE-11-065`

**Related rules:** _none_

## Notes

The actual consumer of this setting (presumably a periodic task in trilha_automatica, out of BE-11 scope) is not visible in this partition; recorded here as the cadence DEFINITION only.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
