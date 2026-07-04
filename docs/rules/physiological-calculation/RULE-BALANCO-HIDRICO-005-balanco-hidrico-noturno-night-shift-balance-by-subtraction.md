# RULE-BALANCO-HIDRICO-005 — Balanco Hidrico noturno (night-shift balance by subtraction)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Night-shift fluid balance = stored 24h balance minus computed day-shift balance.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| self.balanco_24h | — | mL | — |
| balanco_diurno | — | mL | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| balanco_noturno | — | mL |

## Logic
```text
return self.balanco_24h - self.balanco_diurno
```

## Edge cases (as implemented)
Uses the persisted balanco_24h field (default 0), NOT (ganhos - perdas). If balanco_24h is stale/unset (0), noturno = -diurno.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference defines a fluid-balance 'night shift' value as (24h balance - day-shift balance). The additive decomposition day+night = 24h is arithmetically valid, but the 07:00-19:00 / 19:00-07:00 shift split is an institutional convention (see RULE-004). Concept traces to ADQI/Malbrain daily fluid-balance accounting. (https://pmc.ncbi.nlm.nih.gov/articles/PMC10133509/)
- Test vectors: 2/3 match
- The subtraction identity (night = 24h - day) is arithmetically sound and there is no published
clinical reference for the 19:00-07:00 night-shift construct, so verdict is UNVERIFIABLE (internal
business rule), flagged for internal review. IMPORTANT internal-consistency caveat (documented, not a
reference discrepancy): noturno derives from the PERSISTED balanco_24h FloatField (default 0,
maintained incrementally by RULE-014/015 accruals), NOT from (ganhos - perdas) nor from a windowed
19:00-07:00 recompute. balanco_diurno meanwhile is computed from criado_em__range. These two use
DIFFERENT sources, so if balanco_24h is stale, unset (0), or diverges from the window-based diurno,
noturno can be wrong or negative - test vector 2 shows an unset balanco_24h yielding noturno = -diurno.
Same accumulator-drift surface flagged in RULE-014/015 (no decrement on edit/delete). If internal
review scopes balanco_24h reliability out, the arithmetic itself is correct. Confirmed at balanco.py:119-121.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/balanco_hidrico/balanco.py | 119-121 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-005
- Related rules: RULE-BALANCO-HIDRICO-004, RULE-BALANCO-HIDRICO-006

## Notes
balanco_24h is a stored FloatField (default 0), populated elsewhere (likely serializer/util, out of partition).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
