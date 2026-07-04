# RULE-CADASTROS-UI-004 — Camera credential fields gated on can_manage_camera permission

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Camera-related fields - login/senha de câmera on the Estabelecimento form, IP da câmera on the Leito form - are only rendered for users holding the can_manage_camera permission.

## Inputs

| name | type |
|---|---|
| can_manage_camera | boolean |

## Outputs

| name | type |
|---|---|
| visibility of camera credential Form.Items | boolean |

## Logic

```text
if can_manage_camera:
  render "Login de acesso" (login_camera) and "Senha de acesso" (senha_camera)  // Estabelecimento
  render "IP da câmera do leito" (ip_camera)                                     // Leito
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormEstabelecimento/FormEstabelecimento.tsx` | 28,61-81 | `f9656be266` | primary |
| trilhas-frontend | `src/components/FormLeito/FormLeito.tsx` | 24,58-66 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-010`

**Related rules:**

- [RULE-CADASTROS-UI-002](RULE-CADASTROS-UI-002-leito-estabelecimento-name-and-code-locked-for-non-manual-co.md)

## Notes

Mirrored in src/components/FormLeito/FormLeito.tsx lines 24,58-66 for the ip_camera field.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
