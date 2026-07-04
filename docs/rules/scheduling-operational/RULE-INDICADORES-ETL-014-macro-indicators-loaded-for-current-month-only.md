# RULE-INDICADORES-ETL-014 — Macro indicators loaded for current month only

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
The macro-indicator ETL processes only rows whose DT_MES_ANO falls in the current server year and current server month, ordered by DT_MES_ANO, upserting one record per sector.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| DT_MES_ANO | date |  |  |
| CD_SETOR_ATENDIMENTO | identifier |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| MacroIndicadores rows | upsert |  |

## Logic
```text
year, mes = timezone.now().year, timezone.now().month
src = MacroIndicadoresTasy.filter(DT_MES_ANO__year == year, DT_MES_ANO__month == mes).order_by("DT_MES_ANO")
for obj in src:
    MacroIndicadores.update_or_create(CD_SETOR_ATENDIMENTO=obj.CD_SETOR_ATENDIMENTO, defaults=obj.__dict__)
```

## Edge cases (as implemented)
"Current" is timezone.now() (Django active timezone). Any historical month is never backfilled by this job. update_or_create key is CD_SETOR_ATENDIMENTO only, so at most one macro row per sector survives.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/etl/macroindicadores.py` | 5-25 | `8166c07e` | primary |

- Merged from: RULE-etl-BE-02-005
- Related rules: RULE-INDICADORES-ETL-013

## Notes
microindicadores.py is an unconditional upsert keyed on NR_SEQ_SETOR_LEITO (no month filter).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
