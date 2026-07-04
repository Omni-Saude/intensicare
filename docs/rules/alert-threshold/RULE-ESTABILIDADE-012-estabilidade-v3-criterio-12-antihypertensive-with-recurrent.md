# RULE-ESTABILIDADE-012 — Estabilidade v3 criterio_12 - antihypertensive with recurrent hypotension (AMARELO, wired)

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
Any scheduled antihypertensive prescribed AND more than 2 balance records with PAS<90 AND PAD<60 in last 6h. WIRED (contributes to AMARELO alert).

## Inputs

| name | type | unit | same as RULE-010) |
|---|---|---|---|
| balanco.pas | float | mmHg |  |
| balanco.pad | float | mmHg |  |
| cpoe antihypertensives (16-drug list | float |  |  |

## Outputs

| name | type |
|---|---|
| criterio_12 | boolean |

## Logic

```text
return all([
  balanco_6h.filter(pas__lt=90, pad__lt=60).count() > 2,     # docstring: PAS<90 OU PAD<60 (OR); code ANDs them
  any([ get_number(cpoe.<16 antihypertensives>) > 0 ]),
]) if (balanco_6h and ultima_cpoe) else False
```

## Edge cases (as implemented)

Requires BOTH pas<90 AND pad<60 in the SAME record (comma = AND) whereas the docstring says OR. Count strictly > 2 (i.e. >= 3 records). Window refactored 4h -> 6h. Same 16-vs-18 antihypertensive-list omission as RULE-010 (no anlodipino/metoprolol).

## Divergence

Code vs docstring: (1) PAS/PAD combined with AND (`pas__lt=90, pad__lt=60`) vs documented OR; (2) antihypertensive list 16 checked vs 18 documented (omits anlodipino, metoprolol).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 614-669 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-072`

**Related rules:**

- [RULE-ESTABILIDADE-014](RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md)
- [RULE-ESTABILIDADE-010](../drug-dosing/RULE-ESTABILIDADE-010-estabilidade-v3-criterio-10-antihypertensive-with-active-vas.md)
- [RULE-ESTABILIDADE-024](../care-pathway/RULE-ESTABILIDADE-024-estabilizacao-trilha2-shock-work-up-vasopressor-escalation-t.md)

## Notes

Status upgraded OK->DISCREPANCY: Phase-1 identified the AND-vs-OR divergence in notes but left status OK. Facade criterio_12 = 'Hipotensao recorrente e anti-hipertensivos na prescricao'. verify:false — generic BP thresholds + drug-list enum, no specific published score.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
