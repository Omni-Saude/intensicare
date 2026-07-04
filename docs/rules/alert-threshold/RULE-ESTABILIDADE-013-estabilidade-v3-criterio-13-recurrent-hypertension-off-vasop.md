# RULE-ESTABILIDADE-013 — Estabilidade v3 criterio_13 - recurrent hypertension off vasopressor (AMARELO, wired)

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Intended: PAS>155 OR PAD>90 in the last 2 balance records AND no noradrenaline in last 4h AND no ischemic-stroke (AVCi / I64) admission diagnosis. WIRED (contributes to AMARELO).

## Inputs

| name | type | unit |
|---|---|---|
| balanco.pas | float | mmHg |
| balanco.pad | float | mmHg |
| balanco.qt_vol_nora | float | ml/h |
| evolucao.diagnostico_1..4 | string |  |

## Outputs

| name | type |
|---|---|
| criterio_13 | boolean |

## Logic

```text
return all([
  balanco_4h.filter(pas__gt=155, pad__gt=90).count() == 2,   # docstring: PAS>155 OU PAD>90 nos ultimos 2 lancamentos
  not balanco_4h.filter(qt_vol_nora__gt=0).exists(),
  not list(filter(lambda x: x.startswith("I64"),
                  vars(ultima_evolucao).fromkeys(("diagnostico_1","diagnostico_2","diagnostico_3","diagnostico_4")))),
]) if (ultima_evolucao and balanco_4h) else False
```

## Edge cases (as implemented)

(1) pas>155 AND pad>90 in the SAME record (comma = AND) with count exactly == 2, whereas the docstring says "PAS>155 OU PAD>90 nos ultimos 2 lancamentos"; (2) the I64/AVCi exclusion is vacuously always True — `vars(evolucao).fromkeys((...))` builds a dict keyed by the field NAMES ("diagnostico_1".."diagnostico_4") with None values, so filtering keys for startswith("I64") always yields [] and `not []` == True.

## Divergence

Code vs docstring: (1) PAS/PAD combined with AND vs documented OR; (2) `.count() == 2` (exactly two) vs documented "nos ultimos 2 lancamentos"; (3) the AVCi (ICD I64) diagnosis gate is non-functional (fromkeys bug) and never excludes anyone.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 671-709 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-073`

**Related rules:**

- [RULE-ESTABILIDADE-014](RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md)

## Notes

Facade criterio_13 = 'Hipertensao recorrente, otimizar anti-hipertensivos'. The fromkeys diagnosis bug is a shared systemic pattern (Phase-1 cross-ref RULE-systemic-BE-03-001). verify:false — generic hypertension thresholds, no specific published score.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
