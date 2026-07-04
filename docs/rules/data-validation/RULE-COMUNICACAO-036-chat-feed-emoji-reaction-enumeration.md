# RULE-COMUNICACAO-036 — Chat/feed emoji-reaction enumeration

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
Reactions to a chat/feed message are restricted to one of seven named emoji types — smile, cry, approval, disapproval, strength, gratitude, heart.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| emoji | string enum |  | sorriso \| choro \| aprovacao \| reprovacao \| forca \| gratidao \| coracao |

## Outputs

| name | type | unit |
|---|---|---|
| emoji | string enum |  |

## Logic

```text
Chat.Reacao.TipoReacao = "sorriso" | "choro" | "aprovacao" | "reprovacao" | "forca" | "gratidao" | "coracao"
```

## Edge cases (as implemented)

None beyond the closed 7-value set.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Mensagem.d.ts` | 55-62 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-mensagem-FE-07-001`

**Related rules:**

- [RULE-COMUNICACAO-037](../scheduling-operational/RULE-COMUNICACAO-037-one-reaction-per-user-per-observation-unread-counter-side-ef.md)
- [RULE-COMUNICACAO-038](RULE-COMUNICACAO-038-reaction-usuario-observacao-always-server-injected.md)
- [RULE-COMUNICACAO-001](RULE-COMUNICACAO-001-reaction-count-by-emoji-aggregation-sql-correct-vs-order-dep.md)
- [RULE-COMUNICACAO-002](RULE-COMUNICACAO-002-current-user-s-own-reaction-id-on-an-observation.md)

## Notes

| RECONCILED: cross-checked against backend core/models/choices/reacao.py (ReacaoChoices.emoji()) — both enumerate the identical 7 values in the identical order (sorriso, choro, aprovacao, reprovacao, forca, gratidao, coracao). No divergence.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
