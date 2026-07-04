# RULE-BALANCO-HIDRICO-006 — 24h fluid balance = intake minus output over the 07:00-07:00 nursing day

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Net fluid balance (balanco hidrico) for an attendance over the 07:00-07:00 nursing day, computed as total Entrada intake minus total Saida output. Unlike the other helpers, missing sums default to 0 (not None), so this always returns a number.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| horario_ref | — | — | — |
| nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| balanco_24h | volume mL (can be negative) | — |

## Logic
```text
if horario_ref.hour < 7:
    entrada_qs1 = Entrada day==(ref-2d).day AND hour>=7
    entrada_qs2 = Entrada day==(ref-1d).day AND hour<=7
    saida_qs1   = Saida   day==(ref-2d).day AND hour>=7
    saida_qs2   = Saida   day==(ref-1d).day AND hour<=7
else:
    entrada_qs1 = Entrada day==(ref-1d).day AND hour>=7
    entrada_qs2 = Entrada (criado_em==horario_ref) AND hour<7
    saida_qs1   = Saida   day==(ref-1d).day AND hour>=7
    saida_qs2   = Saida   (criado_em==horario_ref) AND hour<7
saidas   = null-aware(s1,s2) else 0
entradas = null-aware(e1,e2) else 0
return entradas - saidas
```

## Edge cases (as implemented)
Same window defects as RULE-...-001 (month-agnostic __day; else-branch qs2 unsatisfiable). Here empty sums fall back to 0, so the return is always numeric (never None). Note Saida here applies NO tipo filter (all outputs), unlike diureses/evacuacoes.

## Divergence
Window construction defect (shared across BE-09 helpers): criado_em__day matches day-of-month ONLY (wrong across month boundaries). In the hour>=7 branch qs2 predicate `criado_em == horario_ref AND hour < 7` is unsatisfiable, silently dropping 00:00-07:00 of the current day. Unlike the sibling helpers, empty sums fall back to 0, so this always returns a number (never None). Applies NO tipo filter on Saida (all outputs).

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Cumulative/24h fluid balance = total intake - total output is the standard critical-care definition (Malbrain MLNG et al., "Principles of fluid management and stewardship in septic shock", Ann Intensive Care 2018;8:66; LITFL Critical Care Compendium - Fluid Balance). The 07:00-07:00 nursing-day (turno das 7h as 7h) is an institutional nursing convention, not a guideline equation. No scored calculator / coefficients exist. (https://annalsofintensivecare.springeropen.com/articles/10.1186/s13613-018-0402-x)
- Test vectors: 1/3 match
- Equation and units match the standard definition; the discrepancy is purely the temporal window. D2 systematically drops the 00:00-07:00 night-shift tail (~7h) of both intake and output when the form is generated during day shift (hour>=7); net balance error = (intake-output) of the dropped segment (can be either sign). D1 can grossly mis-window across month boundaries. Empty sums fall back to 0 here (not None), so it always returns a number. Fluid balance drives fluid-management/resuscitation and de-resuscitation decisions -> moderate.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 212-276 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-006
- Related rules: RULE-BALANCO-HIDRICO-005, RULE-BALANCO-HIDRICO-007, RULE-BALANCO-HIDRICO-008, RULE-BALANCO-HIDRICO-009, RULE-BALANCO-HIDRICO-010, RULE-BALANCO-HIDRICO-011, RULE-BALANCO-HIDRICO-012, RULE-BALANCO-HIDRICO-014, RULE-BALANCO-HIDRICO-015, RULE-BALANCO-HIDRICO-027

## Notes
DISCREPANCY inherited from shared window helper. balanco = entradas - saidas.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
