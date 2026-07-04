# RULE-PRESCRICAO-039 — Pharmacist intervention vocabulary

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Multicheck vocabulary of pharmacist interventions/conducts.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| conduta_farmaceutica.condutas | enum[] (multicheck) |  | 33 options |

## Outputs
| Name | Type | Unit |
|---|---|---|
| interventions | enum set |  |

## Logic
```text
options include: ajuste_de_dose_de_medicamento, ajuste_de_dose_de_antimicrobiano, ajuste_de_posologia,
ausencia_ou_aprazamento_incorreto, correcao_de_eletrólitos, diluição, estabilidade,
indicacao_medicamento_alternativo, indicacao_de_forma_farmaceutica, dosagem_sérica,
interacao_medicamentosa_x_alimento_nutriente, interacao_medicamentosa_contra_indicada,
medicamentos_contra_indicados_via_sonda, nao_padrao_atendido, nao_padrao_substituido, ajuste_de_prescricao,
inclusao_exclusao_de_medicamento, substituicao_de_via_endovenosa_por_oral, substitiicao_de_antimicrobiano,
reconstituinte, sinalizacao_de_alegria, subdosagem_superdosagem, sugestao_suspensao_de_antimicrobiano,
sugestao_suspensao_outros_medicamentos, transcricao_de_prescricao_medica, tratamento_com_atb_duracao_alteracao,
velocidade_de_infusao, via_de_administracco, profilaxia_para_tev, profixia_para_lamg,
orientacoes_de_armazenamento_de_medicamentos
```

## Edge cases (as implemented)
Contains typos in values (substitiicao, via_de_administracco, profixia, sinalizacao_de_alegria) that persist to stored data.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFarmaceutico.ts` | 540-677 | `f9656be2` | primary |

- Merged from: RULE-pharma-FE-01-061

## Notes
The value sinalizacao_de_alegria ('signaling of joy') is almost certainly a typo for 'alergia' (allergy) — recorded verbatim.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
