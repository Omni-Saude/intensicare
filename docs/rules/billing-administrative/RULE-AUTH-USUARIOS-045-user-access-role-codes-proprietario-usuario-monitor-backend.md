# RULE-AUTH-USUARIOS-045 — User access-role codes (proprietario/usuario/monitor) — backend model vs frontend type

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | billing-administrative |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Single-char codes stored in Usuario.acessos ArrayField that gate ownership/user/monitor capabilities and are auto-managed by membership save/delete hooks.
 The frontend independently re-declares the identical 3-value union (`Usuario.acessos = "u" | "p" | "m"`) but its JSDoc only documents "u" and "p"; the backend source resolves the frontend's undocumented third value "m" as "monitor", though no code in either partition mutates/enforces what the 'monitor' access level actually grants.

## Inputs

| name | type | range |
|---|---|---|
| acesso_code | char(1) | p (Proprietário) \| u (Usuario) \| m (monitor) |

## Outputs

| name | type |
|---|---|
| acesso_set | list[char] |

## Logic

```text
# Backend — core/models/choices/usuario.py:14-20
UsuarioChoices.acessos() -> (("p","Proprietário"),("u","Usuario"),("m","monitor")).
Usuario.acessos = ArrayField(CharField(max_length=1), default=list).
"p" managed by Empresa.save (RULE-empresa-BE-04-009);
"u" managed by UsuarioEmpresa save/delete (RULE-acesso-BE-04-031).
"m" (monitor) defined but not mutated by in-scope code.

# Frontend — src/@types/models/User.d.ts:37-43
/**
 * @description Acessos do usuário
 * @property {string} u usuário
 * @property {string} p proprietário
 */
type acessos = "u" | "p" | "m"   // "m" undocumented in FE; backend labels it "monitor"
```

## Edge cases (as implemented)

default empty list; codes appended idempotently by hooks. None demonstrated; "m" is simply unused/undocumented in this partition.

## Divergence

No divergence in the option list itself (both sides agree on exactly u|p|m). Kept AMBIGUOUS (not downgraded to OK) because, even after cross-referencing, no code in either partition mutates or consumes the "m"/monitor value — backend's own capture states "m" (monitor) defined but not mutated by in-scope code — so its functional meaning remains unconfirmed despite the label now being known.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/choices/usuario.py` | 14-20 | `8166c07eae` | primary |
| trilhas-frontend | `src/@types/models/User.d.ts` | 37-43 | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-006`
- `RULE-usuario-FE-07-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-032](RULE-AUTH-USUARIOS-032-user-company-membership-grants-u-access-and-cascades-group-c.md)
- [RULE-AUTH-USUARIOS-007](../access-control/RULE-AUTH-USUARIOS-007-empresa-read-vs-read-write-permissions-are-identical.md)

## Notes

---
Best guess for 'm' is 'moderador' or a role tied to medical staff (e.g. 'médico'), but this is speculation — flagged per ground rules rather than guessed silently. Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
