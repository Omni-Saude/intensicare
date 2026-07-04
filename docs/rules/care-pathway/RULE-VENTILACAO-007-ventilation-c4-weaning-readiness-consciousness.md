# RULE-VENTILACAO-007 — Ventilation C4 - weaning readiness / consciousness

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Flags (long VM with good oxygenation on controlled mode without sedation) OR RASS>=-2 OR Glasgow>8.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dias_vm (days) | | | |
| dispositivo (str) | | | |
| sedativos_present (bool) | | | |
| relacao_po2_fio2 | | | |
| rass (str enum) | | | |
| glasgow (int) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_4 (bool) | | |

## Logic

```text
any([
  all([ dias_com_ventilacao_mecanica > 7,
        buscar_dispositivo_ventilacao_mecanica() == "PCV" or == "VCV",
        not sedatives_exist,
        relacao_po2_fio2 > 250 ]),
  (int(rass) >= -2) if rass else False,
  (glasgow > 8) if glasgow else False ])
```

## Edge cases (as implemented)

RASS parsed via int() of the choice string ('-2'->-2). Any one disjunct suffices. glasgow strict >8.

## Divergence

Controlled-mode test compares buscar_dispositivo_ventilacao_mecanica() (VentilacaoMecanica.dispositivo, valid choices tot/tqt/dni) against "PCV"/"VCV", which are MODALIDADE values (choices psv/vcv/pcv, lowercase). In production the device-path is effectively unreachable; the test only passes it by manually setting dispositivo="PCV" (uppercase). See enum rule RULE-VENTILACAO-025.

## Verification

- Verdict: DISCREPANCY (clinical impact: low)
- Reference: Richmond Agitation-Sedation Scale (Sessler 2002, AJRCCM), range -5..+4; Glasgow Coma Scale (Teasdale 1974), GCS<=8 = coma / airway-protection threshold; MDCalc RASS

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 225-244 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-051
- Related rules: RULE-VENTILACAO-014, RULE-VENTILACAO-025, RULE-VENTILACAO-002, RULE-VENTILACAO-017

## Notes

Test test_trilha_ventilacao.py:107-131. RASS/Glasgow are published anchors.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
