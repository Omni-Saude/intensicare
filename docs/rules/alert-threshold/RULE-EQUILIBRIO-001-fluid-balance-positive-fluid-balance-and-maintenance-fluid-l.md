# RULE-EQUILIBRIO-001 — Fluid balance - positive fluid balance and maintenance-fluid limits (criteria 1-4)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | equilibrio |

## Rule
Fluid-balance ("equilibrio") trilha criteria 1-4 governing very-positive 24h fluid balance, accumulated positive balance, unnecessary maintenance soroterapia, and falling diuresis. Each criterion carries an alert label plus recommendation text.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| balanco hidrico 24h | float | ml/24h | — |
| balanco hidrico acumulado | float | ml | — |
| diurese trend (ultimas 6h) | float | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta + recomendacoes | string | — |

## Logic
```text
criterio_1  balanco hidrico muito positivo > 3000 ml/24h ->
  checar reducao/suspensao de soroterapia de manutencao, reduzir infusao de fluidos,
  concentrar solucao de drogas de infusao continua, considerar diureticos p/ zerar BH.
criterio_2  balanco hidrico acumulado muito positivo ->
  suspender/reduzir soroterapia; se manter, reduzir p/ 5 ml/h; considerar diureticos;
  evitar prova de expansao volemica ou bolus de cristaloides.
criterio_3  soroterapia desnecessaria, considerar suspensao ->
  reduzir/suspender; se manter, reduzir p/ 5 ml/h; preferir hidratacao com agua filtrada
  VO/SNE ate ~2400 ml/dia.
criterio_4  reducao da diurese nas ultimas 6h ->
  avaliar funcao renal (substituir drogas nefrotoxicas se piora), avaliar desidratacao/
  ingesta hidrica, avaliar risco de SEPSE (abertura de protocolo), avaliar retencao
  urinaria (bexigoma) / obstrucao de SVD, acessar status volemico por USG.
```

## Edge cases (as implemented)
Very-positive BH cutoff is strictly > 3000 ml/24h. Maintenance-fluid floor is 5 ml/h. Water hydration ceiling ~2400 ml/dia. Criteria are boolean flags computed upstream (Tasy); the facade holds only the alert/recommendation text, not the numeric predicate evaluation. Note (surfacing): in the live TrilhaEquilibrioModel.get_detalhe() only criteria [1,3,6,8,9] are surfaced, so criterio_2 and criterio_4 alert text exists in the payload but is NOT shown in this model's detalhe and does not contribute to the alert color (see RULE-EQUILIBRIO-003).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/facade/trilha_equilibrio.py | 1-36 | 8166c07e | primary |
| ahlabs-trilhas | trilha_automatica/facade/equilibrio.py | 1-4 | 8166c07e | duplicate |

- Merged from: RULE-equilibrio-BE-01-009
- Related rules: RULE-EQUILIBRIO-002, RULE-EQUILIBRIO-003, RULE-EQUILIBRIO-004

## Notes
= equilibrio_automatica. payload_equilibrio_automatica (trilha_automatica/facade/equilibrio.py) is a straight alias of payload_trilha_equilibrio (`payload_equilibrio_automatica = payload_trilha_equilibrio`) - same object, no divergence. No frontend copy of these criteria/thresholds exists (frontend only displays trilha alert colors, not the criteria text). verify=false: institutional fluid-management thresholds (3000 ml/24h, 5 ml/h, 2400 ml/dia) with no single named published anchor.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
