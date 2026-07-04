# RULE-COMUNICACAO-027 — Reaction hard-delete override

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | comunicacao |

## Rule
Deleting a reaction bypasses normal (soft-delete) semantics by calling delete(force_delete=True), permanently removing the row.

## Logic
```text
def perform_destroy(instance):
    instance.delete(force_delete=True)
```

## Edge cases (as implemented)
Contrasts with the soft-delete convention seen elsewhere (e.g. objects_without_deleted managers, is_active flags on Usuario) - reactions are truly hard-deleted.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/reacao.py | 35-36 | 8166c07e | primary |
- Merged from: RULE-reacao-BE-05-002
- Related rules: RULE-COMUNICACAO-038, RULE-COMUNICACAO-001

## Notes
force_delete kwarg implies the underlying model's default .delete() is a soft-delete; the model itself is out of this partition's scope.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
