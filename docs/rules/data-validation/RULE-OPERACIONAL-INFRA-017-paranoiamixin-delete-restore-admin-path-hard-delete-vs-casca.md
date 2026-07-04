# RULE-OPERACIONAL-INFRA-017 — ParanoiaMixin.delete/restore — admin-path hard delete vs cascading soft delete

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

delete(): if the instance has a `request` attribute AND request.path starts with '/admin/' AND the caller did not pass soft_delete=True, OR the caller passed force_delete=True, performs a REAL (hard, cascading via Django's normal delete) deletion. Otherwise, it soft-deletes: recursively soft-deletes all related_objects() (cascade=True) inside one DB transaction, then sets deletado_em=datetime.now() on self and saves. restore() mirrors this: cascades restore to related objects, then clears deletado_em on self.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.soft_delete | boolean | - | - |
| kwargs.force_delete | boolean | - | - |
| self.request.path | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| deletion outcome | hard delete OR soft-delete cascade | - |

## Logic

```text
delete(**kwargs):
  IF (hasattr(self,"request") AND self.request.path.startswith("/admin/") AND NOT kwargs.get("soft_delete", False))
     OR kwargs.pop("force_delete", False):
    super().delete(**kwargs)      # HARD delete
  ELSE:
    WITH transaction.atomic():
      FOR related IN self.related_objects(): related.delete(cascade=True, **kwargs)
    self.deletado_em = datetime.now(); self.save()
restore(**kwargs):
  WITH transaction.atomic():
    FOR related IN self.related_objects(): related.restore(cascade=True)
  self.deletado_em = None; self.save()
```

## Edge cases (as implemented)

Deletes performed through the Django admin UI (path starting '/admin/') default to a REAL hard delete unless soft_delete=True is explicitly passed — the inverse of what a 'safety-first' soft-delete convention would suggest for admin/staff-driven actions vs API-driven ones.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/models.py` | 193-243 | `8166c07e` | primary |

- Merged from: RULE-model-BE-11-057
- Related rules: RULE-OPERACIONAL-INFRA-018

## Notes

AMBIGUOUS: flagged because the admin-path branch's default-to-hard-delete behavior is surprising and risk-relevant for a clinical records system; needs product/security sign-off during rebuild. Also see RULE-model-BE-11-058: SetUpModel, which most concrete models appear to inherit from, entirely overrides this delete() method with different (simpler) semantics.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
