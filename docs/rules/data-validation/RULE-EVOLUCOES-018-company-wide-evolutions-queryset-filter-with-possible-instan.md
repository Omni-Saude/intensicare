# RULE-EVOLUCOES-018 — Company-wide evolutions queryset filter with possible instance-vs-id type mismatch

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | evolucoes |

## Rule
EvolucoesEmpresaViewSet.get_queryset filters Formulario by leito__setor__estabelecimento__empresa_id=empresa_pk, where empresa_pk is assigned directly from self.request.empresa - based on the pattern used throughout the rest of this partition (e.g. dados_offline.py: setattr(request, 'empresa', Empresa.objects.get(...))), request.empresa is an Empresa MODEL INSTANCE, not a raw id/pk value. Filtering an '_id'-suffixed field against a full model instance rather than its .pk is untested from this partition alone and may either work (if Django's ORM coerces it) or fail/misbehave depending on the primary key field type.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| request.empresa |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset |  |  |

## Logic
```text
empresa_pk = request.empresa           # NOTE: likely an Empresa instance, not a raw pk, despite the variable name
queryset = Formulario.objects.filter(leito__setor__estabelecimento__empresa_id=empresa_pk)
return queryset
```

## Edge cases (as implemented)
If Empresa's primary key is a UUIDField, Django's ORM query-value adaptation for an '_id' exact-lookup typically expects a UUID/str/int, not a model instance - passing an instance here could raise a database adaptation error, or Django could resolve it transparently by extracting .pk (behavior depends on Django/psycopg version, not confirmable from this partition alone).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/evolucoes_empresa.py` | 19-24 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-05-002
- Related rules: none

## Notes
Best interpretation: the variable name 'empresa_pk' suggests the author intended a raw pk value, but assigns request.empresa (an instance per the convention seen in dados_offline.py) without calling .pk - flagged AMBIGUOUS/DISCREPANCY-adjacent for a verifier with access to core/models/empresa.py (to confirm the pk field type) and to actual runtime behavior. permission_trilhas=('can_access_relatorio_evolucao',) gates this viewset.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
