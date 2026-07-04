# RULE-TENANCY-ORGANIZACAO-049 — Company logo field rename with silent drop for non-string values

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
EmpresaViewSet.manage_data always pops 'logo' out of the incoming data; it is only re-added as 'logo_b64' if it is a truthy string. If 'logo' is present but not a string (or falsy), it is silently discarded from the payload entirely with no error and no effect.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| logo | string \| other |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| logo_b64 | string |  |

## Logic
```text
logo = data.pop("logo", None)
if logo and isinstance(logo, str):
    data["logo_b64"] = logo
# else: logo value is lost, no logo_b64 set, no error raised
```

## Edge cases (as implemented)
A non-string truthy 'logo' value (e.g., a dict or file-like object sent by mistake) is dropped without feedback to the client.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/empresa.py | 34-40 | 8166c07e | primary |

- Merged from: RULE-empresa-BE-05-002
- Related rules: RULE-TENANCY-ORGANIZACAO-040

## Notes
Reconciliation: paired with empresa-BE-05-001 (EmpresaSerializer.update), which receives whatever survives this view-layer pre-processing step as logo_b64; kept separate (different layer).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
