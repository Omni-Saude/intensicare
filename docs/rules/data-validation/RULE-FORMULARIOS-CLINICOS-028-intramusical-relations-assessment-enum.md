# RULE-FORMULARIOS-CLINICOS-028 — Intramusical-relations assessment enum

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
Multicheck of the patient's relationship to musical instruments (music-therapy specific scale).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_global.relacoes_intramusicais | enum[] (multicheck) |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| intramusical relations | enum set |  |

## Logic

```text
options: nao_registra_presenca_de_instrumentos_musicais, manipula_instrumentos_musicais,
realiza_atividade_a_partir_dos_instrumentos_musicais, registra_a_presenca_de_instrumentos_musicais,
explora_instrumentos_musicais, realiza_atividade..._com_intencao_intermusical
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMusicoterapia.ts` | 91-128 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-music-FE-01-068`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-027](RULE-FORMULARIOS-CLINICOS-027-music-therapy-global-assessment-enums.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
