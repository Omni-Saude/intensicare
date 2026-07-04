# RULE-FORMULARIOS-CLINICOS-031 — Nursing neurological assessment enums

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Neuro exam enums for pupils, orientation, emotional state, tone, eye-opening, motor deficit.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_neurologica.* | enum |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| neuro assessment | object |  |

## Logic

```text
pupilas {isocoricas (Fotoregente), miose, midriase}
orientacao {ativo, sonolento, torporoso, comatoso, reativo}
emocional {calmo, agitado, agressivo, letargico, nsa}
tonus {flacidez, rigidez, flexao_de_pernas, movimentos_ativos}
abertura_ocular {espontanea, ao_comando, a_dor, nenhuma}   // GCS eye-opening component labels
deficit_motor {sem_deficit, com_deficit, avaliacao_prejudicada (prejudicada pelo nível de consciência)}
```

## Edge cases (as implemented)

abertura_ocular mirrors GCS eye-opening subscale but stored categorically.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 473-553 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-nursing-FE-01-044`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-032](RULE-FORMULARIOS-CLINICOS-032-physiotherapy-neuro-cardio-respiratory-assessment-enums.md)
- [RULE-FORMULARIOS-CLINICOS-034](RULE-FORMULARIOS-CLINICOS-034-psychology-global-assessment-enums.md)

## Notes

orientacao/emocional/abertura_ocular enums reused across Fono, Psico, Fisio, TecEnf forms.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
