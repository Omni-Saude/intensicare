# RULE-BALANCO-HIDRICO-016 — tempo_criacao - horas desde a criacao (shared helper)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Hours elapsed since a record (Entrada/Saida/SinaisVitais) was created, used as the recency window guard in sepsis criteria.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| self.criado_em | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| tempo_criacao | — | hours |

## Logic
```text
return (timezone.now().astimezone() - self.criado_em.astimezone()).seconds / 3600
```

## Edge cases (as implemented)
Uses timedelta.seconds (the seconds-within-a-day component, 0..86399), NOT total_seconds(). For any record older than 24h the day component is dropped, so the result is always in [0, 24) and wraps daily. This makes sepsis "<= 24" window guards effectively always-true and the "<= 12" guard (criterio_9) and criterio_6 "< 2h" recency unreliable.

## Divergence
Uses timedelta.seconds (the seconds-within-a-day component, 0..86399) instead of total_seconds(); for any record older than 24h the day component is dropped, so the result wraps into [0,24). This makes the sepsis recency window guards (<=24, the <=12 in criterio_9, and criterio_6 <2h) unreliable. Byte-identical defect triplicated in models/balanco_hidrico/entradas.py:66-68 and saidas.py:73-75; consumed by RULE-sepse-BE-06-001/003/005/008/009 and inline in criterio_6.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Python Software Foundation. datetime.timedelta — total_seconds() vs. the .seconds attribute (seconds-within-a-day only, 0..86399). Python 3 Standard Library documentation. (https://docs.python.org/3/library/datetime.html#datetime.timedelta.total_seconds)
- Test vectors: 2/4 match
- Confirms the DISCREPANCY carried from extraction. Defect is timedelta.seconds (seconds-within-a-day, 0..86399)
used instead of total_seconds(). Verified against Python runtime semantics: for any age >= 24h the whole-day
component is discarded, so the function returns age mod 24h. Byte-identical defect triplicated in
models/balanco_hidrico/sinais_vitais.py:110-113, entradas.py:66-68, saidas.py:73-75. Consumed by sepse
criterio recency gating and inline in criterio_6. Not a clinical-scale rule; the authoritative reference is the
language runtime contract that the legacy code violates.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/balanco_hidrico/sinais_vitais.py | 110-113 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-006
- Related rules: RULE-BALANCO-HIDRICO-017

## Notes
DISCREPANCY: should use .total_seconds() for a true elapsed-hours value. Identical implementation duplicated in entradas.py (lines 66-68) and saidas.py (lines 73-75). Consumed by RULE-sepse-BE-06-001/003/005/008/009 and (via inline seconds/3600) criterio_6.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
