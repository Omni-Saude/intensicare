# RULE-AUTH-USUARIOS-021 — Bed-management page reuses access-group permission

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The Leitos (beds) management page is gated by the "can_manage_grupo_acesso" permission (the same permission that gates Grupos/access-group management), rather than a bed-specific or establishment-management permission such as can_manage_empresa.

## Inputs

| name | type | range |
|---|---|---|
| permission | string | can_manage_grupo_acesso |

## Outputs

| name | type |
|---|---|
| redirect-or-render | decision |

## Logic

```text
getServerSideProps = validateRoute(ctx, false, "can_manage_grupo_acesso")(...)
// identical permission string used for both /configuracoes/grupos and
// /configuracoes/leitos
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/configuracoes/leitos/index.tsx` | 363-376 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-FE-08-003`

**Related rules:**

- [RULE-AUTH-USUARIOS-020](RULE-AUTH-USUARIOS-020-permission-string-ssr-route-guard-validateroute-incl-dead-co.md)

## Notes

Recorded verbatim; may be an intentional coarse-grained "admin" permission reused across multiple config screens, or a copy-paste artifact. Compare with configuracoes/estabelecimentos/index.tsx and configuracoes/empresa/index.tsx, which both use "can_manage_empresa" for structurally similar company-configuration screens.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
