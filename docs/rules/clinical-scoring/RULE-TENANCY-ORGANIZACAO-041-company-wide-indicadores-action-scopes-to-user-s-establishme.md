# RULE-TENANCY-ORGANIZACAO-041 — Company-wide indicadores action scopes to user's establishments/sectors

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | workflow |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
The indicadores custom action on EmpresaViewSet returns per-establishment status breakdowns (EstabelecimentoStatusSerializer) for only the company's establishments where the requesting user belongs to at least one sector, using currently-active, currently-occupied movimentacoes scoped the same way, ordered alphabetically by establishment name.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| pk (empresa id) | uuid |  |  |
| request.user | object |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| estabelecimentos | array of object |  |

## Logic
```text
movimentacoes = Movimentacao.objects.filter(
    leito__setor__estabelecimento__empresa__id=pk, atual=True, leito__ocupado=True,
    leito__setor__usuarios=request.user)
estabelecimentos = Estabelecimento.objects.filter(
    pk__in=Estabelecimento.objects.filter(empresa=pk, setores__usuarios=request.user).distinct("pk").values("pk")
).order_by("nome")
return EstabelecimentoStatusSerializer(estabelecimentos, context={"movimentacoes": movimentacoes, ...}, many=True).data
```

## Edge cases (as implemented)
A commented 'setores__leitos__ocupado=True' filter on estabelecimentos is not applied - establishments with zero occupied beds still appear if the user is a member of at least one sector. Source also carries an explicit TODO ('Filtrar pelo usuário que fez a requisição, baseado em vinculo') even though the code already does filter by setores__usuarios=request.user - suggesting the author considered this filter insufficient/incomplete relative to a finer-grained 'vinculo' (link) based filter used elsewhere (e.g. RULE-paciente-BE-05-003).

## Verification
- Verdict: UNVERIFIABLE
- Reference: None. EmpresaViewSet.indicadores is a multi-tenancy access-scoping query: it returns per-establishment status breakdowns for a company's establishments where the requesting user belongs to at least one sector, using active (atual=True), occupied (leito__ocupado=True) movimentacoes scoped identically, ordered by establishment name. Pure authorization/query-scoping business logic with no clinical calculation.
- Test vectors:
  - inputs: {'empresa': 'E', 'user_member_of': 'sector in estab A only', 'estabs_in_E': '[A, B]'}; expected_reference: n/a - no authoritative source; actual_legacy: Estabelecimento filter (empresa=pk, setores__usuarios=user) returns only A; B excluded. Ordered by nome.; match: True
  - inputs: {'estab_A': 'user is member but zero occupied beds'}; expected_reference: n/a - no authoritative source; actual_legacy: A still appears - the 'setores__leitos__ocupado=True' filter is commented out; membership alone qualifies the establishment.; match: True
  - inputs: {'movimentacao': "atual=False OR leito.ocupado=False OR sector not user's"}; expected_reference: n/a - no authoritative source; actual_legacy: Excluded from movimentacoes context - filter requires atual=True AND leito__ocupado=True AND leito__setor__usuarios=user.; match: True
- Internal/proprietary access-control and query-scoping rule; flag for internal review. No clinical reference. Source carries an explicit TODO ('Filtrar pelo usuario ... baseado em vinculo') indicating the author viewed the setores__usuarios membership filter as coarser than a finer 'vinculo'-based scope used elsewhere; this is an acknowledged internal-completeness concern, not a reference discrepancy.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/empresa.py | 42-86 | 8166c07e | primary |

- Merged from: RULE-empresa-BE-05-004
- Related rules: RULE-TENANCY-ORGANIZACAO-042, RULE-TENANCY-ORGANIZACAO-038

## Notes
The TODO comment is recorded as evidence of a known/acknowledged incompleteness, not treated as the rule itself - the rule is the code's actual (as-implemented) filter. | Reconciliation: this is the empresa-level instance of the same 'indicadores' custom-action pattern implemented again at establishment scope (estabelecimento-BE-05-010) and sector scope (setor-BE-05-015); each level scopes to a different queryset and returns a different shape, so kept as 3 separate rules cross-referenced via related rather than merged.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
