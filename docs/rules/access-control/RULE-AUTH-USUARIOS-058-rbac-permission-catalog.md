# RULE-AUTH-USUARIOS-058 — RBAC permission catalog

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The system defines a closed catalog of 28 permission flags spanning patient/occupancy management, camera access, auditing, user/group management, sepsis-protocol refusal, evolution-report access, per-professional evolution-form authoring (10 roles), and fluid-balance/prescription management.

## Inputs

| name | type | range |
|---|---|---|
| permission | string enum | 28 literal values (see logic) |

## Outputs

| name | type |
|---|---|
| Permissions | Record<Permission, boolean> |

## Logic

```text
Permission =
  can_create_paciente | can_add_movimentacao | can_remove_paciente | can_assist_ocupacao |
  can_upload_files_amhdocs | can_manage_empresa | can_access_camera | can_manage_camera |
  can_view_auditoria | can_view_ocupacoes | can_manage_usuario | can_manage_grupo_acesso |
  can_recusar_protocolo_sepse | can_access_relatorio_evolucao |
  can_preencher_formulario_medico | can_preencher_formulario_tec_enfermagem |
  can_preencher_formulario_enfermeiro | can_preencher_formulario_fisioterapeuta |
  can_preencher_formulario_musicoterapeuta | can_preencher_formulario_nutricionista |
  can_preencher_formulario_terapeuta | can_preencher_formulario_psicologo |
  can_preencher_formulario_fonoaudiologo | can_preencher_formulario_farmaceutico |
  can_preencher_formulario_intercorrencia | can_manage_evolucao | can_manage_prescricao |
  can_delete_horario_prescricao | can_delete_balanco_hidrico | can_manage_balanco_hidrico
Permissions = { [key in Permission]: boolean }
```

## Edge cases (as implemented)

can_preencher_formulario_terapeuta (generic "therapist") exists alongside more specific role permissions (fisioterapeuta, musicoterapeuta, psicologo, fonoaudiologo) — overlap/scope of this generic flag vs the specific ones is not clarified in this partition.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Permissions.d.ts` | 4-38 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissoes-FE-07-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-001](../data-validation/RULE-AUTH-USUARIOS-001-grupoacesso-permission-catalog-payload-computation.md)
- [RULE-AUTH-USUARIOS-037](../data-validation/RULE-AUTH-USUARIOS-037-full-permission-catalog-exposure.md)
- [RULE-AUTH-USUARIOS-016](../care-pathway/RULE-AUTH-USUARIOS-016-permission-gate-for-rejecting-closing-sepse-protocol.md)

## Notes

Extends the fixed category taxonomy with 'access-control' because RBAC rules fit none of the 9 supplied categories; grouped here with session/menu-gating rules for the verifier's convenience. Cross-cluster note: this static 28-permission union is the frontend counterpart of the backend's dynamically-aggregated PermissionsChoices.permissions() catalog (RULE-AUTH-USUARIOS-001/RULE-AUTH-USUARIOS-037); several underlying model Meta.permissions declarations that feed that catalog live in other clusters' partitions (e.g. balanco-hidrico's Balanco model, prescricao's PrescricaoContinua/HorarioPrescricao models, sepse's TrilhaInterativaSepse model, formularios-clinicos' Formulario model), so a full item-by-item BE/FE catalog reconciliation is out of this cluster's scope; spot-checked codenames (can_manage_empresa, can_manage_usuario, can_manage_grupo_acesso, can_recusar_protocolo_sepse, can_access_camera, can_view_auditoria/ocupacoes, can_create_paciente/can_add_movimentacao/can_remove_paciente, can_preencher_formulario_*) all have a matching backend Meta.permissions declaration.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
