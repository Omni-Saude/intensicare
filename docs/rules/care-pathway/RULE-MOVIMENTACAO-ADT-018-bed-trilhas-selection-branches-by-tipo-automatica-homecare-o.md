# RULE-MOVIMENTACAO-ADT-018 — Bed trilhas selection branches by tipo (automatica/homecare only)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
get_trilhas dispatches to _get_trilhas_automaticas for tipo=='automatica', to _get_trilhas_homecare for tipo=='homecare', and returns None (falls through) for any other tipo (i.e. 'manual').

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.tipo | string enum manual\|automatica\|homecare |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| trilhas | array of object \| null |  |

## Logic
```text
if instance.tipo == "automatica":
    return self._get_trilhas_automaticas(instance)
elif instance.tipo == "homecare":
    return self._get_trilhas_homecare(instance)
# else: implicit return None
```

## Edge cases (as implemented)
'manual'-type beds get trilhas=None in the OcupacaoSerializer payload (not an empty list).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/leito.py | 202-210 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-006
- Related rules: RULE-MOVIMENTACAO-ADT-036, RULE-MOVIMENTACAO-ADT-037, RULE-MOVIMENTACAO-ADT-052

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
