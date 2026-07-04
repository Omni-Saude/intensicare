# RULE-VENTILACAO-013 — Ventilation C10 - adequate oxygenation (incl. COPD target)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Flags SatO2>96 OR PO2>100 OR (COPD AND SatO2>92).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| sato2 (percent) | | | |
| po2 (mmHg) | | | |
| dpoc (bool) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_10 (bool) | | |

## Logic

```text
any([
  (sato2 > 96) if sato2 else False,
  (po2 > 100) if po2 else False,
  all([ dpoc, (sato2 > 92) if sato2 else False ]) ])
```

## Edge cases (as implemented)

Strict >96, >100, >92. COPD lowers the SpO2 target to >92.

## Verification

- Verdict: VERIFIED (clinical impact: none)
- Reference: O'Driscoll BR, et al. BTS Guideline for oxygen use in adults in healthcare and emergency settings. Thorax 2017;72(Suppl 1):ii1-ii90. Target SpO2 94-98% for most acutely ill adults (avoid hyperoxia); 88-92% for patients at risk of hypercapnic respiratory failure (e.g. COPD). PaO2 hyperoxia above the normal 80-100 mmHg range.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 328-344 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-057
- Related rules: RULE-VENTILACAO-017

## Notes

Oxygenation-target anchors (SpO2, COPD 88-92 band). Verified verbatim against source. Test test_trilha_ventilacao.py:221-228.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
