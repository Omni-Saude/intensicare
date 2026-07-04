# RULE-FORMULARIOS-CLINICOS-027 — Music-therapy global assessment enums

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
Music therapist global assessment covering general state (5-level), communication language, visual contact, spatiotemporal orientation, gross/fine motor coordination.

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
estado_geral {otimo, bom, regular, ruim, pessimo}
linguagem_comunicacao {verbal, nao_verbal, musical, nao_musical, corporal, nao_corporal}
contato_visual(boolean); orientacao_espaco_temporal(boolean)
coordenacao_motora_grossa {otima, boa, regular, ruim, pessima}
coordenacao_motora_fina {otima, boa, regular, ruim, pessima}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMusicoterapia.ts` | 22-90 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-music-FE-01-067`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-028](RULE-FORMULARIOS-CLINICOS-028-intramusical-relations-assessment-enum.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
