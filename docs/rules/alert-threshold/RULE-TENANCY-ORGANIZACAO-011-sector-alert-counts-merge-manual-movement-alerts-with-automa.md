# RULE-TENANCY-ORGANIZACAO-011 — Sector alert counts merge manual movement alerts with automatic-pathway alerts

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_alertas produces a VERMELHO/AMARELO/NEUTRO count dict by combining two sources: (1) counts of alerta_movimentacao from currently-active (atual=True) Movimentacao records for the sector's beds (manual-type tracking), and (2) alertas_automaticos computed separately over the sector's automatica-type leitos via Leito.get_total_generos_e_alertas_automaticos. The two sources are summed per alert-level key.

## Inputs

| Name | Type | Unit |
|---|---|---|
| obj.leitos (filtered tipo=automatica) | queryset of Leito |  |
| Movimentacao(atual=True, leito__setor=obj) | queryset |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alertas | object {VERMELHO, AMARELO, NEUTRO} |  |

## Logic

```text
self.generos_automaticos, self.alertas_automaticos = Leito.get_total_generos_e_alertas_automaticos(
    leitos=obj.leitos.all().filter(tipo="automatica"))
alertas = {"VERMELHO": 0, "AMARELO": 0, "NEUTRO": 0}
alertas.update(Movimentacao.objects.filter(atual=True, leito__setor=obj.pk)
               .values_list("alerta_movimentacao").annotate(Count("alerta_movimentacao")))
for key in alertas:
    alertas[key] += self.alertas_automaticos[key]
return alertas
```

## Edge cases (as implemented)
get_generos_e_alertas_automaticos must run before get_alertas reads self.alertas_automaticos - it is called as the first line inside get_alertas itself, so ordering is self-contained and safe regardless of DRF field serialization order.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal/proprietary business logic: per-sector alert-level tally (VERMELHO/AMARELO/NEUTRO) that sums manual Movimentacao alerts with automatica-pathway bed alerts. This is an application-specific aggregation, not a validated clinical scale, scoring system, or guideline-defined algorithm.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 56-79 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-003`
- Related rules: RULE-TENANCY-ORGANIZACAO-035

## Notes
Leito.get_total_generos_e_alertas_automaticos is defined in core/models, out of this partition's scope; its output shape (dict with VERMELHO/AMARELO/NEUTRO keys) is inferred from usage here. | Reconciliation: distinct from RULE-TENANCY-ORGANIZACAO (setor-BE-05-010, get_total_alertas) which computes a similarly-shaped VERMELHO/AMARELO/NEUTRO dict but in a different serializer class (SetorStatusSerializer) using context-supplied movimentacoes and tipo-branching, rather than this SetorSerializer.get_alertas which unconditionally sums manual + automatica sources. Not a duplicate capture; kept separate.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
