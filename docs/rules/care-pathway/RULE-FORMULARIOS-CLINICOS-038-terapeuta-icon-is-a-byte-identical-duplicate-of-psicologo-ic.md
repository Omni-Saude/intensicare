# RULE-FORMULARIOS-CLINICOS-038 — Terapeuta icon is a byte-identical duplicate of Psicologo icon

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule
src/icons/Terapeuta.jsx and src/icons/Psicologo.jsx contain byte-for-byte identical SVG markup (same viewBox '0 0 785.771 658', identical path/circle elements and fill colors) - confirmed via direct diff after normalizing the component name/height line. The only differences: internal function name (generic 'Icon' in Psicologo.jsx vs 'Terapeuta' in Terapeuta.jsx), the export name, and the height aspect-ratio multiplier (size*0.837 for Psicologo vs size*1.2 for Terapeuta). Both 166 lines.

## Outputs

| Name | Type | Unit |
|---|---|---|
| rendered_svg_identical | boolean | n/a |

## Logic

```text
diff(Psicologo.jsx[lines 5-163], Terapeuta.jsx[lines 5-163]) == only line 4 differs:
  "height={size * 0.837}"  vs  "height={size * 1.2}"
=> all path/circle "d"/"fill" data identical
```

## Edge cases (as implemented)

DISCREPANCY (verbatim, not corrected): the UI cannot visually distinguish the 'Psicologo' (Psychologist) and 'Terapeuta' (generic Therapist) disciplines by icon - the same artwork renders (different aspect ratio). May be intentional placeholder reuse or a copy-paste oversight; source alone does not disambiguate.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/icons/Terapeuta.jsx | 1-166 | f9656be2 | primary |

- Merged from: RULE-CLINICAL-FE-09-011
- Related rules: RULE-FORMULARIOS-CLINICOS-037

## Notes

Cross-referenced against src/icons/Psicologo.jsx lines 1-166; diff performed directly on file contents.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
