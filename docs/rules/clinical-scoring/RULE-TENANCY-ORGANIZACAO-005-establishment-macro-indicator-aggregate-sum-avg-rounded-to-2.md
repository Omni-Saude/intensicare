# RULE-TENANCY-ORGANIZACAO-005 — Establishment macro-indicator aggregate (sum/avg rounded to 2 decimals)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_macro_indicadores aggregates MacroIndicadores rows for the establishment code (CD_ESTABELECIMENTO), summing vidas_salvas/obitos/tempo_permanencia/admissao and averaging tx_mortalidade/tx_ocupacao, each rounded to 2 decimal places. Only computed for tipo in ('automatica','homecare'); 'manual' establishments get an empty dict.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.codigo | string |  |
| instance.tipo | string enum |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| vidas_salvas | float |  |
| obitos | float |  |
| tempo_permanencia | float |  |
| tx_mortalidade | float | % |
| tx_ocupacao | float | % |
| admissao | float |  |

## Logic

```text
indicadores = {}
if instance.tipo in ("automatica", "homecare"):
    indicadores = MacroIndicadores.objects.filter(CD_ESTABELECIMENTO=instance.codigo).aggregate(
        vidas_salvas=Round(Sum("VIDAS_SALVAS"), precision=2),
        obitos=Round(Sum("OBITOS"), precision=2),
        tempo_permanencia=Round(Sum("TEMPO_PERMANENCIA"), precision=2),
        tx_mortalidade=Round(Avg("TX_MORTALIDADE"), precision=2),
        tx_ocupacao=Round(Avg("TX_OCUPACAO"), precision=2),
        admissao=Round(Sum("ADMISSAO"), precision=2))
return indicadores
```

## Edge cases (as implemented)
If no MacroIndicadores rows match CD_ESTABELECIMENTO, Django's Sum/Avg aggregate over an empty queryset returns None (not 0/0.0) for each key, since no explicit default/Coalesce is used - the resulting dict will contain None values rather than raising.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical/statistical standard governs this proprietary establishment-level macro-indicator aggregation (which of vidas_salvas/obitos/tempo_permanencia/admissao to Sum vs which of tx_mortalidade/tx_ocupacao to Avg, and the 2-decimal Round). Internal IntensiCare/Trilhas business rule.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/estabelecimento.py` | 151-164 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-004`
- Related rules: RULE-TENANCY-ORGANIZACAO-006

## Notes
Version/implementation difference vs. the sector-level RULE-setor-BE-05-009 (single-record .get() with bare except, no rounding, keyed by an additional CD_SETOR_ATENDIMENTO) - cross-reference for a verifier. | Reconciliation: sector-level counterpart (see related) uses a materially different implementation (single-record .get() with bare except, no rounding) — flagged there as DISCREPANCY. Kept as separate rules since each aggregates a different queryset (establishment-wide vs single sector).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
