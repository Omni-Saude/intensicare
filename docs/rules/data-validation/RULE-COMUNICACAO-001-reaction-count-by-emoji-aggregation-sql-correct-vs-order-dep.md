# RULE-COMUNICACAO-001 — Reaction-count-by-emoji aggregation — SQL-correct vs order-dependent duplicate implementations

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
Two backend code paths independently compute 'reaction counts grouped by emoji' for an observation's reactions, and they diverge. (1) ObservacaoSerializer.get_reacoes returns instance.reacoes.values('emoji').annotate(total=Count('emoji')) — a SQL-level GROUP BY, correct regardless of row ordering. (2) ReacaoViewSet.list instead aggregates the same kind of data via Python's itertools.groupby over filter_queryset(get_queryset()) with NO explicit .order_by('emoji'), and the Reacao model itself declares no Meta.ordering (confirmed against core/models/reacao.py: Meta only sets db_table and unique_together=('observacao','usuario')) — so groupby only merges emoji runs that are already consecutive in whatever order the DB happens to return rows in.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.reacoes / queryset of Reacao | queryset | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| reacoes / payload | array of {emoji, total[, usuarios]} | — |

## Logic
```text
# (A) ObservacaoSerializer.get_reacoes — core/api/v1/serializers/observacao.py:155-156 (CORRECT, order-independent)
def get_reacoes(instance):
    return list(instance.reacoes.values("emoji").annotate(total=Count("emoji")))

# (B) ReacaoViewSet.list — core/api/v1/views/reacao.py:24-27,38-51 (BUGGY, order-dependent)
def get_queryset(self):
    return Reacao.objects.select_related("observacao","usuario").filter(observacao=kwargs.get("observacoes__pk"))
    # NOTE: no .order_by('emoji'); Reacao.Meta has no ordering either
def list(self, request, *args, **kwargs):
    qs = self.filter_queryset(self.get_queryset())
    payload = []
    for emoji, reacoes in groupby(qs, key=lambda r: r.emoji):   # itertools.groupby
        reacoes = list(reacoes)
        usuarios = [r.usuario for r in reacoes]
        payload.append({"emoji": emoji, "total": len(reacoes), "usuarios": UsuarioResponsavelSerializer(usuarios, many=True).data})
    return Response(payload)
```

## Edge cases (as implemented)
(A) No reactions -> empty list; correct total regardless of insertion order. (B) itertools.groupby only merges CONSECUTIVE same-key items: two reactions with the same emoji separated (in whatever default/PK order Postgres returns them) by a reaction with a different emoji will appear as TWO separate {emoji,total} entries in the ReacaoViewSet.list response, each under-counting the true total for that emoji. Verified: Reacao model (core/models/reacao.py) declares only db_table and unique_together=('observacao','usuario') in Meta — no ordering — so this failure mode is live, not merely theoretical.

## Divergence
ObservacaoSerializer.get_reacoes (observacao.py:155-156) uses a SQL-level annotate(Count) — correct under any row ordering. ReacaoViewSet.list (reacao.py:24-27,38-51) uses itertools.groupby with no order_by and no model-level default ordering — can silently split/undercount a single emoji's total into multiple response entries when reactions of that emoji are not contiguous in DB return order. Same conceptual computation ('reactions grouped by emoji for an observation'), two backend call sites, materially different correctness guarantees.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. This is an internal data-aggregation (reaction-count-by-emoji) business rule; correctness is defined only by the codebase's own intended semantics (a SQL GROUP BY over reactions). Python stdlib docs for itertools.groupby are the only external authority relevant, and only for the mechanism, not the clinical meaning.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/observacao.py | 155-156 | 8166c07e | primary |
| ahlabs-trilhas | core/api/v1/views/reacao.py | 24-27, 38-51 | 8166c07e | variant |
- Merged from: RULE-observacao-BE-05-002, RULE-reacao-BE-05-003
- Related rules: RULE-COMUNICACAO-002, RULE-COMUNICACAO-037, RULE-COMUNICACAO-038

## Notes
Cannot confirm from this partition alone whether Reacao's model Meta.ordering happens to be by emoji (which would make this safe in practice) - the Reacao model is out of scope (core/models). Flagged for a verifier with access to core/models/reacao.py.

---

Reconciled during Phase-2: confirmed via direct inspection of core/models/reacao.py (Meta has no ordering) that the groupby-based endpoint's correctness claim in its original note ('cannot confirm ... out of scope') resolves to CONFIRMED DISCREPANCY, not merely a theoretical risk.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
