# RULE-VENTILACAO-008 — Ventilation C5 - prolonged intubation (>10 days TOT)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | threshold |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Flags more than 10 days of mechanical ventilation via orotracheal tube (dispositivo == "tot").

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dias_vm (days) | | | |
| dispositivo (str) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_5 (bool) | | |

## Logic

```text
if verificar_objeto_existe(dp,'ventilacao_mecanica'):
  return all([ dias_com_ventilacao_mecanica > 10, dispositivo == "tot" ])
return False
```

## Edge cases (as implemented)

Strict >10 days. Requires VM object. Test 10d->False, 11d->True (with dispositivo tot).

## Verification

- Verdict: VERIFIED (clinical impact: none)
- Reference: Contemporary tracheostomy-timing evidence (post-TracMan reassessment, JALH 2025): reasonable to wait >=10 days to confirm ongoing ventilation need before tracheostomy; RespCare tracheostomy review

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 246-255 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-052
- Related rules: RULE-VENTILACAO-009, RULE-VENTILACAO-017, RULE-VENTILACAO-002, RULE-VENTILACAO-025

## Notes

dispositivo "tot" is a valid device choice (lowercase). Tracheostomy-timing anchor (~10-14d). Test test_trilha_ventilacao.py:133-146.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
