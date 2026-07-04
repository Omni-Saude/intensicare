# RULE-AUDITORIA-LOGS-024 — Dead nested duplicate of EstadoLogView

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | workflow |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
LogView contains a nested inner class also named EstadoLogView (indented inside LogView, directly after get_context_data), whose body is functionally identical to the real module-level EstadoLogView defined immediately afterward. The inner class is unreachable: log/views/__init__.py and log/urls.py only ever reference the module-level EstadoLogView; LogView.EstadoLogView is never imported or instantiated anywhere.

## Inputs

_None._

## Outputs

_None._

## Logic

```text
class LogView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs): ...
    class EstadoLogView(LoginRequiredMixin, APIView):   # dead code, unreachable
        def get(self, request, *args, **kwargs): ...
class EstadoLogView(LoginRequiredMixin, APIView):        # the real, used one
    def get(self, request, *args, **kwargs): ...
```

## Edge cases (as implemented)

n/a — purely dead code, no runtime effect.

## Divergence

A nested inner class LogView.EstadoLogView duplicates the module-level EstadoLogView's body but is never imported/instantiated by log/views/__init__.py or log/urls.py -- purely dead code with no runtime effect, recorded verbatim as found (likely copy/paste-and-forget).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 193-271 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-020`

**Related rules:**

- [RULE-AUDITORIA-LOGS-031](RULE-AUDITORIA-LOGS-031-geo-cascade-endpoints-use-a-narrower-filter-whitelist-than-t.md)
- [RULE-AUDITORIA-LOGS-034](RULE-AUDITORIA-LOGS-034-country-region-city-cascading-filter-city-not-re-scoped-by-c.md)

## Notes

DISCREPANCY: recorded verbatim as found; likely a copy/paste-and-forget artifact rather than an intentional inner class.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
