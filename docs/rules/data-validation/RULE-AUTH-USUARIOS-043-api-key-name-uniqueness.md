# RULE-AUTH-USUARIOS-043 — API key name uniqueness

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Refuses to create a new API key when an API key with the same name already exists; otherwise creates and prints the key.

## Inputs

| name | type | range |
|---|---|---|
| name_key | string | must be unique among APIKey.name |

## Outputs

| name | type |
|---|---|
| created_key \| error | string |

## Logic

```text
if APIKey.objects.filter(name=name).exists():
    error("Chave ja existe")
else:
    api_key, key = APIKey.objects.create_key(name=name)
    success("Chave criada com sucesso ...")
```

## Edge cases (as implemented)

Exact-name match check; runs inside a DB transaction (@transaction.atomic).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/management/commands/generate_api_key.py` | 12-19 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-VALIDATION-BE-12-022`

**Related rules:**

- [RULE-AUTH-USUARIOS-004](../access-control/RULE-AUTH-USUARIOS-004-partner-required-permission-predicate.md)

## Notes

Management command 'generate_api_key'.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
