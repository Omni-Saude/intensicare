# RULE-VENTILACAO-005 — Ventilation C3 - FiO2xPEEP mismatch with severe hypoxemia

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | medium |
| Cluster | ventilacao |

## Rule

Flags a PEEP not matching the (different, severe) FiO2->PEEP table AND P/F ratio < 150.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| fio2 | | | |
| peep (cmH2O) | | | |
| relacao_po2_fio2 | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_3 (bool) | | |

## Logic

```text
if relacao_po2_fio2 (truthy) and peep > 0:
  key = str(fio2/100)[0:3]
  peep_new_table = {"0.0":[5],"0.1":[5],"0.2":[5],
                    "0.3":[5,6,7,8,9,10,11,12,13,14],"0.4":[14,15,16],
                    "0.5":[16,17,18],"0.6":[18,19,20,21,22],"0.7":[18,19,20,21,22],
                    "0.8":[22],"0.9":[22],"1.0":[22]}
  return (peep not in peep_new_table[key]) and (relacao_po2_fio2 < 150)
return False
```

## Edge cases (as implemented)

Guard here is clean (ratio truthy AND peep>0), unlike C2. Strict ratio<150. Same fio2/100 percentage assumption.

## Divergence

FiO2 unit inconsistency (fio2/100 percentage assumption vs fraction tests) as in C2 (RULE-VENTILACAO-004), but the guard is CORRECT here (ratio truthy AND peep>0). The C3 severe-hypoxemia table differs from the C2 moderate table.

## Verification

- Verdict: DISCREPANCY (clinical impact: moderate)
- Reference: ARDSNet Higher-PEEP/Lower-FiO2 titration table (severe hypoxemia arm, ALVEOLI). Canonical allowed PEEP per FiO2: 0.3->5,8,10,12,14; 0.4->14,16; 0.5->16,18; 0.5-0.8->20; 0.8->22; 0.9->22; 1.0->22,24. P/F <150 is the PROSEVA prone-positioning threshold (NEJM 2013;368:2159); Berlin "severe" ARDS is P/F <100 (JAMA 2012;307:2526).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 182-223 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-050
- Related rules: RULE-VENTILACAO-004, RULE-VENTILACAO-006, RULE-VENTILACAO-010, RULE-VENTILACAO-017

## Notes

Test test_trilha_ventilacao.py:95-105 (fio2=1,po2=149,peep=4 -> key '0.0'->[5], 4 not in [5], ratio 149<150 -> True).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
