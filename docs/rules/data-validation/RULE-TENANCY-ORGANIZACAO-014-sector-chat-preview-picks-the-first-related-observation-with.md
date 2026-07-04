# RULE-TENANCY-ORGANIZACAO-014 — Sector chat preview picks the first related observation without explicit ordering

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
SetorChatsSerializer.get_ultima_mensagem returns the text of instance.observacoes.first() (or empty string if none exist), intending to show the 'latest message' - but no explicit .order_by() is applied here, so correctness depends entirely on the Observacao model's default Meta.ordering (out of this partition's scope).

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.observacoes | related manager of Observacao |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| ultima_mensagem | string |  |

## Logic

```text
return instance.observacoes.first().texto if instance.observacoes.exists() else ""
```

## Edge cases (as implemented)
If Observacao's default ordering is not by creation date descending, 'first()' will not actually return the most recent message despite the field name 'ultima_mensagem' (last message).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal/proprietary UI/data-presentation logic: SetorChatsSerializer.get_ultima_mensagem returns instance.observacoes.first().texto. Chat-preview 'latest message' selection is application behavior, not a clinical algorithm. Correctness hinges on Observacao.Meta.ordering, which is outside this partition's scope.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 311-314 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-013`
- Related rules: RULE-TENANCY-ORGANIZACAO-033

## Notes
Best interpretation: relies on Observacao.Meta.ordering being descending by criado_em; a verifier with access to core/models/observacao.py should confirm.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
