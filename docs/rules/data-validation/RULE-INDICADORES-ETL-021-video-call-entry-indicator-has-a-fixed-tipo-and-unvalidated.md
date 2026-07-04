# RULE-INDICADORES-ETL-021 — Video-call entry indicator has a fixed tipo and unvalidated setor_id

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
entrada_videochamada always creates an Indicador with tipo hardcoded to 'entrada_videochamada'; usuario_id and data_entrada are server-stamped as in the generic create; setor_id is taken directly from the client body with no check that the user actually belongs to that sector.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.data.setor_id | uuid |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| indicador | object |  |

## Logic
```text
indicador_data = {
  "tipo": "entrada_videochamada",
  "dados": {"usuario_id": request.user.get_pk, "setor_id": data.get("setor_id"), "data_entrada": str(timezone.now())},
}
Indicador(**indicador_data).save()
return Response({"ok": True})
```

## Edge cases (as implemented)
No verification that setor_id corresponds to a real Setor the user has access to - any UUID-shaped value is accepted and stored as-is.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/indicador.py` | 33-46 | `8166c07e` | primary |

- Merged from: RULE-indicador-BE-05-002
- Related rules: RULE-INDICADORES-ETL-020, RULE-INDICADORES-ETL-027

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
