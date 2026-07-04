# RULE-MOVIMENTACAO-ADT-028 — Camera-enabled bed list requires a non-empty configured IP

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
CameraViewSet.get_queryset only lists beds in the current sector that have a non-null AND non-empty-string ip_camera configured.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| leito.ip_camera | string \| null |  |  |
| request.setor | object |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | queryset of Leito |  |

## Logic
```text
return Leito.objects.exclude(ip_camera="").filter(ip_camera__isnull=False, setor=request.setor)
```

## Edge cases (as implemented)
Both conditions are required: excludes empty string AND filters not-null - a bed with ip_camera=None or ip_camera='' is excluded either way.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/camera.py | 42-45 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-011
- Related rules: RULE-MOVIMENTACAO-ADT-010, RULE-MOVIMENTACAO-ADT-027

## Notes
permission_trilhas = ('can_access_camera',) gates this viewset (enforcement out of scope).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
