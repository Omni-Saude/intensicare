# RULE-VENTILACAO-012 — Ventilation C9 - shock without ventilation

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Flags noradrenaline present AND lactate>2.5 AND no mechanical ventilation. Hard alert-forcing criterion.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| noradrenalina_exists (bool) | | | |
| lactato_arterial (mmol/L) | | | |
| ventilacao_mecanica_exists (bool) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_9 (bool) | | |

## Logic

```text
all([
  verificar_objeto_existe(dp,'noradrenalina'),
  (lactato_arterial > 2.5) if lactato_arterial else False,
  not verificar_objeto_existe(dp,'ventilacao_mecanica') ])
```

## Edge cases (as implemented)

Strict lactato>2.5 (note estabilidade/sepse use >=2.5; ventilacao uses >2.5). Adding VM flips to False.

## Verification

- Verdict: DISCREPANCY (clinical impact: low)
- Reference: Singer M, et al. "The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3)." JAMA 2016;315(8):801-810. Septic shock = vasopressor requirement to maintain MAP >=65 mmHg AND serum lactate >2 mmol/L (>18 mg/dL) despite adequate fluid resuscitation.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 315-326 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-056
- Related rules: RULE-VENTILACAO-011, RULE-VENTILACAO-014

## Notes

Alert-forcing criterion (RULE-VENTILACAO-014). Boundary differs from lactate rules elsewhere (>2.5 vs >=2.5). Lactate shock anchor. Verified verbatim against source. Test test_trilha_ventilacao.py:202-219.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
