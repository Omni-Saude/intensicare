# RULE-AUTH-USUARIOS-060 — Company monitoring-modality enumeration (duplicate of LeitoTipo)

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Each company (Usuario.Empresa.tipo) is classified using the identical three-value literal union already used for bed monitoring modality (manual / automatica / homecare) — see RULE-ocupacao-FE-07-002.

## Inputs

| name | type | range |
|---|---|---|
| tipo | string enum | manual \| automatica \| homecare |

## Outputs

| name | type |
|---|---|
| tipo | string enum |

## Logic

```text
Usuario.Empresa.tipo: "manual" | "automatica" | "homecare"
```

## Edge cases (as implemented)

None; values are consistent with Ocupacao.LeitoTipo (no drift observed, unlike the Arquivo/Leito category-enum pair).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/User.d.ts` | 28-36 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-FE-07-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-022](../triage-eligibility/RULE-AUTH-USUARIOS-022-automatica-only-shortcuts-not-enforced-server-side.md)
- [RULE-AUTH-USUARIOS-026](../triage-eligibility/RULE-AUTH-USUARIOS-026-homecare-only-gestao-de-pacientes-tab.md)

## Notes

Independently redeclared rather than referencing Models.Ocupacao.LeitoTipo directly — a duplication risk (see RULE-arquivo-FE-07-002 for an example where an identical duplication pattern DID drift). This Empresa.tipo union is also used within this cluster to gate RULE-AUTH-USUARIOS-022 (automatica-only shortcuts) and RULE-AUTH-USUARIOS-026 (homecare-only tab); its canonical definition/duplication risk (vs Ocupacao.LeitoTipo) is more fully addressed under whichever cluster owns the Leito/Ocupacao model (movimentacao-adt / sinais-vitais).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
