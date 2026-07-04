# RULE-BALANCO-HIDRICO-036 — Balanco hidrico auto-provisioning, no direct write endpoints

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
BalancoHidricoViewSet only exposes list/retrieve (Create/Update/Destroy mixins are commented out). The list() action auto-creates the day's BalancoHidrico record on first GET if none exists yet for the leito+day (see RULE-balanco-BE-08-007 for the exact date used).

## Inputs

- leito

## Outputs

- BalancoHidrico record

## Logic

```text
class BalancoHidricoViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    # CreateModelMixin, UpdateModelMixin, DestroyModelMixin intentionally NOT included
# record creation only happens as a side-effect of list()
```

## Edge cases (as implemented)

No API path exists in this viewset to explicitly create/update/delete a BalancoHidrico record.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/balanco_hidrico.py` | 18-30 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-BE-08-008`

**Related rules:**

- [RULE-BALANCO-HIDRICO-035](RULE-BALANCO-HIDRICO-035-list-endpoint-required-day-auto-create-with-mismatched-day-v.md)
- [RULE-BALANCO-HIDRICO-037](../scheduling-operational/RULE-BALANCO-HIDRICO-037-daily-fluid-balance-auto-creation-for-occupied-homecare-beds.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
