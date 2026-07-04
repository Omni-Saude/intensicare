# RULE-EVOLUCOES-005 — Company evolutions - patient name resolved by attendance number

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
EvolucoesEmpresaSerializer.get_nome_paciente looks up a Paciente by nr_atendimento matching the Formulario's own nr_atendimento, returning the patient's 'nome' attribute or None if no matching patient exists.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.nr_atendimento |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| nome_paciente |  |  |

## Logic
```text
return getattr(Paciente.objects.filter(nr_atendimento=instance.nr_atendimento).first(), "nome", None)
```

## Edge cases (as implemented)
getattr with a default handles both 'no matching patient' (first() is None) and, defensively, a missing 'nome' attribute - both resolve to None rather than raising.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical/standard reference - this is an internal ORM name-resolution business rule (look up Paciente by nr_atendimento, return .nome or None). Confirmed by the rule's own note that it is a trivial name lookup, not a clinical calculation.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/evolucoes_empresa.py` | 18-23 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-05-001
- Related rules: none

## Notes
verify=true is set mechanically (Phase-1 type='formula'); in substance this is a trivial ORM name lookup (getattr on Paciente...), NOT a clinical calculation with a published anchor.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
