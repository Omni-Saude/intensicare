# RULE-AUTH-USUARIOS-031 — Auto-hash plaintext password on user save

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
On saving a Usuario, if the stored password is not already a recognized hash, it is hashed.

## Inputs

| name | type |
|---|---|
| password | string |

## Outputs

| name | type |
|---|---|
| hashed_password | string |

## Logic

```text
try: identify_hasher(self.password)      # raises ValueError if not a known hash format
except ValueError: self.set_password(self.password)  # hash it
super().save()
```

## Edge cases (as implemented)

If password already hashed, left untouched (prevents double-hashing). No None-guard: identify_hasher(None) would raise (caught as ValueError? actually TypeError) — but Usuario.password is required by AbstractBaseUser.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/usuario.py` | 99-104 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-04-019`

**Related rules:**

- [RULE-AUTH-USUARIOS-054](RULE-AUTH-USUARIOS-054-cpfvalidator-brazilian-cpf-check-digit-validation.md)

## Notes

Usuario also enforces cpf unique (max_length=11), username unique with UnicodeUsernameValidator, pin default=settings.PIN_DEFAULT.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
