# RULE-FORMULARIOS-CLINICOS-025 — Speech-therapy global assessment enums

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
Speech therapist global assessment with communication mode, respiration/airway type, oxygen use, feeding acceptance and feeding route.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_global.* | enum/boolean |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| global assessment | object |  |

## Logic

```text
estado_geral {grave, regular}; orientacao {ativo, sonolento, torporoso, comatoso, reativo};
emocional {calmo, agitado, agressivo, letargico, nsa};
comunicacao {verbal, gestual, expressoes_faciais, comunicacao_alternativa, ausencia_comunicacao};
respiracao {espontanea_ar_ambiente, espontanea_suporte_o2, traqueostomia_plastica, traqueostomia_metalica,
  ventilacao_mecanica, ventilacao_nao_invasiva};
uso_oxigenoterapia(boolean);
alimentacao {total, parcial, recusa}; via {oral, sonda_nasoenteral, gastrostomia}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFonoaudiologo.ts` | 22-132 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fono-FE-01-062`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-026](RULE-FORMULARIOS-CLINICOS-026-speech-therapy-orofacial-and-language-enums.md)

## Notes

orientacao/emocional enums shared across Fono/Psico/Fisio/TecEnf/Nursing discipline forms.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
