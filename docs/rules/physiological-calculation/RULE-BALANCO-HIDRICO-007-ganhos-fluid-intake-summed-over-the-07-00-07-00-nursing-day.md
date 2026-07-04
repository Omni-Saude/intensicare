# RULE-BALANCO-HIDRICO-007 — Ganhos (fluid intake) summed over the 07:00-07:00 nursing day

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Sum of all fluid-intake quantities (Entrada.quantidade, no type filter) for an attendance over the 07:00-07:00 nursing day.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| horario_ref | — | — | — |
| nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| total_ganhos | volume mL (Entrada.quantidade) | — |

## Logic
```text
if horario_ref.hour < 7:
    qs1 = Entrada day==(ref-2d).day AND hour>=7
    qs2 = Entrada day==(ref-1d).day AND hour<=7
else:
    qs1 = Entrada day==(ref-1d).day AND hour>=7
    qs2 = Entrada (criado_em==horario_ref) AND hour<7
s1=Sum(qs1.quantidade); s2=Sum(qs2.quantidade)
return s1+s2 / s1 / s2 / None   (null-aware, 0 falsy)
```

## Edge cases (as implemented)
Same defects as RULE-...-001 (month-agnostic __day; unsatisfiable else qs2; 0->None).

## Divergence
Same 07:00-07:00 window defect as RULE-BALANCO-HIDRICO-006: month-agnostic __day; else-branch qs2 unsatisfiable; 0-sum coerced to None. Ganhos = Sum(Entrada.quantidade) with no tipo filter.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Total fluid intake ("ganhos") over the 24h nursing day is a definitional sum of intake volumes; the intake/output ledger is standard critical-care fluid accounting (Malbrain et al., Ann Intensive Care 2018;8:66). No scored calculator / coefficients / cutoffs. (https://annalsofintensivecare.springeropen.com/articles/10.1186/s13613-018-0402-x)
- Test vectors: 0/3 match
- Sum form and unit (mL) match the definitional quantity; discrepancy is the window (D1/D2/D4) plus 0->None (D3). D2 under-reports intake by the dropped 00:00-07:00 tail. Understated intake on a fluid-balance/evolution display can mislead volume assessment -> moderate.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 107-138 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-003
- Related rules: RULE-BALANCO-HIDRICO-003, RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-008, RULE-BALANCO-HIDRICO-009, RULE-BALANCO-HIDRICO-010, RULE-BALANCO-HIDRICO-011, RULE-BALANCO-HIDRICO-012

## Notes
DISCREPANCY inherited from shared window helper.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
