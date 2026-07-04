# RULE-EVOLUCOES-062 — Pharmacist evolution-form key naming/type inconsistency

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
The pharmacist evolution-form tab is implemented in useEvolucaoMenu under the object key "formulario_farmaceutica" (feminine ending), but this exact string does not appear in the Utils.FormsEvolucao type union (which omits any pharmacist entry at all) and does not match the naming pattern of its own gating permission "can_preencher_formulario_farmaceutico" (masculine ending) or of the sibling role keys (all masculine, e.g. formulario_medico, formulario_psicologo).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| role key |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| evolucaoComponents key set |  |  |

## Logic
```text
Utils.FormsEvolucao = formulario_medico | formulario_tec_enfermagem | formulario_enfermagem |
                       formulario_fisioterapeuta | formulario_musicoterapeuta |
                       formulario_nutricionista | formulario_psicologo |
                       formulario_fonoaudiologo | formulario_intercorrencia
                       // note: no pharmacist entry at all (9 members)
useEvolucaoMenu's evolucaoComponents object literal additionally defines key:
  "formulario_farmaceutica"   // not in the above union; only compiles because the
                               // object is force-cast `as Record<Utils.FormsEvolucao, {...}>`
Permission gating this tab: can_preencher_formulario_farmaceutico   // masculine, differs from the object key
```

## Edge cases (as implemented)
Because the object is cast with `as` (bypassing TypeScript excess-property/exact-shape checks), this mismatch does not surface as a compile error, meaning it can silently persist; any code that iterates Object.keys(evolucaoComponents) typed as Utils.FormsEvolucao would see a key the type system does not know about.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useEvolucaoMenu.tsx` | 292-316 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-07-006
- Related rules: RULE-EVOLUCOES-035

## Notes
Cross-reference src/@types/utils/Utils.d.ts (FormsEvolucao) lines 111-120 and src/@types/models/Permissions.d.ts line 28 (can_preencher_formulario_farmaceutico).

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
