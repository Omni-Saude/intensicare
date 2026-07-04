# RULE-AUTH-USUARIOS-030 — External SSO fallback with auto-provisioning

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | triage-eligibility |
| Type | workflow |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
If local auth fails, the system POSTs credentials to an external SSO (americashealth.co). If the SSO responds with a JSON dict, the user is treated as authenticated: a local Usuario is looked up by email=username, and auto-created if missing, then issued a JWT. No project-specific (Trilhas) entitlement/access check is performed before provisioning or issuing the token.

## Inputs

| name | type | range |
|---|---|---|
| username | string | treated as an email address for the Usuario.get(email=username) lookup |
| password | string |  |

## Outputs

| name | type |
|---|---|
| jwt_payload | object |

## Logic

```text
requisicao = POST https://nps.americashealth.co/api/v2/auth-user/  {username, password}
requisicao_json = json.loads(requisicao.text)
if type(requisicao_json) is dict:
    try:
        usuario = Usuario.objects.get(email=username)
    except Usuario.DoesNotExist:
        usuario = Usuario.objects.create_user(
            username=username, nome=requisicao_json.get("nome"),
            email=username, password=password)
    context = montar_payload_de_usuario(usuario)
    return Response(context, status=202)
else:
    raise AuthenticationFailed("Falha na autenticação")
```

## Edge cases (as implemented)

requisicao_json could raise json.JSONDecodeError if the external service returns non-JSON (uncaught); a non-dict JSON payload (e.g., list, string, error) leads to AuthenticationFailed.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/login.py` | 44-69 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-auth-BE-05-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-029](../data-validation/RULE-AUTH-USUARIOS-029-login-cascade-local-auth-first-incl-http-202-status.md)
- [RULE-AUTH-USUARIOS-052](../data-validation/RULE-AUTH-USUARIOS-052-loginserializer-required-field-validation-never-enforced.md)

## Notes

Code contains an explicit TODO comment ('Adicionar verificação se tem acesso ao projeto Trilhas.') and no such check exists anywhere in the visible code path between the external dict response and user provisioning/JWT issuance - any user who can auth against the shared americashealth SSO gets a Trilhas account and token, regardless of Trilhas project entitlement.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
