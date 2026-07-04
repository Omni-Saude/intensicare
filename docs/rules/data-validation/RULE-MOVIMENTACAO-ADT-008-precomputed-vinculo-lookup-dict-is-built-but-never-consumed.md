# RULE-MOVIMENTACAO-ADT-008 — Precomputed vinculo lookup dict is built but never consumed by the serializer

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
SetorPacienteViewSet.get_serializer_context precomputes a dict of existing UsuarioSetorPaciente link objects keyed by generate_key_access_vinculo_paciente_leito(paciente_pk, setor_pk, usuario_pk) and stores it in context['vinculos_paciente_leito'] - but SetorPacienteSerializer.get_vinculo (the only consumer) instead issues its OWN direct DB query per patient instance, never reading context['vinculos_paciente_leito']. The precomputed dict is dead/unused, and the serializer performs one query per row (N+1).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.usuario__pk | uuid |  |  |
| kwargs.setor__pk | uuid |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| context.vinculos_paciente_leito | object, dead/unused |  |

## Logic
```text
# view (builds dict, never read):
qs = get_queryset().values_list("pk", flat=True)
payload_vinculos = {}
for vinculo in UsuarioSetorPaciente.objects.filter(pk__in=qs, usuario=usuario_pk, setor=setor_pk):
    payload_vinculos[generate_key_access_vinculo_paciente_leito(vinculo.paciente.get_pk, setor_pk, usuario_pk)] = vinculo
context["vinculos_paciente_leito"] = payload_vinculos

# serializer (actual behavior, ignores the above):
def get_vinculo(instance):
    kwargs = self.context["view"].kwargs
    vinculo = UsuarioSetorPaciente.objects.filter(
        usuario=kwargs.get("usuario__pk"), paciente=instance, setor=kwargs.get("setor__pk")
    ).first()
    return vinculo.get_pk if vinculo else None
```

## Edge cases (as implemented)
For N patients in the list, this results in N additional DB queries (one per get_vinculo call) rather than a single upfront query - a performance discrepancy relative to the apparent intent of the precomputed context dict.

## Divergence
Intent-vs-implementation discrepancy (single-implementation dead code). The view precomputes context['vinculos_paciente_leito'] but the serializer's get_vinculo never reads it, doing a per-row query instead. Recorded verbatim; not corrected.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference exists. Software correctness finding (dead precomputed context dict + N+1 per-row query in SetorPacienteViewSet.get_serializer_context vs SetorPacienteSerializer.get_vinculo). Verified against legacy source only.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/paciente.py | 44-63 | 8166c07e | primary |
- Merged from: RULE-paciente-BE-05-002
- Related rules: RULE-MOVIMENTACAO-ADT-042, RULE-MOVIMENTACAO-ADT-045

## Notes
Consumer side: core/api/v1/serializers/paciente.py lines 63-76 (SetorPacienteSerializer.get_vinculo).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
