# RULE-VENTILACAO-009 — Ventilation C6 - prolonged intubation with COVID-19

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Flags TOT ventilation > 10 days AND COVID-19 diagnosis.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dispositivo (str) | | | |
| dias_vm (days) | | | |
| covid_19 (bool) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_6 (bool) | | |

## Logic

```text
if verificar_objeto_existe(dp,'ventilacao_mecanica'):
  return all([ dispositivo == "tot", dias_com_ventilacao_mecanica > 10, covid_19 ])
return False
```

## Edge cases (as implemented)

Strict >10. Requires VM + covid flag. Test 15d tot + covid -> True.

## Divergence

Current code uses dias_vm > 10. _REGRAS text says ">10 dias TOT E COVID" but _ANTIGAS_REGRAS C5 said ">14 dias". The automatica facade (RULE-VENTILACAO-017 criterio_6) states ">14 dias" for COVID trach. Variant divergence: trilha_manual code >10 vs facade text >14.

## Verification

- Verdict: DISCREPANCY (clinical impact: moderate)
- Reference: AAO-HNS and international multidisciplinary COVID-19 tracheostomy guidelines (2020): defer tracheostomy until >=14 days of intubation (often 2-3 weeks) given aerosol/viral-load risk; systematic review Br J Anaesth / Otolaryngol HNS

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 257-267 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-053
- Related rules: RULE-VENTILACAO-008, RULE-VENTILACAO-017, RULE-VENTILACAO-002

## Notes

Test test_trilha_ventilacao.py:148-160.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
