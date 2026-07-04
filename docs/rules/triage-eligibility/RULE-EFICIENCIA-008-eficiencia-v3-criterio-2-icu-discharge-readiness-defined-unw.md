# RULE-EFICIENCIA-008 — Eficiencia v3 criterio_2 - ICU discharge readiness (defined, unwired)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: none |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Intended discharge-readiness gate - >24h admission, no ICU-discharge order, GCS>=11, temp<37.5, good/regular general state, room-air/low-flow O2<=2, no invasive VM or pressors >48h, and (as intended absences) TEC and lactate within range. Multiple checks are miswired.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucao.dt_entrada, diurna_glasgow, diurna_estado_geral, diurna_ventilacao, diurna_fluxo_o2, tempo_enchimento_capilar, diurna_lactato | | | |
| balanco.temp, qt_vol_nora/qt_vol_dobuta/qt_vol_nitropru | | | |
| cpoe.alta_uti | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_2 | boolean | |

## Logic
```text
return all([
  evolucao.dt_entrada < (now - 24h).date(),
  not cpoe_24h.aggregate(soma_alta_uti=Sum("alta_uti")).get("soma_alta_uti", 0),
  evolucao_24h.aggregate(max_glasgow=Max("diurna_glasgow")).get("max_glasgow", 0),  # truthiness, not >=11
  balanco_24h.aggregate(max_temp=Max("temp")).get("temp", 0),                       # WRONG KEY -> default 0 -> falsy
  evolucao.diurna_estado_geral in ["Regular", "Bom"],
  evolucao.diurna_ventilacao.strip().lower() in get_ventilacao("ar_ambiente")
      and get_number(diurna_fluxo_o2) <= 2,
  evolucao_mais_48h(...).filter(ventilacao in mecanica/invasiva),
  not balanco_mais_48h.filter(Q(qt_vol_nora=0)|Q(qt_vol_dobuta=0)|Q(qt_vol_nitropru=0)).exists(),
  get_number(tempo_enchimento_capilar) > 5,
  get_number(diurna_lactato) > 2,
]) if (windows truthy) else False
```

## Edge cases (as implemented)
The max_temp aggregate is read with key "temp" (not "max_temp") -> default 0 -> the whole all([...]) is always False. The Glasgow check tests truthiness of the max, not >=11. The nora/dobuta/nitropru clause uses Q(=0) OR-combined conditions. The tempo_enchimento_capilar>5 and lactato>2 terms are required TRUE, which contradicts the discharge-readiness intent (they describe an unstable patient).

## Divergence
Wrong aggregate key ("temp" vs "max_temp") makes the criterion permanently False; Glasgow reduced to truthiness rather than >=11; TEC>5 and lactate>2 required TRUE invert the "absence-of-instability" intent. Facade text (RULE-EFICIENCIA-012) describes the intended clinical-improvement discharge.

## Verification
- Verdict: DISCREPANCY (impact: none)
- Reference: No single authoritative published equation exists for an ICU-discharge-readiness boolean gate; SCCM ICU Admission/Discharge/Triage guidelines (Nates et al., Crit Care Med 2016) describe principles only. Individual thresholds are anchored to published references: serum lactate >2 mmol/L marks tissue hypoperfusion/septic shock (Sepsis-3, Singer et al., JAMA 2016;315:801-810) and prolonged capillary refill time (CRT >~3-5 s) marks peripheral hypoperfusion (ANDROMEDA-SHOCK, Hernandez et al., JAMA 2019). Composite gate itself is an internal business rule. (https://jamanetwork.com/journals/jama/fullarticle/2492881)
- Test vectors: 1/3 match
- Composite discharge gate is internal (no authoritative equation), but two code defects are objectively wrong against the docstring intent AND clinical sense: (1) balanco_24hrs.aggregate(max_temp=Max('temp')).get('temp',0) reads key 'temp' instead of 'max_temp' -> default 0 -> whole all([]) permanently False; (2) the code REQUIRES tempo_enchimento_capilar>5 and diurna_lactato>2 to be TRUE, whereas the docstring intent is 'ausencia de' (absence of) TEC>5 and lactate>2 -- lactate>2 mmol/L and CRT>5 s are Sepsis-3/ANDROMEDA markers of hypoperfusion, so requiring them TRUE for 'discharge readiness' is clinically inverted. Glasgow term tests truthiness of the max, not >=11. Because the criterion is UNWIRED (calcular_criterio_2 commented out) and permanently False even if wired, real-world patient impact is none; the inverted logic would be high-impact only if both the key bug were fixed and the rule wired.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 356-434 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 103-110 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-082
- Related rules: RULE-EFICIENCIA-012

## Notes
Unwired (calcular_criterio_2 commented out in calcular_criterios).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
