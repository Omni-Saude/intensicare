# RULE-TRILHAS-ENGINE-018 — Care-pathway type enumeration (AssistidoChoices vs ObservacaoChoices — label drift)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
Canonical set of 12 clinical care-pathway ("trilha") type slugs an assist record / observation can reference. Two backend copies exist — AssistidoChoices.tipo (used by AssistidoPor.tipo) and ObservacaoChoices.tipo_trilha (used by Observacao.tipo_trilha) — with identical slug values/order but drifted display labels.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo / tipo_trilha | string (slug) |  | sedacao\|estabilizacao\|ventilacao\|sepse\|antimicrobiano\|nutricao\|equilibrio\|profilaxias\|piora_clinica\|zero_glosa\|auditoria\|eficiencia |

## Outputs

| Name | Type | Unit |
|---|---|---|
| display_label | string |  |

## Logic
```text
# Both copies return the same 12 (value, label) tuples in the same order:
#   sedacao, estabilizacao, ventilacao, sepse, antimicrobiano, nutricao,
#   equilibrio, profilaxias, piora_clinica, zero_glosa, auditoria, eficiencia
# AssistidoChoices.tipo()  (assistido.py)      labels: sepse="Sepse",  piora_clinica="Piora Clínica"
# ObservacaoChoices.tipo_trilha() (observacao.py) labels: sepse="SEPSE", piora_clinica="Piora Clinica"
# Consumers:
#   AssistidoPor.tipo        -> CharField(max_length=65)
#   Observacao.tipo_trilha   -> CharField(max_length=20), blank/null allowed
```

## Edge cases (as implemented)
No default; not enforced beyond Django choices (advisory unless full_clean is called). Observacao.tipo_trilha is blank/null allowed. max_length=20 on Observacao fits the longest slug ("antimicrobiano"=14) so truncation risk is low. These 12 slugs map onto the automatic/homecare pathway model sets (RULE-TRILHAS-ENGINE-001/002).

## Divergence
Two independent backend enum copies of the same 12-slug set drift in display labels: AssistidoChoices.tipo (assistido.py) uses sepse="Sepse" and piora_clinica="Piora Clínica"; ObservacaoChoices.tipo_trilha (observacao.py) uses sepse="SEPSE" and piora_clinica="Piora Clinica" (missing acute accent on the "í"). The other 10 (value,label) pairs and the slug values/order are identical. Field width also differs: AssistidoPor.tipo max_length=65 vs Observacao.tipo_trilha max_length=20. Two copies risk further drift.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/choices/assistido.py` | 4-20 | `8166c07e` | primary |
| ahlabs-trilhas | `core/models/choices/observacao.py` | 1-17 | `8166c07e` | duplicate |

- Merged from: `RULE-trilha-BE-04-001`, `RULE-trilha-BE-04-002`
- Related rules: RULE-TRILHAS-ENGINE-001, RULE-TRILHAS-ENGINE-013

## Notes
Merge of the two enum copies (RULE-trilha-BE-04-001 primary, RULE-trilha-BE-04-002 duplicate). Divergence verified verbatim against legacy source. Pre-flagged in Phase 1 (BE-04-002 already DISCREPANCY) — not a newly discovered divergence.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
