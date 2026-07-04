# RULE-TENANCY-ORGANIZACAO-007 — Establishment unread message count sums across ALL sectors, not just user's own

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | formula |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
get_qtd_mensagens sums the Firestore unread-count for every sector belonging to the establishment (instance.setores.all()), without filtering to sectors the requesting user actually belongs to - unlike nearly every other computed field in this file which scopes to setor__usuarios=request.user.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.setores | related manager of Setor |  |
| request.user.pk | uuid |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| qtd_mensagens | integer |  |

## Logic

```text
total_msg = 0
for setor in instance.setores.all():
    total_msg += get_qtd_msg_setor(setor, request.user, db)   # Firestore chats/{setor.pk}/usuarios/{usuario.pk}
return total_msg
```

## Edge cases (as implemented)
Because the Firestore path is keyed by the user's own pk (chats/{setor}/usuarios/{usuario.pk}), a user with no membership/message history for a given sector simply contributes 0 for that sector (no cross-user data leakage) - but the lack of a setor__usuarios=user filter here is inconsistent with the rest of the file and could sum sectors the user has no access to if that sector nonetheless has a stored Firestore doc for them (e.g. from a past membership).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Internal messaging/tenancy rule: EstabelecimentoStatusSerializer.get_qtd_mensagens sums Firestore unread counters across instance.setores.all(). Legacy verbatim confirmed at core/api/v1/serializers/estabelecimento.py:231-251 @ 8166c07.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/estabelecimento.py` | 231-251 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-006`
- Related rules: RULE-TENANCY-ORGANIZACAO-008

## Notes
Best interpretation: not a security bug (data is keyed by the requesting user's own pk) but a scoping inconsistency vs. sibling methods in the same serializer; flagged AMBIGUOUS because the intent (sum only 'my' sectors vs. sum the whole establishment) cannot be confirmed from code alone. | Reconciliation: sector-level counterpart (see related) is scoped to a single sector for the requesting user via the same Firestore path convention. Kept separate since this rule sums across ALL of the establishment's sectors regardless of user membership (the AMBIGUOUS scoping question is specific to this rule).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
