# RULE-SEPSE-085 — Interactive sepsis pathway completion transition

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
A "trilha interativa" (interactive checklist instance) attached to the current sepsis pathway is considered finished, and is moved from "current" to "historical", only when BOTH its concluida (concluded) flag AND finalizado (finalized) flag are true, and only for the instance matching the id currently tracked as active.

## Inputs

- data.id (string)
- data.concluida (boolean)
- data.finalizado (boolean)
- trilhaInterativaAtual.id (string | undefined)

## Outputs

- trilhaInterativaAtual (object | undefined)

## Logic

```text
if (data.id === trilhaInterativaAtual?.id && data.concluida && data.finalizado) {
  trilhaInterativaAtual = undefined
  refresh historical list (_getTrilhasInterativasHistoricos)
  refresh ocupacao (_getOcupacao)
}
```

## Edge cases (as implemented)

If only one of concluida/finalizado is true, the instance remains "current" (both flags are required, AND logic, not OR).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/sepse/[id_trilha]/index.tsx` | 98-143 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-08-002`

**Related rules:**

- [RULE-SEPSE-075](RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)
- [RULE-SEPSE-090](RULE-SEPSE-090-sepsis-protocol-lifecycle-state-display.md)
- [RULE-SEPSE-093](RULE-SEPSE-093-sepsis-pathway-dual-completion-flags.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
