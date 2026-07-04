# RULE-EVOLUCOES-042 — Evolution/progress-note lifecycle status

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Every clinical evolution/progress-note form has exactly one of three lifecycle states — saved as a draft (salvo), formally released/finalized (liberado), or inactivated/voided (inativo).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| status [salvo | liberado | inativo] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| status |  |  |

## Logic
```text
Evolucao.Status = "salvo" | "liberado" | "inativo"
```

## Edge cases (as implemented)
No explicit transition-guard code is present in this partition (e.g. whether inativo is reachable only from liberado, or from any state).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Evolucao.d.ts` | 40-40 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-07-005
- Related rules: RULE-EVOLUCOES-043, RULE-EVOLUCOES-026

## Notes
Used by both Evolucao.Formulario and Evolucao.FormularioMedico status fields. RECONCILED against backend Formulario.status (choices salvo/liberado/inativo, default 'salvo') — matches this frontend enum exactly; no BE/FE divergence.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
