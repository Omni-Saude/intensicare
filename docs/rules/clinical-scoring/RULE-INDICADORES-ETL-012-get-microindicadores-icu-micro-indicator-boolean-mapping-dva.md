# RULE-INDICADORES-ETL-012 — get_microindicadores — ICU micro-indicator boolean mapping, DVA mapped to a drug-specific 'noradrenalina' key

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | medium |
| Cluster | indicadores-etl |

## Rule
If a micro_indicador record exists, builds a dict of ICU quality indicators: tempo_internacao (length of stay, passthrough), ventilacao_mecanica (VM=='S'), noradrenalina (DVA=='S'), sedacao (SEDACAO=='S'), hemodialise (HEMODIALISE=='S'), mortalidade_esperada (passthrough, expected mortality). The output key 'noradrenalina' is derived from a field named DVA, which in Brazilian ICU terminology commonly stands for 'droga vasoativa' (any vasoactive drug), not specifically norepinephrine.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| micro_indicador | MicroIndicadores instance or None |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| indicador | dict of booleans/values, or {} if micro_indicador is falsy |  |

## Logic
```text
IF micro_indicador:
  indicador = {
    "tempo_internacao": micro_indicador.TEMPO_PERMANENCIA,
    "ventilacao_mecanica": micro_indicador.VM == "S",
    "noradrenalina": micro_indicador.DVA == "S",
    "sedacao": micro_indicador.SEDACAO == "S",
    "hemodialise": micro_indicador.HEMODIALISE == "S",
    "mortalidade_esperada": micro_indicador.MORTALIDADE_ESPERADA,
  }
ELSE:
  indicador = {}
RETURN indicador
```

## Edge cases (as implemented)
Each boolean is strictly equality against the literal string 'S'; any other value (including None) evaluates False.

## Verification
- Verdict: DISCREPANCY (clinical impact: moderate)
- Reference: Evans L, Rhodes A, Alhazzani W, et al. Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2021. Crit Care Med. 2021;49(11):e1063-e1143 (norepinephrine is the first-line vasopressor, one specific agent among many vasoactive drugs). Corroborated by standard Brazilian ICU terminology: "DVA" = droga vasoativa = any vasoactive drug (noradrenalina, adrenalina, vasopressina, dopamina, dobutamina, nitroprussiato, nitroglicerina, levosimendana).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/micro_indicadores.py` | 47-58 | `8166c07e` | primary |

- Merged from: RULE-indic-BE-11-050
- Related rules: RULE-INDICADORES-ETL-011, RULE-INDICADORES-ETL-026, RULE-INDICADORES-ETL-027

## Notes
AMBIGUOUS: labeling a generic 'any vasoactive drug' flag (DVA) as specifically 'noradrenalina' (norepinephrine) in the output may overstate specificity — a patient on any vasoactive agent (not necessarily norepinephrine) would show as noradrenalina=true in this indicator. Recorded verbatim per audit instructions; flagged for clinical SME review. Also compare NoradrenalinaValidator (RULE-vitais-BE-11-027), which validates an actual dosing field distinct from this DVA flag.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
