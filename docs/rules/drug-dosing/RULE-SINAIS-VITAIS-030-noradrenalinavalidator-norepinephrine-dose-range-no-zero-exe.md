# RULE-SINAIS-VITAIS-030 — NoradrenalinaValidator — norepinephrine dose range, no zero exemption

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | validation |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Noradrenaline dosing value/quantity must be between 0 and 200 inclusive. Defined in validators.py and applied on the Noradrenalina model.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| noradrenalina/quantidade | float | ml (unit not stated in validator) | 0-200 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= noradrenalina <= 200): RAISE ValidationError(f"{noradrenalina} deve estar entre 0 e 200")
```

## Edge cases (as implemented)
No zero exemption; 201 -> error. Test test_limites_parametros.py:118-125.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Norepinephrine (noradrenaline) IV infusion (Levophed label; Drugs.com; Surviving Sepsis Campaign 2021). Usual 0.05-0.4 mcg/kg/min (or 2-4 mcg/min flat); practical high-dose ~0.5-1 mcg/kg/min (~35-70 mcg/min); rates up to 3.3 mcg/kg/min reported.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 325-338 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/noradrenalina.py` | 16 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-027, RULE-val-BE-10-094

## Notes
SOFA cardiovascular tiers noradrenaline dose at >10 (within 0-200). get_microindicadores (utils/micro_indicadores.py) maps a generic vasoactive-drug flag (DVA) to a key literally named 'noradrenalina' — separate semantic ambiguity tracked as RULE-indic-BE-11-050 (out of cluster).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
