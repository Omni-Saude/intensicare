# RULE-SEPSE-086 — Historical sepsis pathway instances filtered by aceito=false

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The list of "previous" (trilhasInterativasAnteriores) interactive sepsis pathway instances, shown as dated history tabs, is fetched with an explicit filter {aceito: false} (i.e. "not accepted").

## Inputs

- aceito (query filter) (boolean, false (hardcoded))

## Outputs

- trilhasInterativasAnteriores (array)

## Logic

```text
data = getTrilhasInterativasSepse(..., { aceito: false })
trilhasInterativasAnteriores = data
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/sepse/[id_trilha]/index.tsx` | 70-96 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-08-003`

**Related rules:**

- [RULE-SEPSE-073](RULE-SEPSE-073-sepse-protocol-rejection-workflow-and-neutral-alert.md)
- [RULE-SEPSE-094](RULE-SEPSE-094-sepsis-pathway-accept-discard-workflow.md)

## Notes

Best interpretation: "aceito" likely denotes whether a clinician has formally accepted/signed-off a pathway instance into the permanent record, and the "historical" tab intentionally shows instances still pending acceptance/review rather than fully archived ones. This reading is inferred, not confirmed by any comment or type definition in this partition's scope; recorded verbatim per ground rules.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
