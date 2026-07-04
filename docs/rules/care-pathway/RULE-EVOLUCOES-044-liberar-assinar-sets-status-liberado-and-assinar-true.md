# RULE-EVOLUCOES-044 — Liberar/assinar sets status=liberado and assinar=true

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Releasing/signing an evolution patches it with status "liberado" and assinar true, merging the current form values (optionally adapted by adaptSubmit).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| form values |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| patchBody |  |  |

## Logic
```text
values = { ...form.getFieldsValue(), status:"liberado", assinar:true }
_patchFormulario(formulario.id, adaptSubmit ? adaptSubmit(values) : values)
# dt_registro reformatted to "YYYY-MM-DD HH:mm" inside _patchFormulario when present.
```

## Edge cases (as implemented)
The confirmation modal offers "Atualizar" (plain form.submit, keeps status) vs "Liberar/assinar" (sets liberado+assinar). Re-sign button on already-liberado forms repeats the liberado+assinar patch.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/HistoricoEvolucao/HistoricoEvolucao.tsx` | 196-278 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-04-035
- Related rules: RULE-EVOLUCOES-045, RULE-EVOLUCOES-043, RULE-EVOLUCOES-025

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
