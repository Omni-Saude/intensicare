# RULE-ALERTAS-002 — Aggregate alert counts across movimentacoes

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | scoring |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Counts beds/movimentacoes by worst manual-pathway alert among (trilha_sepse, trilha_ventilacao, trilha_sedacao, trilha_estabilidade), with VERMELHO precedence.

## Inputs

- ids_movimentacoes (list[uuid])

## Outputs

- counts {NEUTRO, AMARELO, VERMELHO} (dict[str,int])

## Logic

```text
for each movimentacao's tuple of
    (trilha_sepse.alerta, trilha_ventilacao.alerta,
     trilha_sedacao.alerta, trilha_estabilidade.alerta):
  if "VERMELHO" in tuple: VERMELHO += 1
  elif "AMARELO" in tuple: AMARELO += 1
  else: NEUTRO += 1
```

## Edge cases (as implemented)

A movimentacao with all-null pathway alerts counts as NEUTRO. Only these four manual pathways considered (not antimicrobiano/nutricao/etc).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published clinical reference. Internal business rule (Leito.calcular_total_alertas, core/models/leito.py:709-736): aggregates a per-bed count bucketed by the worst manual-pathway alert color among four internal care pathways (trilha_sepse, trilha_ventilacao, trilha_sedacao, trilha_estabilidade) using a fixed VERMELHO > AMARELO > NEUTRO precedence. The alert colors themselves derive from RULE-ALERTAS-003; this rule only tallies them. No guideline/paper defines this red>yellow>neutral bed-census aggregation.

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a - counts of beds/movimentacoes (dimensionless) |
| ranges | n/a - inputs are enum strings {VERMELHO, AMARELO, NEUTRO, null}; each movimentacao contributes exactly 1 to exactly one bucket |
| rounding | n/a - integer counters |
| cutoffs | Precedence membership test verified: 'if VERMELHO in tuple -> VERMELHO; elif AMARELO in tuple -> AMARELO; else NEUTRO'. Matches catalog logic exactly (leito.py:731-736). All-null or all-NEUTRO tuples fall to the else -> NEUTRO bucket, as documented in edge_cases. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| tuple=(VERMELHO, NEUTRO, AMARELO, NEUTRO) | n/a - internal-consistency: VERMELHO precedence -> VERMELHO bucket | VERMELHO += 1 | yes |
| tuple=(NEUTRO, AMARELO, NEUTRO, None) | n/a - internal-consistency: no VERMELHO, AMARELO present -> AMARELO bucket | AMARELO += 1 | yes |
| tuple=(None, None, None, None) | n/a - internal-consistency: all-null -> else -> NEUTRO bucket | NEUTRO += 1 | yes |
| tuple=(NEUTRO, NEUTRO, NEUTRO, NEUTRO) | n/a - internal-consistency: no VERMELHO/AMARELO -> else -> NEUTRO bucket | NEUTRO += 1 | yes |

**Verifier notes**

Legacy source verified @8166c07 (core/models/leito.py:709-736); catalog pseudocode matches the implementation exactly, including the substring/membership `in tuple` precedence and the else->NEUTRO fallthrough for null/neutral tuples. Only the four manual pathways are aggregated (antimicrobiano/nutricao/etc. excluded), as documented. This is a pure UI/census counter with no published-reference surface (no equation, units, or clinical cutoff to audit). The upstream correctness of the VERMELHO/AMARELO/NEUTRO colors it counts depends on RULE-ALERTAS-003 (which is separately DISCREPANCY-flagged); this aggregator's own logic is internally consistent and behaviorally correct for its contract. Flagged for internal review only; not treated as wrong.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 709-736 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-BE-04-023`

**Related rules:**

- [RULE-ALERTAS-006](RULE-ALERTAS-006-bed-alert-color-aggregation-get-alerta-leito-with-sepse-lara.md)

## Notes

Sibling counters in the same model: get_total_alertas_automaticos (738-762) counts by leito.alerta_nao_assistido; get_total_generos_e_alertas_automaticos (764-816) additionally tallies genero {M,F,N,O}.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
