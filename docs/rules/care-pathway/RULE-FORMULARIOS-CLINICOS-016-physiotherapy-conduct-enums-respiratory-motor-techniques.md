# RULE-FORMULARIOS-CLINICOS-016 — Physiotherapy conduct enums (respiratory & motor techniques)

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Physiotherapy interventions selectable as respiratory and motor technique multichecks.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| fisioterapia_respiratoria / fisioterapia_motora | enum[] (multicheck) |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| therapy conduct | enum set |  |

## Logic

```text
fisioterapia_respiratoria multicheck {manobras_higiene_bronquica, padroes_ventilatorios,
  tecnicas_de_reexpansao_pulmonar, tosse_dirigida, tosse_assistida, tosse_induzida,
  treinamento_de_musculatura_respiratoria, aspiracao_de_via_aerea_superiore_traqueostomia,
  bag_squeezing, ajuste_de_oxigenoterapia, epap, ajuste_de_parametros_ventilatorios, aspiracao}
uso_de_cough_assist(string)
fisioterapia_motora multicheck {cinesioterapia_passiva, cinesioterapia_ativo_assistida, cinesioterapia_ativa,
  cinesioterapia_ativa_livre, cinesioterapia_resistida, sedestacao_no_leito, sedestacao_fora_do_leito,
  ortostatismo, deambulacao, treino_de_marcha, treino_de_equilibrio, exercicios_calistenicos,
  exercicios_isometricos, alongamento, mobilizacao_passiva, posicionamento_funcional, crioterapia,
  termoterapia, eletroterapia}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFisioterapeuta.ts` | 758-859 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-physio-FE-01-055`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-008](../triage-eligibility/RULE-FORMULARIOS-CLINICOS-008-physiotherapy-early-mobilization-eligibility-flags.md)
- [RULE-FORMULARIOS-CLINICOS-032](../data-validation/RULE-FORMULARIOS-CLINICOS-032-physiotherapy-neuro-cardio-respiratory-assessment-enums.md)
- [RULE-FORMULARIOS-CLINICOS-033](../data-validation/RULE-FORMULARIOS-CLINICOS-033-physiotherapy-motor-function-enums.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
