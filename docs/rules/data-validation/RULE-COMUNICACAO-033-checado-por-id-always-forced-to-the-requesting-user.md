# RULE-COMUNICACAO-033 — checado_por_id always forced to the requesting user

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
ChecagemObservacaoViewSet.manage_data overwrites checado_por_id with the current authenticated user's pk, preventing a client from checking off an observation on someone else's behalf.

## Inputs

| name | type | unit |
|---|---|---|
| request.user.pk | uuid |  |

## Outputs

| name | type | unit |
|---|---|---|
| data.checado_por_id | uuid |  |

## Logic

```text
data = super().manage_data(request, *args, **kwargs)
data["checado_por_id"] = str(request.user.pk)
return data
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/checagem_observacao.py` | 20-25 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-checagem-BE-05-002`

**Related rules:**

- [RULE-COMUNICACAO-006](../alert-threshold/RULE-COMUNICACAO-006-firebase-unread-count-decrement-when-an-observation-checagem.md)
- [RULE-COMUNICACAO-014](../care-pathway/RULE-COMUNICACAO-014-protocol-checklist-item-toggle-authorization.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
