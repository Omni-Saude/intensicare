# RULE-AUDITORIA-LOGS-022 — Log dashboard access control (authenticated-only, no staff/ownership check)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | eligibility |
| Status | AMBIGUOUS |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
All four log views (LogView, EstadoLogView, CityLogView, LogDetailView) are gated only by LoginRequiredMixin with login_url='/admin/'. There is no is_staff, is_superuser, or permission-class check anywhere in the log app. Any authenticated core.Usuario — not just administrators — can view the full log dashboard (including every other user's IP, geolocation, request/response bodies, and headers) and can fetch ANY single log's full detail by primary key (get_object_or_404(LogModel, pk=logs_pk)) with no ownership scoping to the requesting user.

## Inputs

| name | type | unit |
|---|---|---|
| request.user | Usuario | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| access_granted | boolean | n/a |

## Logic

```text
class LogView(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"   # only requires request.user.is_authenticated; no is_staff check
# identical pattern in EstadoLogView, CityLogView, LogDetailView
# LogDetailView.get_context_data: log = get_object_or_404(LogModel, pk=logs_pk)  # no owner/user filter
```

## Edge cases (as implemented)

A non-staff Usuario who is merely logged in can browse every other user's audit trail, including request/response bodies that may contain clinical or personal data logged by other apps' endpoints.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 17-21, 274-289 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-014`

**Related rules:**

- [RULE-AUDITORIA-LOGS-033](RULE-AUDITORIA-LOGS-033-log-field-exposure-scoping-logsimpleserializer-vs-logseriali.md)

## Notes

AMBIGUOUS: the URL prefix '/admin/' and login_url='/admin/' (Django admin login) strongly suggest staff-only intent, but the code as written only checks authentication, not staff status. Recorded verbatim per instructions; flagged as AMBIGUOUS rather than DISCREPANCY because there is no explicit 'should be staff-only' statement to compare against, only naming convention.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
