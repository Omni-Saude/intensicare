# RULE-OPERACIONAL-INFRA-018 — SetUpModel.delete — overrides ParanoiaMixin.delete with simpler soft-delete-only semantics (no cascade, no admin-path check)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

SetUpModel (which combines TimeManagerMixin, ParanoiaMixin, UUIDPkFieldMixin, UniqueTogetherManagerMixin, UniqueManagerMixin) defines its OWN delete() method directly, which takes precedence over the inherited ParanoiaMixin.delete() in Python's MRO. SetUpModel.delete(): if force_delete=True, performs a real hard delete via super(SetUpModel, self).delete(); otherwise sets deletado_em=timezone.now() and saves — with NO cascade to related_objects() and NO admin-request-path branch.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.force_delete | boolean | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| deletion outcome | hard delete OR simple (non-cascading) soft-delete | - |

## Logic

```text
SetUpModel.delete(self, *args, **kwargs):
  IF kwargs.get("force_delete", False):
    RETURN super(SetUpModel, self).delete(*args, **kwargs)   # HARD delete, no cascade logic here
  ELSE:
    self.deletado_em = timezone.now()
    self.save()
```

## Edge cases (as implemented)

Because SetUpModel defines delete() directly on the class, ParanoiaMixin's cascade-to-related-objects and the admin-request-path hard-delete branch (RULE-model-BE-11-057) are effectively DEAD CODE for any model built on SetUpModel (the common base class convention in this codebase) — they would only apply to a model using ParanoiaMixin WITHOUT also using/overriding via SetUpModel.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/models.py` | 245-261 | `8166c07e` | primary |

- Merged from: RULE-model-BE-11-058
- Related rules: RULE-OPERACIONAL-INFRA-017

## Notes

DISCREPANCY: two different delete-semantics coexist in the same MRO chain (ParanoiaMixin.delete vs SetUpModel.delete) and only one is ever reachable depending on which class a given model instantiates from. Verifier should check which concrete app models (out of this partition's scope) inherit SetUpModel vs ParanoiaMixin directly to know which delete behavior actually applies where.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
