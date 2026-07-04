# RULE-INDICADORES-ETL-015 — etl_schema (v1) — Tasy-to-Trilha sync with assistido reset

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Synchronizes Trilha rows from the Oracle Tasy hospital system (TrilhaTasy), restricted to source rows referenced in the last 30 days. For an existing local Trilha (matched by nr_atendimento), diffs up to quantidade_criterios criterio_N fields against the incoming Tasy values; if ANY differ, marks the pathway as not-yet-reviewed (assistido=False). Also re-resolves the linked Leito by estabelecimento/setor/leito codes, scoped to the 'americashealth' whitelabel tenant, and re-saves it.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| TrilhaTasy | Django model class (oracle db) |  |  |
| Trilha | Django model class (default db) |  |  |
| quantidade_criterios | integer |  | >= 0, default 0 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| Trilha rows | created or updated |  |
| Leito rows | re-saved |  |

## Logic
```text
dia_referencia = now() - 30 days
query = TrilhaTasy.objects.filter(dt_referencia__gte=dia_referencia).using("oracle").all()
FOR obj IN query.iterator():
  TRY:
    trilha = Trilha.objects.get(nr_atendimento=obj.nr_atendimento)
    criterio_modificado = False
    FOR i IN 1..quantidade_criterios:
      criterio = f"criterio_{i}"
      IF hasattr(trilha, criterio):
        IF getattr(trilha, criterio) != obj.__dict__.get(criterio):
          criterio_modificado = True      # OR-accumulated across all i
        setattr(trilha, criterio, obj.__dict__.get(criterio))
    IF criterio_modificado: trilha.assistido = False
    trilha.save()
    leito = Leito.objects.get(
      setor__estabelecimento__empresa__whitelabel="americashealth",
      setor__estabelecimento__codigo=trilha.cd_estabelecimento,
      setor__codigo=trilha.cd_setor_atendimento,
      codigo=trilha.cd_unidade_compl)
    leito.save()
  EXCEPT Trilha.DoesNotExist:
    TRY:
      trilha = Trilha.objects.create(**obj.__dict__)
      (same Leito lookup/save as above; failures pprint(e) and are swallowed)
    EXCEPT Exception AS e: pprint(e)
  EXCEPT Exception AS e: pprint(e)
```

## Edge cases (as implemented)
All lookup/creation failures are caught and merely printed (pprint), never raised — the batch continues to the next record with no rollback or alerting. Tasy rows older than 30 days relative to dt_referencia are never scanned by this version.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/etl.py` | 7-62 | `8166c07e` | primary |

- Merged from: RULE-etl-BE-11-003
- Related rules: RULE-INDICADORES-ETL-016

## Notes
Hardcoded to whitelabel 'americashealth' only. Compare with novo_etl_schema (RULE-etl-BE-11-004), the v3/v2 variant, which changes the criterio-modified accumulation logic (a discrepancy) and adds a homecare tenant fallback.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
