# RULE-INDICADORES-ETL-013 — Incremental (watermark) load of occupancy indicators

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Occupancy indicators (per-establishment and per-sector) are loaded incrementally: find the most recent dt_referencia already stored locally, then pull from Oracle every row with dt_referencia >= that watermark; if no local rows exist, load all. Each row is updated in place when its pk already exists, else created.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dt_referencia | datetime |  |  |
| last_local.dt_referencia | datetime |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| rows_upserted | integer |  |

## Logic
```text
last = Local.objects.order_by("-dt_referencia").first()
if last:
    src = Oracle.filter(dt_referencia >= last.dt_referencia).order_by("dt_referencia")
else:
    src = Oracle.order_by("dt_referencia").all()
for obj in src:
    if Local.filter(pk=obj.pk):
        obj.__dict__.pop("cd_estabelecimento")   # or cd_setor_atendimento for sectors
        Local.filter(pk=obj.pk).update(**obj.__dict__)
    else:
        Local.objects.create(**obj.__dict__)
```

## Edge cases (as implemented)
Watermark comparison is >= (gte), so the boundary record at exactly last.dt_referencia is re-fetched and re-updated every run (idempotent update, but reprocessed). pk collision key is the row pk; cd_estabelecimento / cd_setor_atendimento is popped before update to avoid overwriting the tenant key.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/etl/indicadores.py` | 7-70 | `8166c07e` | primary |

- Merged from: RULE-etl-BE-02-004
- Related rules: RULE-INDICADORES-ETL-014

## Notes
Duplicated verbatim in trilha_automatica/etl/trilha1.py lines 19-82 as novo_etl_indicadores_estabelecimento / novo_etl_novo_etl_indicadores_setores. Two identical implementations of the same watermark rule.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
