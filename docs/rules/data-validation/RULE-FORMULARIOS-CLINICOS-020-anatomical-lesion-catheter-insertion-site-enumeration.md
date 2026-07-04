# RULE-FORMULARIOS-CLINICOS-020 — Anatomical lesion / catheter-insertion site enumeration

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
Enumerated anatomical sites used to locate skin lesions/pressure injuries and vascular catheter/access insertion points (e.g. sacro/cóccix, trocanter, calcanhar/heel, and central-line sites subclávia/jugular/femural/radial).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| local | string |  | see enumeration (44 sites) |

## Outputs

| name | type | unit |
|---|---|---|
| label | string |  |

## Logic

```text
Values: orelha_direita, orelha_esquerda, escapular_direita, escapular_esquerda,
maleolo_direito, maleolo_esquerdo, cabeca, sacro_coccix, trocanter_direito,
trocanter_esquerdo, toronozelo_lateral, toronozelo_medial,
tuberosidade_esquiatica_direita, tuberosidade_esquiatica_esquerda,
calcanhar_direito, calcanhar_esquerdo, abdomen_direito, abdomen_esquerdo,
torax_direito, torax_esquerdo, msd, mse, mid, mie, subclavia_direita,
subclavia_esquerda, jugular_interna_direita, jugular_interna_esquerda,
femural_direita, femural_esquerda, radial_direita, radial_esquerda, sacral,
coccix, abdomen, mediastino, esterno, safena, inframaria_d, inframaria_e,
perianal, perineo, cervical
```

## Edge cases (as implemented)

Verbatim typos preserved: 'toronozelo_lateral'/'toronozelo_medial' (intended tornozelo = ankle), 'inframaria_d/e' (intended inframamária = inframammary). MSD/MSE/MID/MIE = upper/lower right/left limbs. Both sacro_coccix and separate sacral + coccix entries exist (redundant regions).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/localLesoes.ts` | 1-73 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-lesoes-FE-02-001`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-002](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md)
- [RULE-FORMULARIOS-CLINICOS-019](RULE-FORMULARIOS-CLINICOS-019-other-lesion-non-pressure-assessment-list.md)

## Notes

Shared vocabulary serving both lesion and vascular/surgical-access forms.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
