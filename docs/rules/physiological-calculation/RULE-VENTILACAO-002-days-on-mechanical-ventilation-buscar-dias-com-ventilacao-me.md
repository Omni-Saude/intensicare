# RULE-VENTILACAO-002 — Days on mechanical ventilation (buscar_dias_com_ventilacao_mecanica)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Number of days a patient has been on mechanical ventilation; consumed by ventilation criteria C4/C5/C6/C8.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| ventilacao_mecanica.horario_inicio (datetime) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| dias (int, days) | False | | |

## Logic

```text
if hasattr(dp,'ventilacao_mecanica'):
    return abs((now - vm.horario_inicio).days)
return False
```

## Edge cases (as implemented)

Uses timedelta.days (integer day component, truncates hours). abs() so future start times still return positive. No VM object -> returns False.

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. This is an internal date-arithmetic helper (days since ventilacao_mecanica.horario_inicio) consumed by downstream ventilation criteria C4/C5/C6/C8. "Days on mechanical ventilation" is a raw duration count, not a published scale/equation/cutoff.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 199-203 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-059
- Related rules: RULE-VENTILACAO-007, RULE-VENTILACAO-008, RULE-VENTILACAO-009, RULE-VENTILACAO-011, RULE-VENTILACAO-025

## Notes

Trivial date-diff helper; flagged verify=true because type=formula, but has no published clinical anchor. horario_inicio is set on the VentilacaoMecanica object (see RULE-VENTILACAO-025).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
