# RULE-VENTILACAO-011 — Ventilation C8 - extubation-readiness bundle

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: high |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Flags a full readiness bundle - awake, >1d VM, low PEEP/FiO2, adequate FR and oxygenation, no noradrenaline. Hard alert-forcing criterion.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| glasgow (int) | | | |
| rass (str enum) | | | |
| dias_vm (int) | | | |
| peep | | | |
| fio2 (fraction, uses <0.4) | | | |
| fr (int) | | | |
| relacao_po2_fio2 | | | |
| noradrenalina_exists (bool) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_8 (bool) | | |

## Logic

```text
all([
  any([(glasgow>=10) if glasgow else False, (int(rass)>=-2) if rass else False]),
  (dias_com_ventilacao_mecanica > 1) if VM exists else False,
  (peep <= 8) if peep else False,
  (fio2 < 0.4) if fio2 else False,
  (fr <= 22) if fr else False,
  (relacao_po2_fio2 >= 200) if (po2 and fio2) else False,
  not verificar_objeto_existe(dp,'noradrenalina') ])
```

## Edge cases (as implemented)

fio2 < 0.4 treats FiO2 as a fraction here (contrast C2/C3 which divide fio2 by 100 as a percentage). Inclusive peep<=8, fr<=22, ratio>=200; strict glasgow>=10; dias_vm>1.

## Divergence

FiO2 treated as a FRACTION here (fio2 < 0.4), contrasting C2/C3 (RULE-VENTILACAO-004/005) which divide fio2 by 100 as a PERCENTAGE - FiO2 unit inconsistency within the same model.

## Verification

- Verdict: DISCREPANCY (clinical impact: high)
- Reference: Boles J-M, et al. "Weaning from mechanical ventilation." ERS/ATS/ESICM/SCCM/SRLF Task Force. Eur Respir J 2007;29:1033-1056 (International Consensus Conference on weaning). Readiness-to-wean/SBT screening: adequate oxygenation = SpO2 >=90% on FiO2 <=0.40 and PEEP <=8 cmH2O, OR PaO2/FiO2 >=150 (PEEP <=8); some protocols use P/F >200. Adequate consciousness, RR criterion, no/minimal vasopressors.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 285-313 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-055
- Related rules: RULE-VENTILACAO-014, RULE-VENTILACAO-002, RULE-VENTILACAO-017, RULE-VENTILACAO-004, RULE-VENTILACAO-005

## Notes

Alert-forcing criterion (RULE-VENTILACAO-014). SBT/extubation-readiness anchors. Verified verbatim against source. Test test_trilha_ventilacao.py:178-200 (removing noradrenaline flips to True).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
