# RULE-AUTH-USUARIOS-061 — Context-switch destinations exclude bed level

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | validation |
| Status | OK |
| Confidence | low |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The organizational context-switcher (e.g. for changing which company/establishment/sector the UI is scoped to) supports exactly three destination levels — empresa, estabelecimento, setor — explicitly excluding "leito" (bed) as a switchable destination.

## Inputs

| name | type | range |
|---|---|---|
| destiny | string enum | empresa \| estabelecimento \| setor |

## Outputs

| name | type |
|---|---|
| destiny | string enum |

## Logic

```text
Utils.SwitchDestiny = "empresa" | "estabelecimento" | "setor"   // no "leito" member
```

## Edge cases (as implemented)

None demonstrated beyond the closed 3-value set.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Utils.d.ts` | 109-109 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-FE-07-004`

**Related rules:**

- [RULE-AUTH-USUARIOS-008](RULE-AUTH-USUARIOS-008-hierarchical-permission-cascade-get-permissoes-empresa-estab.md)
- [RULE-AUTH-USUARIOS-010](../data-validation/RULE-AUTH-USUARIOS-010-grupoacesso-hierarchical-scope-resolution.md)

## Notes

Extends the fixed category taxonomy with 'access-control' as the closest fit for a context/navigation-scope switcher; low practical significance but included per the 'choice enums with business meaning' instruction.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
