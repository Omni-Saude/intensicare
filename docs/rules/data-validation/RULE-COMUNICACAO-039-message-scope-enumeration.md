# RULE-COMUNICACAO-039 — Message scope enumeration

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Every chat message is scoped to exactly one of two levels — sector-level (setor) or bed-level (leito).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| tipo_mensagem | string enum |  | setor \| leito |

## Outputs

| name | type | unit |
|---|---|---|
| tipo_mensagem | string enum |  |

## Logic

```text
Chat.TipoMensagem = "setor" | "leito"
```

## Edge cases (as implemented)

tipo_mensagem is optional on Chat.Mensagem (may be undefined for message types that predate this scoping distinction, or for other message categories not scoped this way).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Mensagem.d.ts` | 41-41 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-mensagem-FE-07-002`

**Related rules:**

- [RULE-COMUNICACAO-011](../care-pathway/RULE-COMUNICACAO-011-notification-click-through-decision-tree.md)
- [RULE-COMUNICACAO-019](../scheduling-operational/RULE-COMUNICACAO-019-observation-auto-creates-a-notification-and-routes-by-target.md)

## Notes

| RECONCILED: cross-checked against backend core/models/observacao.py (tipo_mensagem = "leito" if self.leito else "setor") — matches this 2-value union exactly, no divergence.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
