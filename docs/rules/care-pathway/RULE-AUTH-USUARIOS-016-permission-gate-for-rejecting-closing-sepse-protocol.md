# RULE-AUTH-USUARIOS-016 — Permission gate for rejecting/closing SEPSE protocol

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On the interactive SEPSE trilha viewset, when the request does not accept the protocol (aceito falsy) during create/update/partial_update, the required trilha permission is set to "can_recusar_protocolo_sepse", so only users holding that permission may reject or close the protocol. The acting user is recorded as registrado_por and the parent trilha id is injected from the URL.

## Inputs

| name | type | range |
|---|---|---|
| data.aceito | boolean |  |
| action | enum | {create, update, partial_update} |

## Outputs

| name | type |
|---|---|
| permission_trilhas | tuple |

## Logic

```text
data["trilha"] = kwargs["trilhas__pk"]
data["registrado_por_id"] = request.user.get_pk
if not data.get("aceito") and action in ("partial_update", "update", "create"):
    self.permission_trilhas = ("can_recusar_protocolo_sepse",)
```

## Edge cases (as implemented)

Only the rejection/closure path is permission-gated here; acceptance is not restricted by this branch. Permission enforced via TrilhasPermissaoMixin (core.mixins, out of partition).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/views/trilha_interativa_sepse.py` | 40-52 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-authz-BE-02-020`

**Related rules:**

- [RULE-AUTH-USUARIOS-058](../access-control/RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

A commented-out sibling gate (can_rejeitar_protocolo_sepse, exceto POST) exists in item_trilha_interativa_sepse.py view.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
