# RULE-SEPSE-084 — Active sepsis care-pathway selection

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Given the loaded occupancy (ocupacao) record, the sepsis page selects the applicable care-pathway (trilha) as the first element of ocupacao.trilhas whose tipo equals "sepse".

## Inputs

- ocupacao.trilhas (array of Trilha objects)

## Outputs

- trilhaSepse (Trilha | undefined)

## Logic

```text
trilhaSepse = ocupacao.trilhas.find(trilha => trilha.tipo === "sepse")
```

## Edge cases (as implemented)

If no trilha with tipo === "sepse" exists, trilhaSepse is undefined and the page falls to the "no protocols" empty state (RULE-sepse-FE-08-005).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/sepse/[id_trilha]/index.tsx` | 50-68 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-08-001`

**Related rules:**

- [RULE-SEPSE-084](RULE-SEPSE-084-active-sepsis-care-pathway-selection.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
