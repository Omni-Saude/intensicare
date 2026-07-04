# RULE-SEPSE-088 — Empty-state for absent sepsis protocols

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The sepsis page shows an "no protocols" empty state unless there is either a current active interactive pathway instance, or at least one historical instance.

## Inputs

- trilhaInterativaAtual (object | undefined)
- trilhasInterativasAnteriores (array | undefined)

## Outputs

- rendered content (enum)

## Logic

```text
if (trilhaInterativaAtual || (trilhasInterativasAnteriores && trilhasInterativasAnteriores.length > 0)) {
  render Tabs (current + historical)
} else {
  render Empty("Não há protocolos de sepse para este paciente")
}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/sepse/[id_trilha]/index.tsx` | 261-298 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-08-005`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
