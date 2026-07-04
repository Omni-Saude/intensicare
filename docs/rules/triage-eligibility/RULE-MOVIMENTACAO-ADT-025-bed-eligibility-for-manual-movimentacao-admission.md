# RULE-MOVIMENTACAO-ADT-025 — Bed eligibility for manual movimentacao (admission)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
A manual admission is blocked on automatic-type beds and on already-occupied beds.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| leito | pk, uuid |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid \| ValidationError | bool |  |

## Logic
```text
leito = get_object_or_404(Leito, pk)
if leito.tipo == "automatica": raise ValidationError("Nao e possivel alterar um leito automatico!")
if leito.ocupado: raise ValidationError("Leito ja se encontra ocupado!")
```

## Edge cases (as implemented)
404 if bed not found. Only "automatica" blocked (homecare/manual allowed).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/use_cases/validators/leito.py | 13-27 | 8166c07e | primary |
- Merged from: RULE-validation-BE-04-042
- Related rules: RULE-MOVIMENTACAO-ADT-032, RULE-MOVIMENTACAO-ADT-062, RULE-MOVIMENTACAO-ADT-052

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
