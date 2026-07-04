# RULE-COMUNICACAO-002 — Current user's own reaction id on an observation

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
get_minha_reacao_id returns the pk of the requesting user's own Reacao on this observation, or None if none exists or there is no authenticated user in context.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| request.user | object\|null | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| minha_reacao_id | uuid \| null | — |

## Logic
```text
request = context.get("request")
if request and request.user:
    try:
        reacao = instance.reacoes.get(usuario=request.user.get_pk)
        return reacao.get_pk
    except Reacao.DoesNotExist:
        return None
else:
    return None
```

## Edge cases (as implemented)
Uses .get() (not .first()) - would raise MultipleObjectsReturned if a user somehow has more than one reaction on the same observation (not caught); this is only safe if a unique constraint exists on (observacao, usuario), which is out of this partition's scope to confirm. RECONCILED: Reacao model (core/models/reacao.py) declares unique_together=('observacao','usuario') in Meta — confirmed present — so .get() cannot raise MultipleObjectsReturned in practice; the ambiguity flagged by Phase-1 is resolved (safe as written).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal accessor returning the requesting user's own reaction pk on an observation. Relevant external authority is only the Django ORM QuerySet.get() contract (raises DoesNotExist / MultipleObjectsReturned).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/observacao.py | 158-171 | 8166c07e | primary |
- Merged from: RULE-observacao-BE-05-003
- Related rules: RULE-COMUNICACAO-001, RULE-COMUNICACAO-015, RULE-COMUNICACAO-037, RULE-COMUNICACAO-038

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
