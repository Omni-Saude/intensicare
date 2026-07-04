# RULE-VENTILACAO-004 — Ventilation C2 - FiO2xPEEP mismatch with moderate hypoxemia

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | medium |
| Cluster | ventilacao |

## Rule

Flags a PEEP value not matching the expected FiO2->PEEP table AND P/F ratio between 151 and 300.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| fio2 (fraction/percent - see notes) | | | |
| peep (cmH2O) | | | |
| relacao_po2_fio2 | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_2 (bool) | | |

## Logic

```text
# guard (as written, malformed): effectively "po2 and fio2 present"; peep>0 NOT enforced
key = str(fio2/100)[0:3]   # e.g. fio2=40 -> "0.4"; fio2=1 -> "0.0"
peep_new_table = {"0.0":[5],"0.1":[5],"0.2":[5],"0.3":[5],"0.4":[5,6,7,8],
                  "0.5":[8,9,10],"0.6":[10],"0.7":[10,11,12],"0.8":[14],
                  "0.9":[14,15,16,17,18],"1.0":[18,19,20,21,22,23,24]}
return (peep not in peep_new_table[key]) and (151 < relacao_po2_fio2 < 300)
```

## Edge cases (as implemented)

Guard is a tangled expression: `X if (po2 and fio2) else False and peep>0 if peep else False` -> the peep>0 requirement is dead (inside `False and ...`); guard true iff po2 and fio2 truthy. arredondar divides fio2 by 100 (percentage assumption) yet tests pass fio2=1 giving key "0.0". Strict 151<ratio<300.

## Divergence

(1) Malformed guard: peep>0 requirement is dead code (inside `False and ...`), so PEEP>0 is NOT enforced. (2) FiO2 unit inconsistency: key = str(fio2/100)[0:3] assumes percentage (fio2=40 -> "0.4") but tests/ratio pass fio2 as a fraction (fio2=1 -> key "0.0"). C2 table differs from C3 table (RULE-VENTILACAO-005).

## Verification

- Verdict: DISCREPANCY (clinical impact: moderate)
- Reference: ARDSNet Lower-PEEP/Higher-FiO2 titration table (moderate/less-severe hypoxemia arm). Canonical allowed PEEP per FiO2: 0.3->5; 0.4->5,8; 0.5->8,10; 0.6->10; 0.7->10,12,14; 0.8->14; 0.9->14,16,18; 1.0->18,20,22,24. Berlin ARDS severity by P/F: mild 200-300, moderate 100-200, severe <100 (JAMA 2012;307:2526).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 136-180 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-049
- Related rules: RULE-VENTILACAO-005, RULE-VENTILACAO-006, RULE-VENTILACAO-017

## Notes

ARDSnet-style FiO2xPEEP table (moderate hypoxemia). An unused peep_old_table (previous-version single expected PEEP per FiO2) is also defined here - captured separately as RULE-VENTILACAO-006. Test test_trilha_ventilacao.py:63-73 (fio2=1,po2=152,peep=4 -> key "0.0", 4 not in [5], ratio in (151,300) -> True).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
