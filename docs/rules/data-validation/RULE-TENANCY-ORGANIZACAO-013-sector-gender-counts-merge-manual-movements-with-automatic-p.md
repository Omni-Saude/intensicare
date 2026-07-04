# RULE-TENANCY-ORGANIZACAO-013 — Sector gender counts merge manual movements with automatic-pathway beds

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
get_generos produces an M/F/N/O gender-count dict combining active (atual=True) Movimentacao patient genders with automatica-type-leito genders computed separately, summed per key.

## Outputs

| Name | Type | Unit |
|---|---|---|
| generos | object {M, F, N, O} |  |

## Logic

```text
generos = {"M": 0, "F": 0, "N": 0, "O": 0}
generos.update(Movimentacao.objects.filter(atual=True, leito__setor=obj.pk)
               .values_list("paciente__genero").annotate(Count("paciente__genero")))
for key in generos:
    generos[key] += self.generos_automaticos[key]
return generos
```

## Edge cases (as implemented)
Depends on get_generos_e_alertas_automaticos having already populated self.generos_automaticos (triggered from get_alertas, RULE-setor-BE-05-003) - if 'generos' is serialized before 'alertas' this could AttributeError; DRF serializes fields in declaration order and 'alertas' is declared before 'generos' in the Meta/class body, so this is safe under normal DRF field ordering but is an implicit coupling.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal/proprietary business logic: per-sector patient-gender tally (M/F/N/O) merging active Movimentacao patient genders with automatica-leito genders. The gender code set (M/F/N/O, N likely 'nao informado') is an application enum, not an HL7/FHIR/ISO-5218-conformant published value set with defined semantics/cutoffs.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 94-110 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-005`
- Related rules: RULE-TENANCY-ORGANIZACAO-034

## Notes
Gender code 'N' (alongside M/F/O) is unusual - likely 'não informado' (not informed), recorded verbatim as implemented. Cross-field dependency (generos relies on alertas having run first) is a fragile implicit-ordering discrepancy worth a verifier's attention. | Reconciliation: distinct from setor-BE-05-008 (get_total_generos, SetorStatusSerializer, tipo-branching) — this SetorSerializer.get_generos unconditionally sums manual Movimentacao genders + automatica-leito genders. Not a duplicate capture; kept separate, cross-referenced.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
