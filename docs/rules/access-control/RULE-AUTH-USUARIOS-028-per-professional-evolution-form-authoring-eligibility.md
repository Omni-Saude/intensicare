# RULE-AUTH-USUARIOS-028 — Per-professional evolution-form authoring eligibility

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
For each of 10 professional roles (médico, enfermeiro, técnico de enfermagem, fisioterapeuta, musicoterapeuta, nutricionista, psicólogo, farmacêutico, fonoaudiólogo, intercorrência), the evolution-form tab is visible based on that role's specific "can_preencher_formulario_X" permission, but the ability to actually submit a new entry (canAdd passed into EvolucaoDefault) additionally requires the global can_manage_evolucao permission.

## Inputs

| name | type |
|---|---|
| can_preencher_formulario_<role> | boolean |
| can_manage_evolucao | boolean |

## Outputs

| name | type |
|---|---|
| canAdd (per role) | boolean |

## Logic

```text
for each role in {medico, enfermagem(via can_preencher_formulario_enfermeiro), tec_enfermagem,
                   fisioterapeuta, musicoterapeuta, nutricionista, psicologo, farmaceutico,
                   fonoaudiologo, intercorrencia}:
  tab_visible = can_preencher_formulario_<role>
  canAdd = can_preencher_formulario_<role> AND can_manage_evolucao
```

## Edge cases (as implemented)

A user who can_preencher_formulario_medico but lacks can_manage_evolucao still sees the "Médico" tab (tab_visible true) but cannot submit a new entry (canAdd false) — a view-without-edit state.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useEvolucaoMenu.tsx` | 30-386 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissoes-FE-07-004`

**Related rules:**

- [RULE-AUTH-USUARIOS-058](RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md)

## Notes

Extends the fixed category taxonomy with 'access-control' (see RULE-permissoes-FE-07-001). See RULE-evolucao-FE-07-006 for a naming discrepancy on the pharmacist ('farmaceutica') role key specifically.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
