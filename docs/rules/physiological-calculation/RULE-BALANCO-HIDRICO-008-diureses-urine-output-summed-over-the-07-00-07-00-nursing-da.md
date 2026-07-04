# RULE-BALANCO-HIDRICO-008 — Diureses (urine output) summed over the 07:00-07:00 nursing day

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Sum of urine-output quantities (Saida with tipo in {diurese_espontanea, diurese_sonda}) for an attendance over the 07:00-07:00 nursing day, using the same two-queryset window construction as evacuacoes.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| horario_ref | — | — | — |
| nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| total_diurese | volume mL (Saida.quantidade) | — |

## Logic
```text
diureses = ("diurese_espontanea", "diurese_sonda")
filter tipo__in = diureses, balanco.nr_atendimento == nr_atendimento
if horario_ref.hour < 7:
    qs1 = Saida day==(ref-2d).day AND hour>=7
    qs2 = Saida day==(ref-1d).day AND hour<=7
else:
    qs1 = Saida day==(ref-1d).day AND hour>=7
    qs2 = Saida (criado_em==horario_ref) AND hour<7
combine s1,s2 with the same null-aware add: s1+s2 / s1 / s2 / None
```

## Edge cases (as implemented)
Same defects as RULE-...-001: __day ignores month; else-branch qs2 unsatisfiable; 0 treated as None; None when empty.

## Divergence
Same window defect as RULE-BALANCO-HIDRICO-006. Diureses filter tipo__in (diurese_espontanea, diurese_sonda); 0-sum treated as None; None when empty.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Urine output ("diureses") summed over 24h; accurate urine-output quantitation underpins the KDIGO 2012 AKI oliguria criterion (urine output <0.5 mL/kg/h). KDIGO Clinical Practice Guideline for Acute Kidney Injury, Kidney Int Suppl 2012;2(1). The tipo filter {diurese_espontanea, diurese_sonda} correctly restricts to urine. No scored calculator here. (https://kdigo.org/wp-content/uploads/2016/10/KDIGO-2012-AKI-Guideline-English.pdf)
- Test vectors: 2/3 match
- tipo filter and unit are correct; discrepancy is the window (D1/D2/D4) and 0->None (D3). D2 drops the 00:00-07:00 urine, systematically UNDER-reporting 24h diuresis by up to the night-shift tail; under-counted urine output could spuriously suggest oliguria/AKI (KDIGO), while D1 month aliasing could over-count. Urine output is a primary AKI/volume signal -> moderate.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 68-104 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-002
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-007, RULE-BALANCO-HIDRICO-009, RULE-BALANCO-HIDRICO-010, RULE-BALANCO-HIDRICO-011, RULE-BALANCO-HIDRICO-012

## Notes
DISCREPANCY inherited from shared window helper. Diurese type enum (diurese_espontanea, diurese_sonda) is defined on the Saida model (different partition); referenced here.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
