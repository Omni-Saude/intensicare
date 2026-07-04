# RULE-AUTH-USUARIOS-063 — Shared default signing PIN (Usuario.pin defaults to settings.PIN_DEFAULT)

| Field | Value |
|---|---|
| Category | access-control |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | auth-usuarios |

## Rule

The Usuario.pin field ('PIN para assinar com o CryptoCubo') defaults to settings.PIN_DEFAULT (an env-configurable, deployment-wide value: trilhas/settings.py:245 PIN_DEFAULT = os.environ.get('PIN_DEFAULT')) instead of requiring each user to set a unique PIN. This PIN is later base64-encoded and sent verbatim as the signing credential to the CryptoCubo e-signature API (utils/cryptocubo.py:45-47), so any user whose PIN was never rotated legally signs medical documents/prescriptions with an org-wide shared default secret.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| settings.PIN_DEFAULT | string|null | - | os.environ.get('PIN_DEFAULT'), deployment-wide |
| usuario.pin | CharField | - | max_length=255, null/blank ok, default=PIN_DEFAULT |

## Outputs

| Name | Type | Unit |
|---|---|---|
| usuario.pin default / __PIN signing credential | string|null | - |

## Logic

```text
# core/models/usuario.py:55-61
pin = models.CharField(
    verbose_name="PIN para assinar com o CryptoCubo",
    null=True, blank=True, max_length=255,
    default=settings.PIN_DEFAULT,
)

# trilhas/settings.py:245
PIN_DEFAULT = os.environ.get("PIN_DEFAULT")

# utils/cryptocubo.py:45-47  (downstream use as the live signing credential)
self.__PIN = base64.b64encode(usuario.pin.encode("utf-8")).decode("utf-8") \
             or os.environ.get("CRYPTOCUBO_PIN")
```

## Edge cases (as implemented)

Every user created without an explicit pin inherits the same settings.PIN_DEFAULT value -> one shared signing secret across the whole deployment. The pin is base64-encoded and submitted as the CryptoCubo 'pin' credential, so a shared default makes signatures non-attributable to a unique per-user secret. pin is null/blank-able; if PIN_DEFAULT is unset (env missing) the default is None, which drives the downstream .encode() crash path documented in the cryptocubo PIN rules.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/usuario.py` | 55-61 | `8166c07e` | primary |
| ahlabs-trilhas | `trilhas/settings.py` | 245 | `8166c07e` | supporting |
| ahlabs-trilhas | `utils/cryptocubo.py` | 45-47 | `8166c07e` | supporting |

- Merged from: RULE-gap6-10
- Related rules: RULE-AUTH-USUARIOS-031, RULE-DOCUMENTACAO-FATURAMENTO-032, RULE-DOCUMENTACAO-FATURAMENTO-008

## Notes

SECURITY / COMPLIANCE CONCERN: the deployment ships an org-wide shared default signing PIN. Any user whose PIN is never rotated legally signs medical documents/prescriptions with the same shared secret, defeating per-user attribution of electronic signatures. Only usuario.py:99-104 (save()/password hashing, RULE-AUTH-USUARIOS-031) was previously cited; the pin-default assignment and its downstream use as a live signing credential were uncaptured. Escalation-worthy.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
