# RULE-AUTH-USUARIOS-029 — Login cascade - local auth first (incl. HTTP 202 status)

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On login, the system first attempts Django local authentication (username+password) before trying any external identity provider. Both the local-auth success path and the external-SSO success path (RULE-AUTH-USUARIOS-030) return this exact same payload shape and status code.

## Inputs

| name | type |
|---|---|
| username | string |
| password | string |

## Outputs

| name | type |
|---|---|
| jwt_payload | object |
| http_status | int |

## Logic

```text
usuario = authenticate(username=username, password=password)
if usuario:
    payload = jwt_payload_handler(usuario)
    token = jwt_encode_handler(payload)
    context = jwt_response_payload_handler(token, usuario)
    return Response(context, status=202)
# else fall through to RULE-auth-BE-05-002

# Confirmed by core/tests/test_usuario.py:35-38: POST /api/v1/login/ with a valid
# {username, password} asserts response.status_code == status.HTTP_202_ACCEPTED (202, not 200/201).
```

## Edge cases (as implemented)

authenticate() returns None for inactive or unknown users, or wrong password; falls through to external SSO attempt rather than failing immediately. Non-standard success status (202 rather than 200/201).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/login.py` | 29-42 | `8166c07eae` | primary |
| ahlabs-trilhas | `core/tests/test_usuario.py` | 35-38 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-auth-BE-05-001`
- `RULE-ACCESS-BE-12-032`

**Related rules:**

- [RULE-AUTH-USUARIOS-030](../triage-eligibility/RULE-AUTH-USUARIOS-030-external-sso-fallback-with-auto-provisioning.md)
- [RULE-AUTH-USUARIOS-052](RULE-AUTH-USUARIOS-052-loginserializer-required-field-validation-never-enforced.md)
- [RULE-AUTH-USUARIOS-057](../access-control/RULE-AUTH-USUARIOS-057-authorization-header-format.md)

## Notes

Success status code is 202 (Accepted), not 200. Login view implementation outside partition; behavior asserted by test. Merged: RULE-ACCESS-BE-12-032 independently captured the same 202-status fact via a test-file assertion (core/tests/test_usuario.py) that RULE-auth-BE-05-001 captured directly from the view source (core/api/v1/views/login.py); folded together to avoid double-counting one behavior.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
