# RULE-FORMULARIOS-CLINICOS-009 — Home-care incident intervention/conduct with conditional specific-intervention

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Interventions performed during an incident; a boolean flag reveals a required free-text specific intervention.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| intervencao | enum[] (multicheck) |  | see logic |
| realizado_intervencao_especifica | boolean |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| intervention record | object |  |

## Logic

```text
intervencao multicheck {passagem_sne, passagem_sng, troca_traqueostomia, passagem_sonda_gastrostomia,
  exames_laboratoriais, acesso_venoso_central, acesso_venoso_periferico}
realizado_intervencao_especifica == true -> qual_intervencao_especifica (string)
observacao(string) "Conduta"
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormIntercorrencia.ts` | 88-133 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-intercorrencia-FE-01-070`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-007](../triage-eligibility/RULE-FORMULARIOS-CLINICOS-007-home-care-incident-triage-urgency-grade-and-symptom-classifi.md)
- [RULE-FORMULARIOS-CLINICOS-015](RULE-FORMULARIOS-CLINICOS-015-home-care-incident-disposition-outcome-enum.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
