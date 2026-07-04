# RULE-TENANCY-ORGANIZACAO-006 — Sector macro-indicator single-record fetch with silent failure

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | formula |
| Status | DISCREPANCY |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_macro_indicadores fetches a single MacroIndicadores row keyed by (CD_ESTABELECIMENTO, CD_SETOR_ATENDIMENTO) matching the sector; if found, raw (un-rounded) values for vidas_salvas/obitos/tempo_permanencia/tx_mortalidade/tx_ocupacao/admissao are returned. A bare `except:` clause silently swallows ANY exception (DoesNotExist, MultipleObjectsReturned, or anything else) and returns an empty dict.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.estabelecimento.codigo | string |  |
| instance.codigo | string |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| indicadores | object {vidas_salvas, obitos, tempo_permanencia, tx_mortalidade, tx_ocupacao, admissao} \| {} |  |

## Logic

```text
indicadores = {}
if instance.tipo in ("automatica", "homecare"):
    try:
        obj = MacroIndicadores.objects.get(
            CD_ESTABELECIMENTO=instance.estabelecimento.codigo,
            CD_SETOR_ATENDIMENTO=instance.codigo)
        indicadores = {
            "vidas_salvas": obj.VIDAS_SALVAS, "obitos": obj.OBITOS,
            "tempo_permanencia": obj.TEMPO_PERMANENCIA, "tx_mortalidade": obj.TX_MORTALIDADE,
            "tx_ocupacao": obj.TX_OCUPACAO, "admissao": obj.ADMISSAO}
    except:
        return indicadores   # {}
return indicadores
```

## Edge cases (as implemented)
For 'manual' sectors, indicadores stays {} unconditionally. No rounding is applied here (contrast with EstabelecimentoStatusSerializer's version which rounds to 2 decimals via aggregate/Round). A MultipleObjectsReturned (more than one MacroIndicadores row matching the same estabelecimento+setor codes) is silently treated the same as 'not found'.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal proprietary data-fetch rule: SetorStatusSerializer.get_macro_indicadores single-record fetch of a MacroIndicadores row keyed by (CD_ESTABELECIMENTO, CD_SETOR_ATENDIMENTO). Legacy verbatim confirmed at core/api/v1/serializers/setor.py:187-206 @ 8166c07.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 187-206 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-009`
- Related rules: RULE-TENANCY-ORGANIZACAO-005

## Notes
Version/implementation difference vs. RULE-estabelecimento-BE-05-004 (aggregate Sum/Avg with Round(precision=2) across possibly multiple establishment-wide rows, no try/except at all). Cross-reference for a verifier deciding which behavior is 'correct'. | Reconciliation: establishment-level counterpart (see related) uses Sum/Avg aggregation with explicit Round(precision=2) and no exception handling — this sector-level version is a materially different (less robust) implementation of the same conceptual indicator fetch. Kept as separate rules (different queryset scope), not merged; both flagged for a verifier deciding canonical behavior.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
