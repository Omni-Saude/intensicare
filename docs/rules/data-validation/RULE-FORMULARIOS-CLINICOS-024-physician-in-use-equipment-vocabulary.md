# RULE-FORMULARIOS-CLINICOS-024 — Physician in-use equipment vocabulary

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
Multicheck of respiratory/support equipment in use.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| equipamentos_em_uso.tipos_equipamento | enum[] (multicheck) |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| equipment | enum set |  |

## Logic

```text
options { concentrador_oxigenio, cilindro_o2, bipap, cpap, coughassist, aspirador, ventilador_mecanico }
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 116-135 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-medico-FE-01-033`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-023](RULE-FORMULARIOS-CLINICOS-023-physician-in-use-invasive-devices-vocabulary.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
