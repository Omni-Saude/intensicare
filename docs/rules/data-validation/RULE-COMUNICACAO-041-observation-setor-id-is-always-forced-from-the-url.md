# RULE-COMUNICACAO-041 — Observation setor_id is always forced from the URL

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
try_set_setor overwrites request.data['setor_id'] with the setor__pk URL kwarg on every create; if that kwarg is missing/invalid, a ValidationError is raised requiring the setor be supplied via the URL - a client cannot set the setor via the request body.

## Inputs

| name | type | unit |
|---|---|---|
| kwargs.setor__pk | uuid |  |

## Outputs

| name | type | unit |
|---|---|---|
| request.data.setor_id | uuid |  |

## Logic

```text
try:
    request.data["setor_id"] = str(kwargs.get("setor__pk"))
except:
    raise ValidationError({"setor_obrigatorio": "é obrigatório o envio do setor na url"})
```

## Edge cases (as implemented)

kwargs.get returns None if absent, but str(None) = 'None' would not normally raise - the except is really only for pathological cases (e.g., immutable request.data); in practice a missing setor__pk still sets 'setor_id':'None' string rather than raising, unless the exception is triggered elsewhere (e.g., a QueryDict being immutable).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/observacao.py` | 40-46 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-observacao-BE-05-005`

**Related rules:**

- [RULE-COMUNICACAO-042](RULE-COMUNICACAO-042-observation-responsavel-id-is-always-forced-to-the-authentic.md)

## Notes

AMBIGUOUS edge case: str(None) does not raise, so the stated validation message may not actually trigger when setor__pk is absent from the URL (which would be unusual for a nested route, but noted for completeness). | RECONCILED: verified directly against core/api/v1/views/observacao.py try_set_setor — `request.data["setor_id"] = str(self.kwargs.get("setor__pk"))` — kwargs.get returns None when absent and str(None) does not raise, so the bare except/ValidationError path is not reachable via a missing URL kwarg alone; it would only fire for pathological cases (e.g. an immutable request.data). Status set to AMBIGUOUS per Phase-1's own flagged concern (preserved verbatim, not corrected).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
