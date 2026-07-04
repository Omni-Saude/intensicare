# RULE-TENANCY-ORGANIZACAO-040 — Company logo base64 conversion on update

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
EmpresaSerializer.update converts an incoming logo_b64 string into an actual file (via transform_b64_to_file) before persisting, replacing whatever was in the 'logo' field.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| logo_b64 | string (base64) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| logo | file |  |

## Logic
```text
@transaction.atomic
def update(instance, validated_data):
    b64 = validated_data.pop("logo_b64", None)
    if b64:
        validated_data["logo"] = transform_b64_to_file(b64)
    return super().update(instance, validated_data)
```

## Edge cases (as implemented)
If logo_b64 is falsy/absent, logo is left untouched (not cleared).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/empresa.py | 34-40 | 8166c07e | primary |

- Merged from: RULE-empresa-BE-05-001
- Related rules: RULE-TENANCY-ORGANIZACAO-049

## Notes
Reconciliation: paired with empresa-BE-05-002 (EmpresaViewSet.manage_data), which controls what reaches this serializer's logo_b64 input in the first place; kept separate (different layer: view pre-processing vs serializer persistence).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
