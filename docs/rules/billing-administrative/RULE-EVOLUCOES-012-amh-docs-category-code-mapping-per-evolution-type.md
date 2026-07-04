# RULE-EVOLUCOES-012 — AMH Docs category-code mapping per evolution type

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When exporting a signed evolution document to the external AMH Docs system, the professional-type "tipo" of the evolution is mapped to a fixed category code; unrecognized types fall back to a generic "EI" code.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo [medico | tecnico_enfermagem | enfermagem | fisioterapeuta | terapeuta | musicoterapeuta | nutricionista | psicologo | fonoaudiologo | farmaceutico | intercorrencia] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| categoria |  |  |

## Logic
```text
switcher = {
  "medico": "EHCMED", "tecnico_enfermagem": "EHCTEC", "enfermagem": "EHCENF",
  "fisioterapeuta": "EHCFIS", "terapeuta": "EHCTER", "musicoterapeuta": "EHCMUS",
  "nutricionista": "EHCNUT", "psicologo": "EHCPSI", "fonoaudiologo": "EHCFON",
  "farmaceutico": "EHCFCT", "intercorrencia": "EHCINT",
}
categoria = switcher.get(tipo, "EI")
```

## Edge cases (as implemented)
Default "EI" for any tipo not in the switcher.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 154-191 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-002
- Related rules: RULE-EVOLUCOES-010

## Notes
pdf_base64 is prefixed "data:application/pdf;base64," and built from pdf_assinado.read() — i.e. always the SIGNED pdf at this call site (see RULE-evolucao-BE-07-003).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
