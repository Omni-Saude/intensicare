# RULE-MOVIMENTACAO-ADT-049 — Test/temporary bed exclusion filter (AND semantics)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Before classification, a base queryset excludes "test" beds. As implemented the exclusion only removes a row when ALL THREE conditions hold together: patient name contains "teste" AND bed description contains "teste" AND bed-type description contains "temp".

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| nm_paciente | string |  |  |
| ds_leito | string |  |  |
| ds_tipo_leito | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| excluded | boolean |  |

## Logic
```text
base = EstabelecimentoSetorLeitoTasy.objects.using("oracle").exclude(
    nm_paciente__icontains="teste",
    ds_leito__icontains="teste",
    ds_tipo_leito__icontains="temp",
)
# exclude(**kwargs) => NOT (nm_paciente ILIKE %teste% AND ds_leito ILIKE %teste% AND ds_tipo_leito ILIKE %temp%)
```

## Edge cases (as implemented)
Case-insensitive substring match. Because the three predicates are AND-combined inside a single exclude(), a real test bed that matches only one or two of the three tokens is NOT excluded.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/etl/estabelecimento_setor_leito.py` | 118-122 | `8166c07e` | primary |

- Merged from: RULE-leito-BE-02-002
- Related rules: RULE-MOVIMENTACAO-ADT-021

## Notes
AMBIGUOUS: naming ("teste"/"temp") strongly suggests intent was to drop any test/temporary row (OR semantics). Implemented AND semantics make the filter far narrower than the apparent intent. Recorded verbatim.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
