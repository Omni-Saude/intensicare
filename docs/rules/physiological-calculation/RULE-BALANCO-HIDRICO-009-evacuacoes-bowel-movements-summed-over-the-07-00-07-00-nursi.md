# RULE-BALANCO-HIDRICO-009 — Evacuacoes (bowel movements) summed over the 07:00-07:00 nursing day

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Total number/quantity of bowel-movement outputs (Saida with tipo="evacuacao") for a given attendance over the 24h "nursing day" that runs 07:00 to 07:00. The window is assembled from two day-of-month filtered querysets whose composition depends on whether the reference time is before or after 07:00.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| horario_ref | — | — | — |
| nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| total_evacuacoes | count/volume (Saida.quantidade) | — |

## Logic
```text
diurese_types irrelevant; filter tipo == "evacuacao", balanco.nr_atendimento == nr_atendimento.
if horario_ref.hour < 7:
    qs1 = Saida where criado_em.day == (horario_ref - 2 days).day  AND criado_em.hour >= 7
    qs2 = Saida where criado_em.day == (horario_ref - 1 day).day   AND criado_em.hour <= 7
else:
    qs1 = Saida where criado_em.day == (horario_ref - 1 day).day   AND criado_em.hour >= 7
    qs2 = Saida where criado_em == horario_ref (EXACT datetime eq)  AND criado_em.hour < 7
s1 = Sum(qs1.quantidade); s2 = Sum(qs2.quantidade)
if s1 and s2: return s1 + s2
elif s1 and not s2: return s1
elif not s1 and s2: return s2
else: return None
```

## Edge cases (as implemented)
Uses criado_em__day (day-of-month ONLY, ignores month/year) so results are wrong across month boundaries. Boundary hour 7 is included by BOTH qs (>=7 and <=7). Zero sums are falsy so a genuine total of 0 is treated like None. In the else (hour>=7) branch, qs2's predicate 'criado_em == horario_ref AND hour < 7' can never be satisfied (horario_ref.hour>=7), so qs2 is always empty and only day D-1 07:00-23:59 is counted (00:00-07:00 of the current day is dropped). Returns None (not 0) when no records.

## Divergence
Same window defect as RULE-BALANCO-HIDRICO-006. Evacuacoes filter tipo=='evacuacao'; boundary hour 7 included by BOTH querysets (>=7 and <=7); 0-sum treated as None.

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: Bowel-movement ("evacuacoes") output summed over the 24h nursing day - a definitional count/volume aggregation with no published scored calculator, coefficients, or cutoffs. tipo filter == "evacuacao". General nursing intake/output charting standard (StatPearls, Fluid Balance / Intake and Output). (https://www.ncbi.nlm.nih.gov/books/NBK549784/)
- Test vectors: 1/3 match
- tipo filter correct; same window defects (D1/D2/D4) and 0->None (D3). Bowel-movement totals are largely qualitative/monitoring and not a resuscitation-critical number, so the same window loss carries low clinical impact relative to urine/fluid balance.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 30-65 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-001
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-007, RULE-BALANCO-HIDRICO-008, RULE-BALANCO-HIDRICO-010, RULE-BALANCO-HIDRICO-011, RULE-BALANCO-HIDRICO-012

## Notes
DISCREPANCY: (1) __day matches day-of-month regardless of month; (2) else-branch qs2 uses exact datetime equality 'criado_em=horario_ref' AND hour<7, which is unsatisfiable and silently drops the post-midnight portion of the shift. Same two defects recur verbatim in RULE-...-002/003/004/005/006. Recorded as implemented, not corrected.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
