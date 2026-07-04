# RULE-AUTH-USUARIOS-026 — Homecare-only "Gestão de Pacientes" tab

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On the professional profile page, the "Gestão de Pacientes" (patient management) tab is only rendered when the viewer has can_manage_usuario permission AND the current company's tipo === "homecare".

## Inputs

| name | type | range |
|---|---|---|
| can_manage_usuario | boolean |  |
| currentEmpresa.tipo | string enum | homecare \| manual \| automatica (observed) |

## Outputs

| name | type |
|---|---|
| tab-visibility | boolean |

## Logic

```text
if (can_manage_usuario && currentEmpresa && currentEmpresa.tipo === "homecare") {
  show "Gestão de Pacientes" tab
}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/configuracoes/profissionais/[id_profissional]/index.tsx` | 76-91 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-profissional-FE-08-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-025](RULE-AUTH-USUARIOS-025-professional-profile-self-or-permission-access-gate.md)
- [RULE-AUTH-USUARIOS-060](../care-pathway/RULE-AUTH-USUARIOS-060-company-monitoring-modality-enumeration-duplicate-of-leitoti.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
