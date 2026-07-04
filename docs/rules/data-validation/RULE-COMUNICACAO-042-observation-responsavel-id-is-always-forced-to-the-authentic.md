# RULE-COMUNICACAO-042 — Observation responsavel_id is always forced to the authenticated user

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
try_set_responsavel overwrites request.data['responsavel_id'] with request.user.pk on every create; failure raises ValidationError requiring login.

## Inputs

| name | type | unit |
|---|---|---|
| request.user.pk | uuid |  |

## Outputs

| name | type | unit |
|---|---|---|
| request.data.responsavel_id | uuid |  |

## Logic

```text
try:
    request.data["responsavel_id"] = request.user.pk
except:
    raise ValidationError({"responsavel_obrigatorio": "é necessario estar logado para fazer essa observacao"})
```

## Edge cases (as implemented)

A client cannot spoof responsavel_id via the request body; it is always overwritten to the authenticated user.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/observacao.py` | 48-57 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-observacao-BE-05-006`

**Related rules:**

- [RULE-COMUNICACAO-041](RULE-COMUNICACAO-041-observation-setor-id-is-always-forced-from-the-url.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
