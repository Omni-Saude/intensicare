# RULE-FORMULARIOS-CLINICOS-021 — Home-care chronic-diagnosis catalog (backend humanize map + frontend physician multicheck)

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The 16-code chronic/critical homecare-diagnosis catalog. Backend maps each code to a display label (humanize_choice_diagnostico); frontend presents the identical 16 codes as a physician multicheck with a free-text observation. Same underlying vocabulary captured on both sides.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| val / diagnostico.tipos_diagnostico | string code / enum[] |  | one of the 16 keys below |

## Outputs

| name | type | unit |
|---|---|---|
| label / diagnoses | string / enum set |  |

## Logic

```text
# Backend: humanize_choice_diagnostico(val) = motivos[val]   (direct dict index, no default)
# Frontend: multicheck options[].value  (same 16 codes) + diagnostico.observacao(string)
motivos = {
  "doenca_arterial_corononariana":      "Doença arterial corononariana",
  "doenca_pulmonar_obstrutiva_cronica": "Doença pulmonar obstrutiva crônica",
  "esclerose_lateral_amiotrofica":      "Esclerose Lateral Amiotrófica",
  "fibrilacao_atrial_cronica":          "Fibrilação atrial crônica",
  "diabetes_mellitus_tipo1":            "Diabetes Mellitus tipo 1",
  "diabettes_mellitus_tipo2":           "Diabettes Mellitus tipo 2",
  "cirrose_hepatica":                   "Cirrose hepática",
  "pos_operatorio_de_cirurgia":         "Pós-operatório de cirurgia abdominal",
  "encefalopatia_pos_avc":              "Encefalopatia pós AVC",
  "encefalopatia_anoxica_isquemica":    "Encefalopatia anóxica isquêmica",
  "demencia_senil":                     "Demência senil",
  "doença_de_alzheimer":                "Doença de Alzheimer",   # key carries cedilla; others ASCII
  "doenca_de_parkinson":                "Doença de Parkinson",
  "ventilacao_mecanica_prolongada":     "Ventilação Mecânica prolongada",
  "desnutricao_cronica":                "Desnutrição crônica",
  "polineuropatia_do_doente_critico":   "Polineuropatia do doente crítico",
}
```

## Edge cases (as implemented)

Load-bearing verbatim typos in the CODE keys (shared BE+FE): 'corononariana', 'diabettes_mellitus_tipo2', and the Alzheimer key 'doença_de_alzheimer' carries a cedilla while all other keys are ASCII. The 'pos_operatorio_de_cirurgia' key's label silently narrows to 'de cirurgia abdominal'. Backend uses direct dict indexing with NO default -> KeyError on any code not in this map.

## Divergence

(1) Frontend defect: the multicheck options array ends with a stray trailing comma (dataFormFormularioMedico.ts:79) producing a sparse array hole / undefined option; the backend map has no such hole. (2) Backend humanize_choice_diagnostico raises KeyError for unlisted codes (no default), whereas the frontend is a plain option list (unlisted stored codes simply would not render). The 16 code keys and labels themselves MATCH exactly between BE and FE (including all typos and the cedilla).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/templatetags/formulario.py` | 13-33 | `8166c07eae` | primary |
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 22-83 | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-diagnostico-BE-09-001`
- `RULE-medico-FE-01-031`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-010](RULE-FORMULARIOS-CLINICOS-010-physician-physical-exam-enums-and-conditional-reveals.md)

## Notes

True cross-implementation duplicate (backend humanize map vs frontend multicheck of the same catalog), merged. Canonical choices likely also live on the Diagnostico model (different partition). Status DISCREPANCY preserved from both source entries (BE key typos + FE sparse-array hole).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
