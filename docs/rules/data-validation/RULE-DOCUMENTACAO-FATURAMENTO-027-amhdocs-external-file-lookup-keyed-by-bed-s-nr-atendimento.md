# RULE-DOCUMENTACAO-FATURAMENTO-027 — AMHDocs external file lookup keyed by bed's nr_atendimento

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
get_nr_atendimento (used to build both the internal create() call and the external AMHDocs proxy URL) resolves nr_atendimento from the Leito identified by the 'ocupacoes__pk' URL kwarg.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.ocupacoes__pk | uuid |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| nr_atendimento | string |  |

## Logic
```text
leito = get_object_or_404(Leito.objects.all(), pk=kwargs["ocupacoes__pk"])
return str(leito.nr_atendimento)
```

## Edge cases (as implemented)
Unlike the observacao/assistido views, here 'ocupacoes__pk' is ALWAYS treated as a Leito pk directly (no Movimentacao fallback attempted).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. This is proprietary integration/routing code: get_nr_atendimento resolves a bed's encounter number by primary-key lookup on the internal Leito model (Django ORM get_object_or_404). "nr_atendimento" (encounter/attendance number) is an internal Tasy/AMHDocs identifier, not a standardized code governed by any external body. Marked type=formula in the catalog only because it is a mechanical field derivation, not a clinical formula.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/integracao_amhdocs.py | 23-33 | 8166c07e | primary |
- Merged from: RULE-integracao-BE-05-001
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-028

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
