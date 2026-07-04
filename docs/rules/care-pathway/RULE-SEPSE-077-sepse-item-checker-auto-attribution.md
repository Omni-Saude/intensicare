# RULE-SEPSE-077 — SEPSE item checker auto-attribution

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When a SEPSE checklist item is submitted as checado=true, the checker identity (checado_por_id) is automatically set to the authenticated request user, overriding any client-supplied value.

## Inputs

- data.checado (boolean)
- request.user (user)

## Outputs

- checado_por_id (uuid)

## Logic

```text
data = super().manage_data(request, ...)
if data.get("checado"):
    data["checado_por_id"] = request.user.get_pk
```

## Edge cases (as implemented)

Only applied when checado is truthy; unchecking does not set the attribution here (the serializer clears checado_por on uncheck).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/views/item_trilha_interativa_sepse.py` | 31-37 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-022`

**Related rules:**

- [RULE-SEPSE-075](RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)
- [RULE-SEPSE-098](../data-validation/RULE-SEPSE-098-sepsis-checklist-signer-requires-cpf-unlike-other-checklist.md)

## Notes

ItemViewSet requires ManageDataRequiredMixin; items listed filtered by trilha_interativa pk, ordered by (pacote, nome_item).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
