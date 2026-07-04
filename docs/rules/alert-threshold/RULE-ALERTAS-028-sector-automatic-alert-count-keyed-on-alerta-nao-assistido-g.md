# RULE-ALERTAS-028 — Sector automatic-alert count keyed on alerta_nao_assistido (get_total_alertas_automaticos)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | scoring |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | alertas |

## Rule

Sector 'total_alertas' KPI for automatica/homecare sectors: counts occupied beds bucketed by leito.alerta_nao_assistido (the attendance-ignoring per-bed alert color, RULE-ALERTAS-007) into {VERMELHO, NEUTRO, AMARELO}. Feeds setor/estabelecimento 'total_alertas' (setor.py:234, estabelecimento.py:192).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| leitos | iterable[Leito] | - | occupied beds |
| leito.alerta_nao_assistido | string | - | alert color (RULE-ALERTAS-007) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alertas {VERMELHO, NEUTRO, AMARELO, ...} | dict[str,int] | bed count |

## Logic

```text
alertas = {"VERMELHO": 0, "NEUTRO": 0, "AMARELO": 0}
for leito in leitos:                      # leitos already filtered to occupied
    if leito.ocupado:
        alertas[leito.alerta_nao_assistido] = alertas.get(leito.alerta_nao_assistido, 0) + 1
return alertas
```

## Edge cases (as implemented)

Keys on leito.alerta_nao_assistido (the alert IGNORING attendance), not the assisted-adjusted alert. Because it uses alertas.get(k, 0) + 1 and then assigns alertas[k], any color outside the three seeded keys (e.g. LARANJA, or None) creates a NEW bucket in the returned dict rather than being ignored. Non-occupied beds are skipped.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 750-762 | `8166c07e` | primary |

- Merged from: RULE-gap6-02
- Related rules: RULE-ALERTAS-007, RULE-ALERTAS-027, RULE-TENANCY-ORGANIZACAO-035

## Notes

Feeds setor/estabelecimento 'total_alertas' for automatica/homecare sectors. Distinct from RULE-ALERTAS-002 (calcular_total_alertas), which buckets movimentacoes by the four manual-pathway alerts; this counter keys on the precomputed per-bed alerta_nao_assistido. Previously uncited: RULE-TENANCY-ORGANIZACAO-035 cites the serializer dispatch and the manual-path Count on alerta_movimentacao, not this automatica aggregation.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
