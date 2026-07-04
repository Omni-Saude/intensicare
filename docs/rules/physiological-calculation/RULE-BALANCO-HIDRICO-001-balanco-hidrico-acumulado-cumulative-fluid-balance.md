# RULE-BALANCO-HIDRICO-001 — Balanco Hidrico acumulado (cumulative fluid balance)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Cumulative fluid balance across ALL BalancoHidrico days for the same bed and admission = total non-deleted intake minus total non-deleted output.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| entradas.quantidade | — | mL | all days, deletado_em is null |
| saidas.quantidade | — | mL | all days, deletado_em is null |

## Outputs
| Name | Type | Unit |
|---|---|---|
| balanco_acumulado | — | mL |

## Logic
```text
entradas = 0; saidas = 0
for balanco in BalancoHidrico.objects.filter(leito=self.leito, nr_atendimento=self.leito.nr_atendimento):
    entradas_qs = balanco.entradas.filter(deletado_em__isnull=True)
    saidas_qs   = balanco.saidas.filter(deletado_em__isnull=True)
    if entradas_qs.exists(): entradas += entradas_qs.aggregate(total=Sum("quantidade")).get("total", 0)
    if saidas_qs.exists():   saidas   += saidas_qs.aggregate(total=Sum("quantidade")).get("total", 0)
return entradas - saidas
```

## Edge cases (as implemented)
Filters on self.leito.nr_atendimento (the bed's current admission), NOT self.nr_atendimento (the balance row's) - if a bed is reused across admissions these may diverge. Sum over an existing queryset whose quantidade are all null returns None, and .get("total", 0) returns that None (default 0 not used) -> `entradas += None` raises TypeError; quantidade defaults 0 mitigates.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Malbrain MLNG, Marik PE, Witters I, et al. Fluid overload, de-resuscitation, and outcomes in critically ill or injured patients (ADQI/IFAD). Anaesthesiol Intensive Ther 2014; Bouchard J et al. Kidney Int 2009. Standard definition: (cumulative) fluid balance = total fluid intake - total fluid output; cumulative balance = sum of daily balances since admission. (https://pmc.ncbi.nlm.nih.gov/articles/PMC10133509/)
- Test vectors: 3/3 match
- Core equation (cumulative intake - cumulative output) matches the ADQI/Malbrain standard definition
of cumulative fluid balance. The two catalog caveats are code-robustness issues, NOT reference
discrepancies: (a) filters on self.leito.nr_atendimento rather than self.nr_atendimento (bed reuse
across admissions could mix data - a scoping bug); (b) Sum over an all-null-quantidade queryset
returns None and .get('total',0) yields that None -> `entradas += None` TypeError, mitigated only by
quantidade defaulting to 0. Neither alters the arithmetic when data is present. Uses ALL non-deleted
entradas/saidas (no tipo filter), correct for a gross intake/output balance. Legacy source confirmed
at balanco.py:32-59.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/balanco_hidrico/balanco.py | 32-59 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-001
- Related rules: RULE-BALANCO-HIDRICO-002, RULE-BALANCO-HIDRICO-003, RULE-BALANCO-HIDRICO-004, RULE-BALANCO-HIDRICO-005, RULE-BALANCO-HIDRICO-006

## Notes
Only excludes soft-deleted (deletado_em) rows. TODO in source notes a planned single-query refactor.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
