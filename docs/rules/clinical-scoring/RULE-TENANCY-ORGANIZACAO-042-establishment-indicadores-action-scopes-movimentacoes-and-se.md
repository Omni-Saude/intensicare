# RULE-TENANCY-ORGANIZACAO-042 — Establishment indicadores action scopes movimentacoes and setores to the requesting user

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | workflow |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The indicadores custom action builds a per-sector status breakdown (via SetorStatusSerializer) for only the sectors of this establishment where the requesting user is a member, using currently-active (atual=True), currently-occupied movimentacoes scoped the same way, ordered alphabetically by sector name.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.user | object |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| setores | array of object |  |

## Logic
```text
movimentacoes = Movimentacao.objects.filter(atual=True, leito__setor__estabelecimento=estabelecimento, leito__setor__usuarios=request.user)
setores = Setor.objects.filter(pk__in=Setor.objects.filter(estabelecimento=estabelecimento, usuarios=request.user).distinct("pk").values("pk")).order_by("nome")
return SetorStatusSerializer(setores, context={"movimentacoes": movimentacoes, ...}, many=True).data
```

## Edge cases (as implemented)
A commented-out 'leitos__ocupado=True' filter on the setores query means sectors with zero currently-occupied beds are still included in the list, as long as the user is a member.

## Verification
- Verdict: UNVERIFIABLE
- Reference: None. EstabelecimentoViewSet.indicadores is a multi-tenancy access-scoping query: it builds a per-sector status breakdown for the sectors of one establishment where the requesting user is a member, using active (atual=True) movimentacoes scoped identically, ordered by sector name. Pure authorization/query-scoping business logic with no clinical calculation.
- Test vectors:
  - inputs: {'estab': 'X', 'user_member_of': 'S1 only', 'sectors_in_X': '[S1, S2]'}; expected_reference: n/a - no authoritative source; actual_legacy: Setor filter (estabelecimento=X, usuarios=user) returns only S1; S2 excluded. Ordered by nome.; match: True
  - inputs: {'sector_S1': 'user is member but zero occupied beds'}; expected_reference: n/a - no authoritative source; actual_legacy: S1 still appears - the 'leitos__ocupado=True' filter is commented out; membership alone qualifies the sector.; match: True
  - inputs: {'movimentacao': "atual=False OR sector not user's"}; expected_reference: n/a - no authoritative source; actual_legacy: Excluded from qs context - filter requires atual=True AND leito__setor__estabelecimento=X AND leito__setor__usuarios=user. Note: unlike RULE-041, this movimentacoes query does NOT filter on leito__ocupado=True.; match: True
- Internal/proprietary access-control and query-scoping rule; flag for internal review. No clinical reference. Establishment-level instance of the same 'indicadores' scoping pattern as RULE-041 (company level) and RULE-038 (sector level). Observed internal inconsistency worth an engineering note: RULE-041's movimentacoes query filters leito__ocupado=True whereas this establishment-level query omits that filter - a scoping asymmetry between sibling endpoints, not a clinical-reference discrepancy.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/estabelecimento.py | 55-87 | 8166c07e | primary |

- Merged from: RULE-estabelecimento-BE-05-010
- Related rules: RULE-TENANCY-ORGANIZACAO-041, RULE-TENANCY-ORGANIZACAO-038

## Notes
Reconciliation: establishment-level instance of the same 'indicadores' action pattern as empresa-BE-05-004 (one level up) and setor-BE-05-015 (one level down); kept separate, cross-referenced.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
