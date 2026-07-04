# RULE-SEPSE-099 — Manual sepsis pathway active criteria descriptions (_REGRAS, 20 criteria) with criterio_8 key-typo

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sepse |

## Rule

The active _REGRAS dict on TrilhaSepse (manual pathway) defines total_criterios=20 and the human-readable clinical description text for criteria criterio_1..criterio_20; each descricao_criterio_N CharField default is _REGRAS.get("criterio_N"). DISCREPANCY: line 114 reads _REGRAS.get("criterio8") (missing underscore) instead of "criterio_8", so descricao_criterio_8 always defaults to None, silently dropping the stored/displayed description for the Glasgow-decline/delirium sepsis criterion.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| _REGRAS[criterion_key] | dict[str,str] | - | criterio_1..criterio_20 + total_criterios=20 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| descricao_criterio_1..20 default | string|null | - |

## Logic

```text
_REGRAS = {
  "total_criterios": 20,
  "criterio_1":  "Temperatura > 38,3ºC",
  "criterio_2":  "Ventilação Espontânea E (Frequência Respiratória > 20ipm OU SatO2 < 96 ) E ausência de ventilação mecânica",
  "criterio_3":  "Início de ventilação mecânica há menos que 1 dia",
  "criterio_4":  "Iniciada fusão de noradrenalina nas últimas 24h",
  "criterio_5":  "Tempo de enchimento capilar - TEC > 5 segundos",
  "criterio_6":  "Presença de Pressão arterial sistólica (PAS) < 90 mmHg OU Pressão arterial sistólica (PAD) < 60 mmHg nas últimas 24h",
  "criterio_7":  "debito urinario <=1200ml nas ultimas 24h OU (Presença de valor de creatinina >2mg/dL E ausência de hemodiálise)",
  "criterio_8":  "Presença de redução numérica da escala de coma de Glasgow em dois pontos ou mais nas últimas 24 horas (comparar com o ultimo checklist) OU presença de delirium",
  "criterio_9":  "Presença de valor de bilirrubina > 2mg/dl",
  "criterio_10": "Presença de Temperatura < 36oC verificado na evolução médica ou no balanço hídrico nas últimas 24h",
  "criterio_11": "Presença de Frequência cardíaca > 100 bpm nas últimas 12h verificado na evolução médica ou no balanço hídrico nas últimas 24h",
  "criterio_12": "Presença de PaCO2 < 32 mmHg E ventilação espontânea ... OU presença de valor de PaO2/FiO2 < 300 ...",
  "criterio_13": "Presença de valor de Lactato arterial ≥ 2,5 mmol/L",
  "criterio_14": "Presença de valores de Leucócitos > 12.000/mm3 nas últimas 24h verificados na evolução médica",
  "criterio_15": "Presença de valores de plaquetas < 100.000/mm3 nas últimas 24h",
  "criterio_16": "presença de “Baixa aceitação de Dieta VO” e valor de escala de coma de Glasgow >=13",
  "criterio_17": "Presença de valor de escala de coma de Glasgow <=13 nas últimas 12h",
  "criterio_18": "Presença de CVC OU CDL há mais de 7 dias",
  "criterio_19": "Presença de CVC OU CDL E região femoral E há mais de 5 dias",
  "criterio_20": "Presença de cirurgia abdominal recente",
}

descricao_criterio_1  default = _REGRAS.get("criterio_1")
...
descricao_criterio_8  default = _REGRAS.get("criterio8")   # BUG (line 114): key "criterio8" absent -> None
...
descricao_criterio_20 default = _REGRAS.get("criterio_20")
```

## Edge cases (as implemented)

descricao_criterio_8 is always None because line 114 looks up "criterio8" (no underscore) rather than "criterio_8"; the boolean criterio_8 field itself still functions, only its description text is dropped wherever it is read/exposed. All descricao_criterio_N defaults are captured at class/migration time and seed the CharField default for new rows. _ANTIGAS_REGRAS (27 criteria, lines 13-42) is the deprecated superseded ruleset; _REGRAS (20) is the active one.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 44-68,113-115 | `8166c07e` | primary |

- Merged from: RULE-gap6-06
- Related rules: RULE-SEPSE-066

## Notes

The active _REGRAS dict was never cited by any rule (only the deprecated _ANTIGAS_REGRAS block and dead commented-out criteria at 13-42/204-210/427-456/491-524 are grouped under RULE-SEPSE-066). Escalation-worthy: the criterio_8 key typo at line 114 is a live, silent bug that drops one criterion's clinical description.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
