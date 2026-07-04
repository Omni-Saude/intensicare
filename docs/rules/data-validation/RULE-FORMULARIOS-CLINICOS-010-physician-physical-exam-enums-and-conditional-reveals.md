# RULE-FORMULARIOS-CLINICOS-010 — Physician physical-exam enums and conditional reveals

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Physical-exam findings with several select options that conditionally reveal max-length-constrained free-text fields, plus pupil/edema/elimination enums. Includes a TEC > 5 s capillary-refill flag.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| exame_fisico.tipos_exame | enum[] (multicheck) |  | includes tec_5s (TEC > 5s) |
| exame_fisico.pupilas | enum |  | isocoricas\|mioticas\|midriaticas\|anisocoricas |
| exame_fisico.edema | enum[] (multicheck) |  | mmss\|mmii\|outros |

## Outputs

| name | type | unit |
|---|---|---|
| exam findings | object |  |

## Logic

```text
tipos_exame options include regular_estado_geral, lesao_de_pele, tec_5s (TEC>5s), piora_clinica,
  acesso_venoso_central, vomitos_no_periodo, desnutricao, febre, sonda_vesical_de_demora, edema_periferico
pupilas {isocoricas, mioticas, midriaticas, anisocoricas}
edema multicheck {mmss, mmii, outros}; outros -> outros_edema (string, max 255)
eliminacoes_vesicais {regular, aumentada, diminuida, coloracao}; coloracao -> coloracao_eliminacoes_vesicais (string, max 255)
eliminacoes_intestinais {normal, diarreia, constipado}
ausculta_cardiaca {sem_alteracoes, outros}; outros -> outros_ausculta_cardiaca (string, max 255)
ausculta_pulmonar {sem_alteracoes, mv_bilateral (MV + bilateral com creptos difusos)}
intercorrencias (string, max 50)
```

## Edge cases (as implemented)

Free-text reveals enforce maxLength (255 or 50).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 136-269 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-medico-FE-01-034`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-005](../alert-threshold/RULE-FORMULARIOS-CLINICOS-005-nursing-cardiovascular-assessment-enums-with-capillary-refil.md)
- [RULE-FORMULARIOS-CLINICOS-021](RULE-FORMULARIOS-CLINICOS-021-home-care-chronic-diagnosis-catalog-backend-humanize-map-fro.md)
- [RULE-FORMULARIOS-CLINICOS-023](RULE-FORMULARIOS-CLINICOS-023-physician-in-use-invasive-devices-vocabulary.md)
- [RULE-FORMULARIOS-CLINICOS-024](RULE-FORMULARIOS-CLINICOS-024-physician-in-use-equipment-vocabulary.md)

## Notes

tec_5s reiterates the >5s capillary-refill alert (see RULE-FORMULARIOS-CLINICOS-005). Categorized data-validation form -> verify=false.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
