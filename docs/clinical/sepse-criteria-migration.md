# SEPSE Criteria Migration: C1-C20 Legacy → SSC-2021 v3.0.0

**Date:** 2026-07-09
**Document:** M12 gap closure
**Domain:** Sepse (Sepsis Clinical Surveillance)

## Summary

The IntensiCare sepsis engine (`domain_sepsis.py` v3.0.0) migrated from a legacy model of 20 individual clinical criteria (C1-C20) to the **Surviving Sepsis Campaign 2021 (SSC-2021)** composite alert model. This document records the evolution for audit traceability.

## Legacy Model: 20 Individual Criteria (C1-C20)

The legacy system evaluated 20 individual criteria across two tiers:

### Major Criteria (C1-C9)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| C1 | Fever | Temp > 38.3°C |
| C2 | Respiratory distress | Spontaneous, no ventilator |
| C3 | Mechanical ventilation started | < 24h ago |
| C4 | Noradrenaline started | < 24h ago |
| C5 | Slow capillary refill | > 5s |
| C6 | Hypotension | PAS < 90 or PAD < 90 in 24h |
| C7 | Oliguria / rising creatinine | Oliguria or Cr increase |
| C8 | Glasgow drop / delirium | GCS drop or delirium |
| C9 | Hyperbilirubinemia | Bilirubin elevated |

### Minor Criteria (C10-C20)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| C10 | Hypothermia | Temp < 36°C in 24h |
| C11 | Tachycardia | HR elevated |
| C12 | Hypocapnia / poor oxygenation | PaCO₂ or SpO₂ |
| C13 | Elevated arterial lactate | Lactate > 2 mmol/L |
| C14 | Leukocytosis | WBC > 12 or < 4 in 24h |
| C15 | Thrombocytopenia | Plt < 100K in 24h |
| C16 | Poor oral intake | With preserved consciousness |
| C17 | Depressed consciousness | In last 12h |
| C18 | Central line 7 days | Indwelling central line |
| C19 | Femoral central line 5 days | Femoral CVC |
| C20 | Recent abdominal surgery | Minor surgery flag |

**Legacy Rule:** ≥3 major OR ≥4 minor = sepsis alert

## Current Model: 6 SSC-2021 Composite Alerts

The v3.0.0 engine uses 6 compound alerts aligned with SSC-2021 bundles:

| Alert ID | Name | Computed From |
|----------|------|---------------|
| ALERT-SEPSIS-SCREEN-01 | Screening (qSOFA/SIRS + infection) | qSOFA ≥ 2 or SIRS ≥ 2 + infection source |
| ALERT-SEPSIS-ORGAN-02 | Organ dysfunction | qSOFA ≥ 2 + lactate > 2 mmol/L |
| ALERT-SEPSIS-SHOCK-03 | Septic shock | Lactate ≥ 4 mmol/L or MAP < 65 mmHg |
| ALERT-SEPSIS-BUNDLE-OVERDUE-04 | Hour-1 bundle timer | Time since screen > 60 min without bundle |
| ALERT-SEPSIS-PCT-RISING-05 | PCT rising | Procalcitonin trend ↑ (treatment failure) |
| ALERT-SEPSIS-PCT-DEESC-06 | PCT de-escalation | Procalcitonin-guided antibiotic stop |

## Mapping: Legacy → Current

| Legacy Criteria | Covered By | Notes |
|----------------|-----------|-------|
| C1 (fever), C10 (hypothermia), C11 (tachycardia) | SCREEN-01 | Captured via SIRS score (temperature, HR, RR, WBC) |
| C6 (hypotension), C13 (lactate) | ORGAN-02 + SHOCK-03 | Lactate threshold and MAP evaluation |
| C7 (oliguria/creatinine) | SOFA score | Renal component evaluated in SOFA (separate domain) |
| C12 (hypocapnia/oxygenation) | SCREEN-01 | SpO₂/FiO₂ ratio in qSOFA/SIRS |
| C14 (leukocytosis) | SCREEN-01 | WBC component of SIRS |
| C3 (ventilation), C4 (noradrenaline) | SHOCK-03 | Vasopressor detection |
| C2, C5, C8, C9, C15-C20 | Not directly mapped | Criteria not validated in SSC-2021 composite model |

## Rationale

The SSC-2021 guidelines moved away from SIRS-only screening toward qSOFA + lactate-based risk stratification. The composite alert model:
1. **Reduces false positives** — SIRS criteria alone have 80%+ false positive rate in ICU
2. **Aligns with guidelines** — SSC-2021 bundle compliance is the clinical standard
3. **Enables bundle tracking** — Hour-1 bundle timer is clinically actionable, unlike individual criteria
4. **Supports antibiotic stewardship** — PCT-guided de-escalation (ALERT-06) reduces unnecessary antibiotics

## Legacy Rules Preserved

Rules SEPSE-066 (disabled legacy criteria) and SEPSE-099 (active criteria descriptions) document the transition. The 31 test vectors in `tests/test_domain_sepsis.py` validate both the new composite alerts and the legacy C1-C20 mapping for backward compatibility.

## Reference

- SSC-2021 Guidelines: _Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2021_
- Implementation: `src/intensicare/services/domain_sepsis.py` (v3.0.0, 1022 lines)
- Tests: `tests/test_domain_sepsis.py`
- Rules: `docs/rules/triage-eligibility/RULE-SEPSE-*.md`
