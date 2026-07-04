# RULE-AUTH-USUARIOS-052 — LoginSerializer required-field validation never enforced

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
LoginSerializer declares username and password as required=True, but LoginViewSet.create() never instantiates/validates the serializer - it reads request.data.get(...) directly, so missing fields are never rejected with a 400; they instead become None and flow into authenticate() and the external POST.

## Inputs

| name | type | range |
|---|---|---|
| username | string | required=True (declared, not enforced) |
| password | string | required=True (declared, not enforced) |

## Outputs

_None._

## Logic

```text
# Declared but unused:
# LoginSerializer(username=CharField(required=True), password=CharField(required=True))
# Actual view:
username = request.data.get("username")   # None if absent, no validation error
password = request.data.get("password")
```

## Edge cases (as implemented)

Missing username/password does not raise ValidationError; authenticate(username=None, password=None) simply returns None, and the flow proceeds to the external SSO POST with None values.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/login.py` | 8-17 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-auth-BE-05-003`

**Related rules:**

- [RULE-AUTH-USUARIOS-029](RULE-AUTH-USUARIOS-029-login-cascade-local-auth-first-incl-http-202-status.md)
- [RULE-AUTH-USUARIOS-030](../triage-eligibility/RULE-AUTH-USUARIOS-030-external-sso-fallback-with-auto-provisioning.md)

## Notes

Cross-reference: core/api/v1/views/login.py lines 29-34 confirm request.data.get direct access, bypassing serializer validation entirely.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
