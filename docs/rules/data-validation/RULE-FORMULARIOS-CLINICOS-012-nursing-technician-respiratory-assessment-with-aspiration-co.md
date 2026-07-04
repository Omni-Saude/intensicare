# RULE-FORMULARIOS-CLINICOS-012 — Nursing-technician respiratory assessment with aspiration conditional

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
TecEnfermagem respiratory exam; an aspiration boolean reveals a per-shift aspiration count; O2 flow bounded 0-1000.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| aspiracao | boolean |  |  |
| litros_por_minuto | number | L/min | 0-1000 |

## Outputs

| name | type | unit |
|---|---|---|
| respiratory assessment | object |  |

## Logic

```text
secrecao_traqueal {pouca, media, grande, aspiracao_ausente}; aspecto {mucoide, purulenta, mucopurulenta, sanguinolenta}
tosse {eficaz, nao_eficaz, ausente}; dreno_de_torax {esquerdo, direito, bilateral, ausente}
aspecto_da_secrecao {espessa, purulenta, serosa, fluida_hialina, hematica, sendimentos}; data_troca_selo(date)
aspiracao == true -> nr_aspiracoes_plantao (string, "Nº de aspirações x plantão")
dispositivos multicheck {ausente, tqt, cateter_o2, mascara_o2, vni, vm}
litros_por_minuto: number 0-1000
```

## Edge cases (as implemented)

O2 flow ceiling 1000 L/min is physiologically implausible (same loose bound as physio o2_minuto).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormTecEnfermagem.ts` | 114-215 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-tecnursing-FE-01-073`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-006](../alert-threshold/RULE-FORMULARIOS-CLINICOS-006-nursing-technician-diet-block-ranges-subset.md)
- [RULE-FORMULARIOS-CLINICOS-032](RULE-FORMULARIOS-CLINICOS-032-physiotherapy-neuro-cardio-respiratory-assessment-enums.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
