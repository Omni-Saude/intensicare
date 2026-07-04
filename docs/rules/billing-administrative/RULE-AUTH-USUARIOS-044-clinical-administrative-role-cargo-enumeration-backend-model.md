# RULE-AUTH-USUARIOS-044 — Clinical/administrative role (cargo) enumeration — backend model vs frontend copy

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | billing-administrative |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Allowed job roles for an access group (GrupoAcesso.cargo). The frontend independently re-declares the identical 15-value list (same codes, same labels, same order) as the `cargos` select-options array consumed for GrupoAcesso.cargo form fields, and additionally maintains a broader `cargosObject` humanize/label map that is a strict superset of `cargos` plus 6 extra codenames that have NO corresponding entry in the backend's GrupoAcesso.cargo choices.

## Inputs

| name | type | range |
|---|---|---|
| cargo | string (slug) | administrador\|coord_assistencial\|coord_medico\|medico_diarista\|medico_intensivista\|enfermeiro\|enfermeiro_telemed\|medico_telemed\|tec_enfermagem\|fisioterapeuta\|fonoaudiologo\|psicologo\|nutricionista\|odontologo\|farmaceutico |

## Outputs

| name | type |
|---|---|
| display_label | string |

## Logic

```text
# Backend — core/models/choices/grupo_acesso.py:1-20 (GrupoAcesso.cargo field choices)
GrupoAcessoChoices.cargos() -> 15 (value,label) role tuples covering coordination,
physicians (diarista/intensivista/telemedicine), nurses (+ telemedicine), nursing tech,
physiotherapist, speech therapist, psychologist, nutritionist, dentist, pharmacist.
GrupoAcesso.cargo = CharField(max_length=255, null/blank, choices=cargos()).

# Frontend — src/utils/cargos.ts:1-62 (`cargos`, select options; identical 15 values/labels/order)
cargos = [administrador, coord_assistencial, coord_medico, medico_diarista, medico_intensivista,
          enfermeiro, tec_enfermagem, fisioterapeuta, fonoaudiologo, psicologo, nutricionista,
          odontologo, farmaceutico, enfermeiro_telemed, medico_telemed]  # (value,label) pairs

# Frontend — src/utils/cargos.ts:64-87 (`cargosObject`, humanize map; SUPERSET of `cargos`)
cargosObject = { ...all 15 cargos codes..., 
  medico: "Médico", terapeuta: "Terapeuta", tecnico_enfermagem: "Técnico de Enfermagem",
  enfermagem: "Enfermeiro", musicoterapeuta: "Musicoterapeuta", intercorrencia: "Intercorrência" }
```

## Edge cases (as implemented)

Nullable/blank; advisory choices. cargosObject is a superset of cargos. Both "tec_enfermagem" and "tecnico_enfermagem" map to "Técnico de Enfermagem"; both "enfermeiro" and "enfermagem" map to "Enfermeiro" (synonym codes). "musicoterapeuta" and "intercorrencia" appear only in the humanize map, not the select list.

## Divergence

Frontend `cargosObject` (src/utils/cargos.ts:64-87) contains 6 codename keys with no corresponding value in the backend's GrupoAcessoChoices.cargos()/GrupoAcesso.cargo choices (core/models/choices/grupo_acesso.py:1-20): `medico`, `terapeuta`, `tecnico_enfermagem`, `enfermagem`, `musicoterapeuta`, `intercorrencia`. Two are synonym/legacy duplicates of already-valid backend codes (`tecnico_enfermagem`~`tec_enfermagem`, `enfermagem`~`enfermeiro`); `musicoterapeuta` and `intercorrencia` correspond to permission-flag suffixes (can_preencher_formulario_musicoterapeuta/intercorrencia) that exist in the permission catalog but have no GrupoAcesso.cargo counterpart. The backend model would reject any of these 6 as a GrupoAcesso.cargo value (not in choices); cargosObject is presumably used to humanize a broader set of string fields than strictly GrupoAcesso.cargo, but no code path confirming that scope is cited in either partition.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/choices/grupo_acesso.py` | 1-20 | `8166c07eae` | primary |
| trilhas-frontend | `src/utils/cargos.ts` | 1-87 | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-005`
- `RULE-cargos-FE-02-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-002](../data-validation/RULE-AUTH-USUARIOS-002-user-cargos-roles-empresa-scoped-lookup.md)
- [RULE-AUTH-USUARIOS-046](RULE-AUTH-USUARIOS-046-professional-council-conselho-and-state-of-council-enumerati.md)

## Notes

---
AMBIGUOUS because the two structures diverge: select options (cargos, 1-62) vs display map (cargosObject, 64-87). Verifier should reconcile against backend role choices; synonym pairs (tec_enfermagem/tecnico_enfermagem, enfermeiro/enfermagem) suggest legacy code drift. odontologo appears in select list but not in choicesConselho.

---
Frontend Phase-1 capture used category 'data-validation'; backend capture (kept as primary here) used 'billing-administrative' per its own Phase-1 taxonomy choice.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
