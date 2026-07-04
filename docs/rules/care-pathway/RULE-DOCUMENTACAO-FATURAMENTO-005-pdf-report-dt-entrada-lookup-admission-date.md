# RULE-DOCUMENTACAO-FATURAMENTO-005 — PDF report dt_entrada lookup (admission date)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
The admission date/time (dt_entrada) shown on the balanco hidrico PDF is taken from the first MicroIndicadores record matching the encounter number, or null if none exists.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| balanco.nr_atendimento | string/integer |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| dt_entrada | datetime or null |  |

## Logic
```text
dt_entrada = (MicroIndicadores.objects.filter(NR_ATENDIMENTO=balanco.nr_atendimento).first().DT_ENTRADA
              if MicroIndicadores.objects.filter(NR_ATENDIMENTO=balanco.nr_atendimento).exists()
              else None)
```

## Edge cases (as implemented)
Performs the same filter query twice (existence check then first()); functionally safe but redundant.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/pdf_balanco_hidrico.py | 55-63 | 8166c07e | primary |
- Merged from: RULE-pdf-BE-08-037
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-004, RULE-DOCUMENTACAO-FATURAMENTO-023

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
