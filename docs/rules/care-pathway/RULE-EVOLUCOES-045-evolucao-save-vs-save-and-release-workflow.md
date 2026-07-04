# RULE-EVOLUCOES-045 — Evolução save-vs-save-and-release workflow

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When a caregiver finishes filling an "evolução" (clinical progress note) form, a confirmation modal offers two actions: "Salvar" (save as draft, unsigned) or "Salvar e Liberar" (save and release/sign). The chosen action determines whether the submitted payload carries a "liberado" status and an "assinar" (sign) flag.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucaoLiberada (user choice) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| payload.status |  |  |
| payload.assinar |  |  |

## Logic
```text
onPostEvolucao(values):
  return {
    ...values,
    status: evolucaoLiberada ? "liberado" : undefined,
    assinar: evolucaoLiberada
  }
// "Salvar" button:      evolucaoLiberada = false; form.submit()
// "Salvar e Liberar":   evolucaoLiberada = true;  form.submit();
//                       message.success("Formulário salvo e liberado (assinado)!")
```

## Edge cases (as implemented)
The confirmation modal (Modal.confirm) is only reachable if the OK button is not hidden — see RULE-evolucao-FE-06-012.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx` | 91-100,200-238 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-06-011
- Related rules: RULE-EVOLUCOES-044, RULE-EVOLUCOES-020

## Notes
The actual persistence/signature semantics of "liberado"/"assinar" are implemented server-side and in the (out-of-partition) useEvolucaoMenu hook; this rule documents only the client-side trigger logic.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
