# RULE-INDICADORES-ETL-026 — Micro-indicadores icon/value display rule

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
On a bed card's micro-indicators strip, the noradrenalina, ventilação mecânica, sedação, and hemodiálise icons are shown when their respective boolean-like field is truthy; tempo de internação (shown as "Xd") and mortalidade esperada (shown as "X%") are shown only when their value's type is "number".

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| indicadores.noradrenalina | boolean \| undefined |  |  |
| indicadores.ventilacao_mecanica | boolean \| undefined |  |  |
| indicadores.sedacao | boolean \| undefined |  |  |
| indicadores.hemodialise | boolean \| undefined |  |  |
| indicadores.tempo_internacao | number \| undefined | days |  |
| indicadores.mortalidade_esperada | number \| undefined | % |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| iconVisible | boolean |  |

## Logic
```text
show(noradrenalina|ventilacao_mecanica|sedacao|hemodialise) = !!field
show(tempo_internacao) = typeof tempo_internacao === "number"   // rendered as `${value}d`
show(mortalidade_esperada) = typeof mortalidade_esperada === "number"  // rendered as `${value}%`
```

## Edge cases (as implemented)
tempo_internacao/mortalidade_esperada of exactly 0 are shown (typeof check), unlike the four boolean-style indicators which would hide on a falsy 0/empty value.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/MicroIndicadores/MicroIndicadores.tsx` | 18-88 | `f9656be2` | primary |

- Merged from: RULE-indicadores-FE-06-020
- Related rules: RULE-INDICADORES-ETL-024, RULE-INDICADORES-ETL-025, RULE-INDICADORES-ETL-022, RULE-INDICADORES-ETL-012

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
