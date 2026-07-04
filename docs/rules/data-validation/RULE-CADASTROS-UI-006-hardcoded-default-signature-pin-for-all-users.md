# RULE-CADASTROS-UI-006 — Hardcoded default signature PIN for all users

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Every user's "Pin assinatura" (signature PIN) form field is initialized to the same fixed literal string, rendered in a disabled (non-editable) input, regardless of which user is being created or edited.

## Inputs

_None._

## Outputs

| name | type |
|---|---|
| form field "pin" | string (constant) |

## Logic

```text
initialValues.pin = "Homecare@Vidaconecta"     // same literal for every user, every time
<Form.Item name="pin"><Input disabled .../></Form.Item>
```

## Edge cases (as implemented)

Because the Input is disabled, users cannot change this value from the UI at all in this component; whether the backend independently assigns/overwrites a real per-user PIN, or this literal is actually submitted as-is, cannot be determined from this file alone.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormUsuario/FormUsuario.tsx` | 69-77,218-220 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-003`

**Related rules:**

- [RULE-CADASTROS-UI-005](RULE-CADASTROS-UI-005-new-user-password-auto-filled-from-cpf.md)

## Notes

Flagged AMBIGUOUS/security-relevant: a shared, hardcoded "signature PIN" default ("Homecare@Vidaconecta") looks unusual for a per-user electronic-signature credential; a verifier should confirm whether this field is actually submitted to the API or is purely cosmetic placeholder text overridden server-side.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
