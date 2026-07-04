# RULE-COMUNICACAO-038 — Reaction usuario/observacao always server-injected

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
manage_data forces usuario_id to the current authenticated user and 'observacao' to the observacoes__pk URL kwarg on every reaction create, so a client cannot react as another user nor attach a reaction to an arbitrary observation via the body.

## Inputs

| name | type | unit |
|---|---|---|
| request.user.get_pk | uuid |  |
| kwargs.observacoes__pk | uuid |  |

## Outputs

| name | type | unit |
|---|---|---|
| data.usuario_id | uuid |  |
| data.observacao | uuid |  |

## Logic

```text
data["usuario_id"] = request.user.get_pk
data["observacao"] = kwargs.get("observacoes__pk")
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/reacao.py` | 24-33 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-reacao-BE-05-001`

**Related rules:**

- [RULE-COMUNICACAO-001](RULE-COMUNICACAO-001-reaction-count-by-emoji-aggregation-sql-correct-vs-order-dep.md)
- [RULE-COMUNICACAO-002](RULE-COMUNICACAO-002-current-user-s-own-reaction-id-on-an-observation.md)
- [RULE-COMUNICACAO-015](RULE-COMUNICACAO-015-chat-reaction-removal-restricted-to-its-own-author.md)
- [RULE-COMUNICACAO-027](../care-pathway/RULE-COMUNICACAO-027-reaction-hard-delete-override.md)
- [RULE-COMUNICACAO-037](../scheduling-operational/RULE-COMUNICACAO-037-one-reaction-per-user-per-observation-unread-counter-side-ef.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
