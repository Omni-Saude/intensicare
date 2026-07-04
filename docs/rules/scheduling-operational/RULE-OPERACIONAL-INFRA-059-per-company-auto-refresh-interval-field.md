# RULE-OPERACIONAL-INFRA-059 — Per-company auto-refresh interval field

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | threshold |
| Status | AMBIGUOUS |
| Confidence | low |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Each company (Usuario.Empresa) carries a numeric "tempo_atualizacao" (update time/interval) field, presumably configuring how often the UI should auto-refresh/poll for that company's data, but its unit (seconds vs milliseconds) and the code that actually applies it are not present in this partition.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| tempo_atualizacao | number | unknown — presumed seconds |  |

## Outputs

| name | type | unit |
|---|---|---|
| tempo_atualizacao | number | unknown |

## Logic

```text
Usuario.Empresa.tempo_atualizacao: number   // consumed by an auto-reload mechanism out of this partition's scope
```

## Edge cases (as implemented)

Not applied anywhere within this partition's files (AutoReloadContext in this partition only exposes a generic update/setUpdate boolean toggle with no interval/timer logic of its own).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/User.d.ts` | 34-34 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-FE-07-003`

**Related rules:** _none_

## Notes

Field name suggests a polling interval per the scope instructions' explicit callout of "polling intervals"; the consuming logic likely lives in a component/page file outside this hooks/contexts/@types partition.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
