# RULE-EQUILIBRIO-002 — Renal-function drug substitution, morphine avoidance, and hypernatremia (Na>160) correction (criteria 5-8, 10)

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | equilibrio |

## Rule
Equilibrio trilha criteria 5-8 and 10: nephrotoxic drug substitution on worsening renal function, morphine avoidance under impaired creatinine clearance, and hypernatremia correction protocol.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sodio serico | float | mEq/L | — |
| clearance de creatinina | float | — | — |
| funcao renal (piora) | bool | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta + recomendacoes | string | — |

## Logic
```text
criterio_5  piora da funcao renal + uso de drogas nefrotoxicas ->
  substituir Cefepime -> Tazocin; substituir Vancomicina -> Linezolida;
  substituir losartan/captopril/enalapril -> bloqueador de canal de calcio (ou outra classe anti-HAS).
criterio_6  piora da funcao renal, reavaliar doses e substituicao de drogas nefrotoxicas
  (alerta sem recomendacoes especificas na facade; recomendacoes = []).
criterio_7  clearance de morfina prejudicado ->
  alto risco de acumulo de metabolitos (manter estado de coma); suspender morfina;
  substituir por fentanil, cetamina ou outros analgesicos.
criterio_8  funcao renal reduzida, reavaliar uso de morfina ->
  monitorar nivel de consciencia; preferencialmente substituir por fentanil, cetamina,
  metadona ou outros analgesicos.
criterio_10 hipernatremia com Na > 160 ->
  agua filtrada 400 ml 6/6h VO/SNE;
  Cloreto de sodio 0,22% a 84 ml/h;
  Hidroclorotiazida 25 mg comprimido, 2 comprimidos 1x/dia (para hipernatremia refrataria).
```

## Edge cases (as implemented)
Hypernatremia cutoff strictly Na > 160. criterio_6 has an alert label but an empty recomendacoes list (verbatim). Criteria are upstream boolean flags; facade holds only text. Note (surfacing): in live TrilhaEquilibrioModel.get_detalhe() only [1,3,6,8,9] are surfaced, so criterio_5, criterio_7 and criterio_10 text exists in the payload but is not surfaced by this model and does not affect alert color (criterio_6 and criterio_8 ARE surfaced).

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Sterns RH. Treatment of hypernatremia (UpToDate); Adrogué HJ, Madias NE. Hypernatremia. N Engl J Med 2000;342:1493-1499. Corroborated by AAFP "Diagnosis and Management of Sodium Disorders" (Am Fam Physician 2015;91(5):299-307) for the Na>160 mEq/L severe-symptom threshold and hypotonic free-water correction. Morphine-in-renal-impairment substitution corroborated by pharmacology of active metabolites M3G/M6G accumulation (Dean M. J Pain Symptom Manage 2004;28:497-504). (https://www.aafp.org/afp/2015/0301/p299)
- Test vectors: 4/4 match
- Verifiable anchors all match the reference: Na>160 mEq/L severe-hypernatremia cutoff (units correct here, in mEq/L), morphine avoidance under impaired creatinine clearance (metabolite accumulation), and vancomycin/nephrotoxic substitution rationale. The remaining specifics - exact agent choices (Cefepime->Tazocin, Vancomicina->Linezolida, ACEi/ARB->CCB) and the quantitative hypernatremia orders (NaCl 0.22% i.e. ~quarter-normal hypotonic saline at 84 ml/h, hydrochlorothiazide 25 mg x2 for refractory hypernatremia) - are institutional protocol with no single named guideline anchor, but none CONTRADICT published practice: 0.22% is a valid hypotonic free-water replacement fluid and thiazide use for refractory/nephrogenic hypernatremia is standard. No unit or threshold defect found. (Surfacing note per catalog: criterio_5/7/10 text is not surfaced by TrilhaEquilibrioModel.get_detalhe(); does not affect verification of the numeric predicate.)

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/facade/trilha_equilibrio.py | 37-63, 74-81 | 8166c07e | primary |
| ahlabs-trilhas | trilha_automatica/facade/equilibrio.py | 1-4 | 8166c07e | duplicate |

- Merged from: RULE-equilibrio-BE-01-011
- Related rules: RULE-EQUILIBRIO-001, RULE-EQUILIBRIO-003, RULE-EQUILIBRIO-004

## Notes
verify=true: category drug-dosing (specific drug substitutions, hypernatremia correction with NaCl 0.22% at 84 ml/h and hydrochlorothiazide 25 mg dosing). Preserve drug names/doses verbatim; no clinical correction applied.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
