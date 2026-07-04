# RULE-MOVIMENTACAO-ADT-065 — InfoPaciente listing scoped by encounter

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Patient-info records are restricted to those matching the leito's encounter number (NR_ATENDIMENTO).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ocupacoes__pk (URL kwarg, uuid) | n/a | n/a | n/a |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | n/a | n/a |

## Logic
```text
leito = Leito.objects.get(pk=kwargs["ocupacoes__pk"])
InfoPaciente.objects.filter(NR_ATENDIMENTO=leito.nr_atendimento)
```

## Edge cases (as implemented)
List-only viewset (no create/update/destroy exposed here).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/info_paciente.py | 21-23 | 8166c07e | primary |

- Merged from: RULE-paciente-BE-08-034
- Related rules: RULE-MOVIMENTACAO-ADT-020

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
