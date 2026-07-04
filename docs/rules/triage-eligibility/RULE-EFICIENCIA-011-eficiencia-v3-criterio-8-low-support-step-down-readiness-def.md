# RULE-EFICIENCIA-011 — Eficiencia v3 criterio_8 - low-support step-down readiness (defined, unwired)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: none |
| Confidence | medium |
| Cluster | eficiencia |

## Rule
Intended - >24h ICU AND absence of pressors/tachypnea/hypotension/ tachycardia AND absence of high O2 / invasive-ventilation / deep-sedation markers (step-down readiness). The implemented clause list contradicts the documented absence intent.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucao.dt_entrada, diurna_ventilacao, diurna_fluxo_o2, diurna_fio2, diurna_peep, diurna_glasgow, rass | | | |
| balanco qt_vol_nora, fr, pam, fc | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_8 | boolean | |

## Logic
```text
return all([
  diferenca_dias(dt_entrada) > 1,
  not all([ balanco_4h.filter(qt_vol_nora__gt=0, fr__lt=25, pam__lt=60, fc__gt=100) ]),
  ventilacao in <espontanea> and get_number(fluxo_o2) > 5,     # duplicated identical clause
  ventilacao in <espontanea> and get_number(fluxo_o2) > 5,
  get_number(diurna_fio2) > 45,
  get_number(diurna_peep) > 10,
  get_number(diurna_glasgow) < 13,
  int(rass) < -2 if rass else False,
]) if (ultima_evolucao and balanco_4h and ultimo_balanco) else False
```

## Edge cases (as implemented)
The clause list requires fio2>45, peep>10, GCS<13 and RASS<-2 all TRUE, which describes a HIGH-support patient - the opposite of the documented step-down ("ausencia de") intent. The spontaneous-vent + fluxo_o2>5 clause is duplicated identically. Unwired.

## Divergence
Implemented conditions invert the documented "absence-of-high-support" intent (they require FiO2>45, PEEP>10, GCS<13, RASS<-2 to be TRUE); one spontaneous-ventilation clause is duplicated.

## Verification
- Verdict: DISCREPANCY (impact: none)
- Reference: No single authoritative equation for an ICU step-down-readiness boolean; the relevant published anchors are ventilator-liberation / SBT-readiness criteria (ACCP/ATS 2017 ventilator liberation guideline, Ouellette et al., Chest 2017; AARC SBT CPG 2024): readiness requires LOW support - FiO2 <=0.40-0.50, PEEP <=8-10 cmH2O, and RASS near 0 (light sedation). These confirm the direction: FiO2>45%, PEEP>10, GCS<13 and RASS<-2 describe a HIGH-support / deeply sedated patient, the opposite of step-down readiness. (https://journal.chestnet.org/article/S0012-3692(16)62431-8/fulltext)
- Test vectors: 1/3 match
- Implemented conditions INVERT the documented 'ausencia de' (absence-of-high-support) intent: the all([...]) requires FiO2>45, PEEP>10, GCS<13 and RASS<-2 to be TRUE, which per ACCP/ATS ventilator-liberation criteria describes a high-support, deeply sedated patient - the opposite of a step-down candidate. The spontaneous-ventilation + fluxo_o2>5 clause is duplicated verbatim. Net effect: the criterion fires for high-support patients and stays silent for genuine step-down candidates. Unwired (calcular_criterio_8 commented out) so no production impact; would be high-impact (misdirected mobilization/step-down alert) if wired.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 830-876 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 143-146 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-088
- Related rules: RULE-EFICIENCIA-012

## Notes
Unwired (calcular_criterio_8 commented out in calcular_criterios).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
