# RULE-FORMULARIOS-CLINICOS-033 — Physiotherapy motor-function enums

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule
Motor-function assessment enums for mobility (plegia/paresis patterns), tone, trophism and deformities/contractures.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_funcao_motora.* | enum[]/enum | null | see logic |

## Outputs

| Name | Type | Unit |
|---|---|---|
| motor assessment | object | null |

## Logic

```text
mobilidade multicheck {ativo, hipoativo, inativa, quadriplegico, hemiplegico, paraplegico, quadriparetico,
  hemiparetico, paraparetico, tetraplegia}
localizacao_mobilidade {direito, esquerdo}
tonus_muscular multicheck {normotonia, hipotonia, hipertonia_plastica, hipertonia_elastica}
trofismo multicheck {normotrofia, hipotrofia, hipertrofia}
deformidades_contraturas multicheck {membro_superior_direito, membro_superior_esquerdo, membro_inferior_direito,
  membro_inferior_esquerdo, membros_inferiores, membros_superiores, ausente}
```

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormFisioterapeuta.ts | 678-757 | f9656be2 | primary |

- Merged from: RULE-physio-FE-01-054
- Related rules: RULE-FORMULARIOS-CLINICOS-032, RULE-FORMULARIOS-CLINICOS-016

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
