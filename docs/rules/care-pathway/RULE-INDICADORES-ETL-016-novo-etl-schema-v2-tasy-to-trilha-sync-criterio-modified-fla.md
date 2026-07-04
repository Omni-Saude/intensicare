# RULE-INDICADORES-ETL-016 — novo_etl_schema (v2) — Tasy-to-Trilha sync, criterio-modified flag overwritten instead of OR-accumulated

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Newer version of the Tasy sync. Drops the 30-day date filter (scans ALL TrilhaTasy rows every run). Uses update_or_create keyed on nr_atendimento. Recomputes the criterio-changed flag per criterio_N, but the flag is REASSIGNED (not OR-accumulated) on each loop iteration, so only the comparison result of the LAST evaluated criterio_N determines whether assistido is reset to False — an earlier criterio's change is overwritten and lost if a later-checked criterio is unchanged. Leito resolution first tries whitelabel 'americashealth' and, on Leito.DoesNotExist, falls back to whitelabel 'homecare', additionally matching on nome=trilha.cd_unidade (not present in v1).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| TrilhaTasy | Django model class (oracle db) |  |  |
| Trilha | Django model class (default db) |  |  |
| quantidade_criterios | integer |  | >= 0, default 0 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| Trilha rows | created or updated via update_or_create |  |
| Leito rows | re-saved, americashealth then homecare fallback |  |

## Logic
```text
FOR obj IN TrilhaTasy.objects.using("oracle"):
  payload = vars(obj); payload.pop("_state", None); payload.pop("_original_state", None)
  nr_atendimento = payload.pop("nr_atendimento")
  TRY:
    trilha, created = Trilha.objects.update_or_create(
      nr_atendimento=nr_atendimento, defaults=payload)
    criterio_modificado = False
    FOR i IN 1..quantidade_criterios:
      criterio = f"criterio_{i}"
      IF hasattr(trilha, criterio):
        criterio_modificado = (getattr(trilha, criterio) != payload.get(criterio))  # OVERWRITE, not OR
        setattr(trilha, criterio, payload.get(criterio))
    IF criterio_modificado: trilha.assistido = False
    trilha.save()
    TRY:
      leito = Leito.objects.get(whitelabel="americashealth", ... nome=trilha.cd_unidade, codigo=trilha.cd_unidade_compl, ...)
      leito.save()
    EXCEPT Leito.DoesNotExist:
      leito = Leito.objects.get(whitelabel="homecare", ... same codes ...)
      leito.save()
  EXCEPT Trilha.DoesNotExist:
    (fallback create path identical in spirit to v1)
  EXCEPT Exception AS e: pprint(e)
  EXCEPT Exception AS e: pprint(e)   # unreachable duplicate except clause
```

## Edge cases (as implemented)
Same broad exception swallowing as v1 (pprint, no raise). Contains an unreachable duplicate `except Exception as e: pprint(e)` clause after an identical one at the same try level — dead code, never executes.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/etl.py` | 65-133 | `8166c07e` | primary |

- Merged from: RULE-etl-BE-11-004
- Related rules: RULE-INDICADORES-ETL-015

## Notes
DISCREPANCY vs RULE-etl-BE-11-003: the criterio-changed flag is overwritten each loop iteration instead of OR-accumulated, so assistido may fail to reset to False even when an earlier criterio genuinely changed, as long as the last-checked criterio_N happens to be unchanged. Recorded verbatim per audit instructions; this appears to be an unintentional regression introduced when moving from etl_schema to novo_etl_schema, not a deliberate design change.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
