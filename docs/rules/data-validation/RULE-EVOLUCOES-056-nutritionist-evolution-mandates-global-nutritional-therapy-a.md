# RULE-EVOLUCOES-056 — Nutritionist evolution mandates global, nutritional-therapy, and abdominal assessments

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Unlike every other professional evolution serializer in this codebase (which declare their embedded assessment sub-serializers as required=False), the nutritionist evolution form requires avaliacao_global, terapia_nutricional, and avaliacao_abdominal to be present and valid on every create/update.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_global |  |  |  |
| terapia_nutricional |  |  |  |
| avaliacao_abdominal |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if any of the three sub-sections is missing/invalid |  |  |

## Logic
```text
avaliacao_global = AvaliacaoGlobalNutricionistaSerializer(required=True)
terapia_nutricional = TerapiaNutricionalNutricionistaSerializer(required=True)
avaliacao_abdominal = AvaliacaoAbdominalNutricionistaSerializer(required=True)
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_nutricionista.py` | 19-30 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-016
- Related rules: RULE-EVOLUCOES-038, RULE-EVOLUCOES-015

## Notes
Contrast with e.g. FormularioFisioterapeutaSerializer / FormularioMedicoSerializer / FormularioEnfermagemSerializer, which all mark their equivalent sub-sections required=False.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
