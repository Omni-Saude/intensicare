# RULE-AUTH-USUARIOS-022 — Automatica-only shortcuts not enforced server-side

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
The sector occupancy page only shows navigation buttons to the Inconsistências and Dashboard analítico pages when the current company's tipo === "automatica". However, both destination pages (setor/[id_setor]/inconsistencias and setor/[id_setor]/dashboard) use the default validateRoute(ctx) call with no permission and no server-side re-check of empresa.tipo, so the restriction is UI-only and can be bypassed by direct URL navigation.

## Inputs

| name | type | range |
|---|---|---|
| empresaData.tipo | string enum | manual \| automatica \| homecare (observed values) |

## Outputs

| name | type |
|---|---|
| button-visibility | boolean |

## Logic

```text
// setor/[id_setor].tsx (parent page, CircularMenu items)
show "Relatórios" (Inconsistências) button  IF empresaData.tipo === "automatica"
show "Dashboard" button                     IF empresaData.tipo === "automatica"

// dashboard/index.tsx and inconsistencias/index.tsx (destination pages)
getServerSideProps = validateRoute(ctx)(...)   // no permission, no tipo check
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor].tsx` | 165-206 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-FE-08-004`

**Related rules:**

- [RULE-AUTH-USUARIOS-020](RULE-AUTH-USUARIOS-020-permission-string-ssr-route-guard-validateroute-incl-dead-co.md)
- [RULE-AUTH-USUARIOS-060](../care-pathway/RULE-AUTH-USUARIOS-060-company-monitoring-modality-enumeration-duplicate-of-leitoti.md)

## Notes

Destination pages confirmed at src/pages/.../setor/[id_setor]/dashboard/index.tsx lines 171-182 and src/pages/.../setor/[id_setor]/inconsistencias/index.tsx lines 61-72.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
