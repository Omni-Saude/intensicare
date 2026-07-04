# RULE-COMUNICACAO-008 — Chat message retention window - 48h default, 96h when filtering by leito

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
ChatViewSet's queryset excludes observations older than a cutoff that depends on whether a 'leito' query parameter is present: with a leito filter, messages up to 96 hours (4 days) old are retained; without it (setor-wide chat), only messages up to 48 hours (2 days) old are retained.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| request.query_params.leito | string \| null | — | — |
| observacao.criado_em | datetime | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | queryset of Observacao | — |

## Logic
```text
is_leito_filter = request.query_params.get("leito")
cutoff_hours = 96 if is_leito_filter else 48
queryset = Observacao.objects.filter(setor=request.setor).exclude(
    criado_em__lte=timezone.now() - timedelta(hours=cutoff_hours)
)
```

## Edge cases (as implemented)
Boundary uses __lte (less-than-or-equal) in exclude(), i.e. messages with criado_em exactly equal to the cutoff instant are excluded (kept only if strictly newer than cutoff).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/chat.py | 23-54 | 8166c07e | primary |
- Merged from: RULE-observacao-BE-05-009
- Related rules: RULE-COMUNICACAO-021

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
