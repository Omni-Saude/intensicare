# RULE-VENTILACAO-020 — Physiotherapy ventilation decision tree with divergent pressure ranges

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Ventilation type reveals spontaneous vs invasive vs non-invasive parameter sets; nested intermittent mode reveals hourly load and shift; PEEP/PINS ranges differ from other forms.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo_ventilacao (enum espontanea|mecanica_invasiva|mecanica_nao_invasiva) | | | |
| pressao_expiratoria_pulmonar/PEEP (cmH2O, 5-18) | | | |
| pressao_inspiratoria (cmH2O, 5-40) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| ventilation params (object) | | |

## Logic

```text
tipo_respiracao {nasal,bucal,mista,tqt}
tipo_ventilacao conditions:
  espontanea -> tipo_oxigenoterapia {ar_ambiente,cateter_nasal,mascara_venturi,macronebulizacao,continuo,intermitente}
                + o2_minuto(0-1000 lt/min) + carga_horaria(0-1000 h) + turno {diurno,noturno}
  mecanica_invasiva / mecanica_nao_invasiva (identical field sets):
    tipo_ventilacao_mecanica {intermitente,continua};
      intermitente -> carga_horaria(0-1000) + turno {diurno,noturno}
    parametros_ventilatorios {vcv,simv,psv,pcv,bilevel,ac}
    pressao_expiratoria_pulmonar (PEEP): 5-18
    pressao_inspiratoria: 5-40
    + free-string params: fracao_inspiratoria_oxigenio, volume_corrente, frequencia_respiratoria,
      ventilacao_minuto, tempo_inspiratorio, relacao_inspiratoria_expiratoria,
      limite_maximo_pressao_inspiratoria, pressao_inspiratoria_plato, pressao_suporte, fluxo, tigger, pressao_balonete
Section-level: indice_tobim, pimax, pemax, cuff_leak, iwi (all free strings).
```

## Edge cases (as implemented)

PEEP bounded 5-18 here vs 0-40 on movimentacao/physician forms; PINS 5-40 here vs 0-30 elsewhere - divergent validation for the same clinical parameter.

## Divergence

PEEP bounded 5-18 and PINS 5-40 here, MATCHING the backend homecare validators (RULE-VENTILACAO-022/023); but the movimentacao and physician forms (RULE-VENTILACAO-018/019) use PEEP 0-40 / PINS 0-30 - divergent validation bounds for the same clinical parameters across forms.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFisioterapeuta.ts` | 331-677 | `f9656be2` | primary |

- Merged from: RULE-resp-FE-01-053
- Related rules: RULE-VENTILACAO-018, RULE-VENTILACAO-019, RULE-VENTILACAO-022, RULE-VENTILACAO-023, RULE-VENTILACAO-001, RULE-VENTILACAO-026

## Notes

"indice_tobim" = Tobin index (RSBI); IWI = Integrative Weaning Index - weaning predictors captured as free text (no computation, so no verify). This physio form's PEEP/PINS bounds are the frontend counterpart of the backend homecare validators (5-18 / 5-40).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
