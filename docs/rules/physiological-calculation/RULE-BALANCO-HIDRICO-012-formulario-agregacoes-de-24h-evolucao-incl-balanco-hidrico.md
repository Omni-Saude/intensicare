# RULE-BALANCO-HIDRICO-012 — Formulario - agregacoes de 24h (evolucao) incl. balanco hidrico

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | balanco-hidrico |

## Rule
Evolution form exposes last-24h rollups - evacuations, diuresis, gains, max temperature, max HGT and 24h fluid balance - referenced to the form's creation time; the active implementations delegate to helper functions.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| self.criado_em | reference time | — | — |
| self.nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| evacuacoes_ultimo_dia / diurese_ultimo_dia / ganhos_ultimo_dia / temperatura_max_ultimo_dia / hgt_ultimo_dia / balanco_ultimo_dia | — | mL / Celsius / mg-dL |

## Logic
```text
evacuacoes_ultimo_dia   = evacuacoes_24h_evo(criado_em.astimezone(), nr_atendimento)
diurese_ultimo_dia      = diureses_24h_evo(criado_em.astimezone(), nr_atendimento)
ganhos_ultimo_dia       = ganhos_24h_evo(criado_em.astimezone(), nr_atendimento)
temperatura_max_ultimo_dia = temperatura_24h_evo(criado_em.astimezone(), nr_atendimento)
hgt_ultimo_dia          = hgt_24h_evo(criado_em.astimezone(), nr_atendimento)
balanco_ultimo_dia      = balanco_24h_evo(criado_em.astimezone(), nr_atendimento)
# Superseded inline formula (commented, lines 242-258) documenting intended 24h fluid balance:
#   vomitos_24h = Sum(Saida.quantidade where tipo="vomito_retorno_sonda", criado_em in [ref-1d, ref])
#   balanco_24h = (ganhos_24h or 0) - ((diurese_24h or 0) + (vomitos_24h or 0))  or None
#   where diurese_24h sums tipo in ("diurese_espontanea","diurese_sonda") over [ref-1d, ref]
```

## Edge cases (as implemented)
24h window = [criado_em - 1 day, criado_em] per the commented reference implementation. The intended balance formula SUBTRACTS diuresis + vomit/tube-return from gains (it does NOT subtract all outputs, only diuresis and vomit).

## Verification
- Verdict: UNVERIFIABLE
- Reference: Standard nursing/ICU fluid-balance definition: Fluid Balance = total intake - total output, where output includes urine, stool, emesis, blood loss, and wound/chest-tube drainage; positive balance = intake exceeds output. Nurseslabs, "Monitoring Fluid Intake and Output (I&O)". (https://nurseslabs.com/monitoring-fluid-intake-and-output-io/)
- Test vectors: 1/3 match
- AMBIGUOUS from extraction, and UNVERIFIABLE here because the ACTIVE 24h fluid-balance computation delegates to trilha_homecare.utils (balanco_24h_evo / ganhos_24h_evo / diureses_24h_evo / temperatura_24h_evo / hgt_24h_evo / evacuacoes_24h_evo) — OUTSIDE this rule's partition — so the exact live formula cannot be confirmed from the sources cited here. Two divergent candidates exist: (a) the ACTIVE delegate balanco_24h_evo (RULE-BALANCO-HIDRICO-006) computes entradas - ALL saidas, which is directionally consistent with the textbook all-ins-minus-all-outs definition but carries the shared 07:00-07:00 window defect; (b) the COMMENTED/superseded inline formula subtracts only diuresis + vomit/tube-return, which UNDERcounts output (omits stool, wound/chest-tube drainage, blood loss) and therefore overestimates a positive balance. Flag for internal review: confirm which formula is live and whether omitting non-urine/non-vomit outputs is intended.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/formularios/formulario.py | 147-262 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-008
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-007, RULE-BALANCO-HIDRICO-008, RULE-BALANCO-HIDRICO-009, RULE-BALANCO-HIDRICO-010, RULE-BALANCO-HIDRICO-011, RULE-BALANCO-HIDRICO-028

## Notes
AMBIGUOUS because the ACTIVE computation lives in trilha_homecare.utils (evacuacoes_24h_evo, diureses_24h_evo, ganhos_24h_evo, temperatura_24h_evo, hgt_24h_evo, balanco_24h_evo) - OUTSIDE this partition; a verifier must open trilha_homecare/utils.py to confirm the exact 24h fluid-balance formula. The commented-out inline versions (lines 147-258) are recorded here as the documented intent. Note this 24h balance definition (gains - (diuresis + vomit)) differs from the entrada/saida-based RULE-balanco-BE-06-001..005.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
