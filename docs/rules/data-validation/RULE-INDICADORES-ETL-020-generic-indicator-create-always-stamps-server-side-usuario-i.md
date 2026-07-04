# RULE-INDICADORES-ETL-020 — Generic indicator create always stamps server-side usuario_id and timestamp

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
IndicadorViewSet.create builds an Indicador record whose 'dados' JSON always includes usuario_id (current user) and data_entrada (current timestamp, stringified) merged on top of (i.e., overriding) whatever the client sent in 'dados'; 'tipo' is taken directly from the client without validation against any enum.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.data.tipo | string |  |  |
| request.data.dados | object |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| indicador | object |  |

## Logic
```text
indicador_data = {
  "tipo": data.get("tipo"),
  "dados": {**data.get("dados", {}), "usuario_id": request.user.get_pk, "data_entrada": str(timezone.now())},
}
Indicador(**indicador_data).save()
return Response({"ok": True})
```

## Edge cases (as implemented)
'tipo' is unrestricted free-form input from the client - no choices/enum validation visible in this partition. Because usuario_id/data_entrada are spread after the client's dados dict then set as explicit keys, any client-supplied usuario_id/data_entrada in the body is overwritten by the server values.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/indicador.py` | 16-31 | `8166c07e` | primary |

- Merged from: RULE-indicador-BE-05-001
- Related rules: RULE-INDICADORES-ETL-021, RULE-INDICADORES-ETL-027

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
