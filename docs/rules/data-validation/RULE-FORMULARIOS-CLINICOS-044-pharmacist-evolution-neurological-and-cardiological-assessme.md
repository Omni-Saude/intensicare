# RULE-FORMULARIOS-CLINICOS-044 — Pharmacist evolution neurological and cardiological assessment vocabularies

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule

Two controlled-vocabulary assessment sections in the pharmacist evolution form. 'Avaliação Neurológica' constrains Pupilas, Orientação (level of consciousness), Emocional and Abertura Ocular to fixed option sets (plus a free-text Observação). 'Avaliação Cardiológica' constrains Pressão Arterial and Frequência Cardíaca to fixed option sets plus a boolean Drogas vasoativas flag. These are single-choice select vocabularies with no scoring, threshold or computation.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_neurologica.pupilas | select | - | isocoricas | miose | midriase |
| avaliacao_neurologica.orientacao | select | - | ativo | sonolento | torporoso | comatoso | reativo |
| avaliacao_neurologica.emocional | select | - | calmo | agitado | agressivo | letargico | nsa |
| avaliacao_neurologica.abertura_ocular | select | - | espontanea | ao_comando | a_dor | nenhuma |
| avaliacao_cardiologica.pressao_arterial | select | - | normotenso | hipotensao | hipertensao | instavel |
| avaliacao_cardiologica.frequencia_cardiaca | select | - | normocardio | bradicardico | taquicardio |
| avaliacao_cardiologica.drogas_vasoativas | boolean | - | true | false |

## Outputs

| Name | Type | Unit |
|---|---|---|
| validated enum / boolean / free-text values | mixed | - |

## Logic

```text
Avaliação Neurológica (avaliacao_neurologica):
  Pupilas         -> {isocoricas ("Isocóricas Fotoregente"), miose, midriase}
  Orientação      -> {ativo, sonolento, torporoso, comatoso, reativo}
  Emocional       -> {calmo, agitado, agressivo, letargico, nsa}
  Abertura Ocular -> {espontanea, ao_comando, a_dor, nenhuma}
  Observação      -> free text (string)

Avaliação Cardiológica (avaliacao_cardiologica):
  Pressão Arterial     -> {normotenso, hipotensao, hipertensao, instavel ("Instável Hemodinamicamente")}
  Frequência Cardíaca  -> {normocardio, bradicardico, taquicardio}
  Drogas vasoativas    -> boolean
```

## Edge cases (as implemented)

All select fields are single-choice enumerations; values are stored under nested keys avaliacao_neurologica.* / avaliacao_cardiologica.*. drogas_vasoativas is a boolean and observacao is unconstrained free text. The Pupilas option label reads 'Isocóricas Fotoregente' in the source (likely intended 'Fotoreagente'); preserved verbatim, no behavioral impact (the stored value is 'isocoricas').

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFarmaceutico.ts` | 277-366 | `f9656be2` | primary |

- Merged from: RULE-gap6-08
- Related rules: RULE-FORMULARIOS-CLINICOS-045, RULE-PRESCRICAO-037, RULE-PRESCRICAO-027

## Notes

Adjacent sections (22-275 medications, 367-414 antibiotics) are captured by RULE-PRESCRICAO-037/027; these neuro/cardio classification vocabularies were uncited. Minor: controlled-vocabulary field definitions with no thresholds, scoring or automated decisions.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
