# RULE-BALANCO-HIDRICO-013 — Fluid-balance visao-geral 2-hour time-bucketing (08:00-start day, view facade + utils impl)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Builds the fluid-balance overview grid: for each distinct item name (nome) in a balanco, sum quantidade into twelve fixed 2-hour buckets. Bucket labels/edges start at 08:00 and wrap through 06:00-08:00, using America/Sao_Paulo local time.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| modelo | — | — | — |
| balanco_pk | — | — | — |
| tipo_balanco | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| payload | mL per bucket | — |

## Logic
```text
horario labels = ["08:00","10:00","12:00","14:00","16:00","18:00","20:00","22:00","00:00","02:00","04:00","06:00"]
bucket edges (ref) = [[8,10],[10,12],[12,14],[14,16],[16,18],[18,20],[20,22],[22,00],[0,2],[2,4],[4,6],[6,8]]
qs = modelo.objects_without_deleted.filter(balanco_id == balanco_pk)
for each distinct nome in qs:
    for (h_ini, h_fim) in [(time(a),time(b)) for a,b in ref]:
        valor = qs.annotate(horario = TruncTime(criado_em, tz=America/Sao_Paulo))
                  .filter(nome==nome, horario__range=[h_ini, h_fim])
                  .aggregate(Sum(quantidade))
        append valor or 0
```

## Edge cases (as implemented)
Bucket [22,00] becomes range [22:00:00, 00:00:00]; since 22:00 > 00:00 this SQL BETWEEN is empty, so the 22:00-00:00 slot ALWAYS aggregates to 0 (data there is lost). horario__range is inclusive on both edges, so a record at an exact boundary (e.g. 10:00:00) is counted in two adjacent buckets. Uses objects_without_deleted (soft-delete aware). TruncTime converts to America/Sao_Paulo before comparing.

## Divergence
Bucket [22,00] becomes SQL BETWEEN 22:00:00 and 00:00:00 (inverted range) so the 22:00-00:00 slot ALWAYS aggregates to 0 and its data is lost; horario__range is inclusive on both edges so a record at an exact boundary (e.g. 10:00:00) is double-counted in two adjacent buckets. The view action (balanco_hidrico.py:66-88) and the utils implementation (utils.py:288-358) carry identical 12-slot labels [08:00..06:00]; the utils layer holds the buggy TruncTime bucketing.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: No authoritative published clinical reference governs a 2-hour time-bucketing display grid for a fluid-balance overview — this is an internal presentation/aggregation algorithm. The only externally-anchored concept is the 24h I&O charting window (Nurseslabs I&O), which the grid is meant to partition; the bucketing math itself is proprietary. (https://nurseslabs.com/monitoring-fluid-intake-and-output-io/)
- Test vectors: 1/3 match
- Extraction-flagged DISCREPANCY confirmed against the legacy source. Two defects: (1) the [22, 00] bucket becomes SQL BETWEEN 22:00:00 AND 00:00:00 (inverted range), so the 22:00-00:00 slot ALWAYS aggregates to 0 and any fluid intake/output charted in that 2-hour window is silently dropped from the overview grid; (2) horario__range is inclusive on both edges, so a record at an exact 2-hour boundary (e.g. 10:00:00) is double-counted into two adjacent slots. No external clinical reference dictates the bucket algorithm, so this is a code-correctness defect vs the grid's own stated intent. Clinical impact rated MODERATE: silently losing all late-evening (22:00-00:00) fluid entries and double-counting boundary entries can materially distort the visual fluid-balance overview that feeds the balanco PDF (cria_payload_de_envio_ahmdocs -> pdf_balanco_hidrico*.html); note the running 24h numeric total (balanco_24h, RULE-014/015) is maintained separately and is unaffected by this grid bug. Flag for internal engineering review.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 288-358 | 8166c07e | primary |
| ahlabs-trilhas | trilha_homecare/api/v1/views/balanco_hidrico.py | 66-88 | 8166c07e | duplicate |
- Merged from: RULE-balancohidrico-BE-09-007, RULE-balanco-BE-08-009
- Related rules: RULE-BALANCO-HIDRICO-025, RULE-BALANCO-HIDRICO-027, RULE-BALANCO-HIDRICO-044, RULE-BALANCO-HIDRICO-054

## Notes
DISCREPANCY: the 22:00->00:00 bucket is an empty inverted range (loses late-evening data), and inclusive endpoints double-count boundary timestamps. Consumed by cria_payload_de_envio_ahmdocs to render the balanco PDF (pdf_balanco_hidrico*.html).

Merged catalog-facade (BalancoHidricoViewSet.visao_geral returns the 12 fixed labels and spreads get_visao_geral for Entrada+Saida) with the precise predicate implementation in trilha_homecare/utils.py get_visao_geral (chosen as primary logic). Uses objects_without_deleted (soft-delete aware) and TruncTime -> America/Sao_Paulo. Consumed by cria_payload_de_envio_ahmdocs to render pdf_balanco_hidrico*.html; frontend consumer divergence is RULE-BALANCO-HIDRICO-025.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
