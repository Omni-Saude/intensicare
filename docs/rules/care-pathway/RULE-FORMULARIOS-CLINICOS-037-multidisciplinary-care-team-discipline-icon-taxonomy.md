# RULE-FORMULARIOS-CLINICOS-037 — Multidisciplinary care-team discipline icon taxonomy

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | formularios-clinicos |

## Rule
Ten dedicated React icon components exist for named clinical/professional disciplines, implying the platform's multidisciplinary care-team model recognizes exactly these role categories: Enfermagem, Farmaceutico, Fisioterapeuta, Fonoaudiologo (component fn misspelled 'Fornoaudiologo'), Medico, Musicoterapia, Nutricionista, Psicologo, TecEnfermagem, and Terapeuta (generic 'Therapist').

## Outputs

| Name | Type | Unit |
|---|---|---|
| recognized_disciplines | list<string> | n/a |

## Logic

```text
DISCIPLINE_ICON = {
  Enfermagem: Enfermagem.jsx,          Farmaceutico: Farmaceutico.jsx,
  Fisioterapeuta: Fisioterapeuta.jsx,  Fonoaudiologo: Fonoaudiologo.jsx,
  Medico: Medico.jsx,                  Musicoterapia: Musicoterapia.jsx,
  Nutricionista: Nutricionista.jsx,    Psicologo: Psicologo.jsx,
  TecEnfermagem: TecEnfermagem.jsx,    Terapeuta: Terapeuta.jsx
}
```

## Edge cases (as implemented)

AMBIGUOUS: additional discipline icons may exist under src/icons/configs/ (out of partition scope), so the list cannot be confirmed exhaustive. DISCREPANCY (verbatim): Fonoaudiologo.jsx internal fn/export name is 'Fornoaudiologo' (typo). Masculino.jsx and Psicologo.jsx both internally name their component generic 'Icon' rather than the filename.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/icons/Enfermagem.jsx | 1-9 | f9656be2 | primary |

- Merged from: RULE-CLINICAL-FE-09-010
- Related rules: RULE-FORMULARIOS-CLINICOS-038, RULE-FORMULARIOS-CLINICOS-039

## Notes

Component files: Enfermagem.jsx, Farmaceutico.jsx, Fisioterapeuta.jsx, Fonoaudiologo.jsx, Medico.jsx, Musicoterapia.jsx, Nutricionista.jsx, Psicologo.jsx, TecEnfermagem.jsx, Terapeuta.jsx (each 1-9).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
