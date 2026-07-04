# RULE-NUTRICAO-002 — FOIS (Functional Oral Intake Scale) - enum of 7 levels

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Verification | VERIFIED (impact: none) |
| Confidence | high |
| Cluster | nutricao |

## Rule
Functional Oral Intake Scale classifying oral intake in 7 ordinal levels from nil-per-oral (nivel1, worst) to full oral without restriction (nivel7, best).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| fois level | enum |  | nivel1..nivel7 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| fois classification | string |  |

## Logic
```text
nivel1: Nada por via oral
nivel2: Dependente de via alternativa e minima via oral de algum alimento ou liquido
nivel3: Dependente de via alternativa com consistente via oral de alimento ou liquido
nivel4: Via oral total de uma unica consistencia
nivel5: Via oral total com multiplas consistencias, porem com necessidade de preparo especial ou compensacoes
nivel6: Via oral total com multiplas consistencias, porem sem necessidade de preparo especial (sic "oucompensacoes"), porem com restricoes alimentares
nivel7: Via oral total sem restricoes
```

## Edge cases (as implemented)
Ordinal levels 1 (worst) to 7 (best). No computation; classification enum used in ConteudoFormulario.fois. Source has a typo in the nivel6 label ("especial oucompensacoes") preserved verbatim.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Crary MA, Mann GD, Groher ME. Initial psychometric assessment of a Functional Oral Intake Scale for dysphagia in stroke patients. Arch Phys Med Rehabil. 2005;86(8):1516-20.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/choices/formulario.py | 375-403 | 8166c07e | primary |

- Merged from: RULE-nutri-BE-06-001
- Related rules: none

## Notes
Verified against source lines 375-403. Matches published FOIS scale. Field wired in conteudo_formulario.py (fois, lines 105-111). Backend-only in this cluster.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
