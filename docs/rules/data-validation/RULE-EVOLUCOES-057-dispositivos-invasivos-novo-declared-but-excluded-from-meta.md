# RULE-EVOLUCOES-057 — dispositivos_invasivos_novo declared but excluded from Meta.fields

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
FormularioEnfermagemSerializer explicitly declares a required, many=True field "dispositivos_invasivos_novo" as a class attribute, but this field name is absent from every fields tuple in Meta (default and all three action_fields variants), which violates DRF's ModelSerializer contract that all declared fields must be listed in Meta.fields.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dispositivos_invasivos_novo (declared serializer field) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| N/A — serializer instantiation |  |  |

## Logic
```text
dispositivos_invasivos_novo = BaseDispositivosInvasivoEnfermeiroSerializer(
    many=True, required=True,
)
class Meta:
    fields = (... does not include "dispositivos_invasivos_novo" ...)
    action_fields = {"create": {...}, "list": {...}, "retrieve": {...}}  # also excludes it
```

## Edge cases (as implemented)
DRF's ModelSerializer.get_fields() asserts that every explicitly declared field name appears in the resolved fields list, raising "The field 'dispositivos_invasivos_novo' was declared on serializer ..., but has not been included in the 'fields' option." This would raise an AssertionError the first time this serializer (or any action variant that resolves to the default Meta.fields) is instantiated/used, unless the action_serializer library's ModelActionSerializer/action_fields mechanism suppresses or bypasses this DRF assertion in a way not visible in this file.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_enfermagem.py` | 43-48 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-014
- Related rules: none

## Notes
Confidence marked medium because ModelActionSerializer (from the external action_serializer package, out of scope) may override get_fields()/action_fields resolution in a way that avoids the standard DRF assertion — this could not be verified from files in this partition alone.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
