# RULE-FORMULARIOS-CLINICOS-007 — Home-care incident triage - urgency grade and symptom classification

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Home-care incident record captures trigger type, urgency grade, and a symptom classification multicheck used for triage.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| tipo_acionamento | enum |  | intercorrencia\|ocorrencia |
| grau_urgencia | enum |  | normal\|urgencia\|sem_urgencia\|emergencia |
| classificacao_intercorrencia | enum[] (multicheck) |  | symptom list |

## Outputs

| name | type | unit |
|---|---|---|
| triage record | object |  |

## Logic

```text
tipo_acionamento {intercorrencia, ocorrencia}
grau_urgencia {normal, urgencia, sem_urgencia, emergencia}
classificacao_intercorrencia multicheck: sintomas_respiratorios, sintomas_urinarios, sintomas_gripais,
  taquicardia, bradicardia, febre, cefaleia, prostracao, problemas_estoma, nauseas_e_vomitos, hipodermoclise,
  hipoglicemia, hiperglicemia, dor_abdominal, confusao_mental, constipacao_intestinal, dor_garganta, edemas,
  problemas_oculares, problemas_vaginais, problemas_penianos, reacao_alergica, dor_precordial, lesoes_cutaneas,
  crise_convulsiva, sincope
observacao(string)
```

## Edge cases (as implemented)

grau_urgencia set is an unordered enum (normal/sem_urgencia both benign; emergencia most severe).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormIntercorrencia.ts` | 23-87 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-intercorrencia-FE-01-069`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-009](../care-pathway/RULE-FORMULARIOS-CLINICOS-009-home-care-incident-intervention-conduct-with-conditional-spe.md)
- [RULE-FORMULARIOS-CLINICOS-015](../care-pathway/RULE-FORMULARIOS-CLINICOS-015-home-care-incident-disposition-outcome-enum.md)
- [RULE-FORMULARIOS-CLINICOS-017](../care-pathway/RULE-FORMULARIOS-CLINICOS-017-intercorrencia-clinical-incident-complication-domain-concept.md)

## Notes

Not a formal published triage scale (4 unordered urgency values) -> verify=false.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
