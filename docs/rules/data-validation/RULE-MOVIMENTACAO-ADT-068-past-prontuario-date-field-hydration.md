# RULE-MOVIMENTACAO-ADT-068 — Past-prontuário date field hydration

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
When re-displaying a previously recorded prontuário (occupation record) in read/edit-in-page mode, the noradrenalina, parada cardiorrespiratória, and ventilação mecânica horario_inicio string values are parsed into moment objects so the form fields can render them as date/time pickers.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| values.noradrenalina.horario_inicio | string (date) | n/a | n/a |
| values.parada_cardiorrespiratoria.horario_inicio | string (date) | n/a | n/a |
| values.ventilacao_mecanica.horario_inicio | string (date) | n/a | n/a |

## Outputs
| Name | Type | Unit |
|---|---|---|
| dados_prontuario.noradrenalina.horario_inicio | moment object \| undefined | n/a |
| dados_prontuario.parada_cardiorrespiratoria.horario_inicio | moment object \| undefined | n/a |
| dados_prontuario.ventilacao_mecanica.horario_inicio | moment object \| undefined | n/a |

## Logic
```text
initialValues(values) = {
  dados_prontuario: {
    ...values,
    noradrenalina: values.noradrenalina && { ...values.noradrenalina, horario_inicio: values.noradrenalina.horario_inicio && moment(values.noradrenalina.horario_inicio) },
    parada_cardiorrespiratoria: values.parada_cardiorrespiratoria && { ...values.parada_cardiorrespiratoria, horario_inicio: values.parada_cardiorrespiratoria.horario_inicio && moment(...) },
    ventilacao_mecanica: values.ventilacao_mecanica && { ...values.ventilacao_mecanica, horario_inicio: values.ventilacao_mecanica.horario_inicio && moment(...) }
  }
}
```

## Edge cases (as implemented)
horario_fim of ventilacao_mecanica is NOT re-hydrated here (unlike the submit-side transform in RULE-prontuario-FE-06-013), so it is passed through as a raw string.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ProntuarioPassado/ProntuarioPassado.tsx | 31-55 | f9656be2 | primary |

- Merged from: RULE-prontuario-FE-06-014
- Related rules: None

## Notes
Cross-reference RULE-prontuario-FE-06-013 (inverse transform, submit side).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
