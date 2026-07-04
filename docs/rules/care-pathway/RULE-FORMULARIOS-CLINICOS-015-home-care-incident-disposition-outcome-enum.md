# RULE-FORMULARIOS-CLINICOS-015 — Home-care incident disposition/outcome enum

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
Disposition of an incident, from referral to medical/nursing/APH/hospital visits through telephone guidance to home death.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| itens_desfecho | enum |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| disposition | enum |  |

## Logic

```text
itens_desfecho options: encaminhada_visita_medica, encaminhada_visita_enfermagem, encaminhado_visita_aph_medico,
  encaminhado_hospital_prestador, encaminhado_hospital_familiar, encaminhada_visita_fisio,
  orientacao_telefonica, obito_domiciliar
```

## Edge cases (as implemented)

obito_domiciliar (home death) is a terminal disposition.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormIntercorrencia.ts` | 134-173 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-intercorrencia-FE-01-071`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-007](../triage-eligibility/RULE-FORMULARIOS-CLINICOS-007-home-care-incident-triage-urgency-grade-and-symptom-classifi.md)
- [RULE-FORMULARIOS-CLINICOS-009](RULE-FORMULARIOS-CLINICOS-009-home-care-incident-intervention-conduct-with-conditional-spe.md)

## Notes

relato_gastos (cost report) free-text group follows (174-185).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
