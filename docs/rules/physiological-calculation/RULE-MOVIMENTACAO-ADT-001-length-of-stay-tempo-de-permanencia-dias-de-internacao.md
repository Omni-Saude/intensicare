# RULE-MOVIMENTACAO-ADT-001 — Length-of-stay (tempo de permanencia / dias de internacao)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Days elapsed since admission (data_entrada) used as tempo_permanencia and dias de internacao.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| data_entrada | datetime |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| dias | integer, days |  |

## Logic
```text
tempo_permanencia = diferenca_dias(self.data_entrada.date())
  where diferenca_dias(entrada) = (timezone.now().date() - entrada).days
buscar_dias_internacao = diferenca_dias(data_entrada.date()) if data_entrada else 0
```

## Edge cases (as implemented)
Uses .date() so partial days are truncated (whole-day difference). No data_entrada => tempo_permanencia raises AttributeError (only buscar_dias_internacao guards None with 0).

## Verification
- Verdict: UNVERIFIABLE
- Reference: Length-of-stay is an operational ADT metric, not a published clinical formula. No single authoritative equation exists; conventions vary (elapsed-calendar-days vs midnight-census/inclusive-day count). Legacy computes elapsed whole days: (timezone.now().date() - data_entrada.date()).days.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/movimentacao.py | 73-103 | 8166c07e | primary |
- Merged from: RULE-movimentacao-BE-04-024
- Related rules: RULE-MOVIMENTACAO-ADT-002

## Notes
diferenca_dias in utils/handlers.py:63 (out of partition). Feeds micro_indicadores.tempo_internacao (RULE-002).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
