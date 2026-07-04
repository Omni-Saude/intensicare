# RULE-ALERTAS-003 — Criteria-count -> alert color mapping (define_tipo_alerta) + per-model _CRITERIOS_ALERTA thresholds

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Maps a count of triggered criteria to a care-pathway alert color VERMELHO / AMARELO / NEUTRO using per-trilha {amarelo, vermelho} count thresholds. define_tipo_alerta is the single shared function; each *Sintetico / *_sintetico (v1 and v3) model invokes it from generate_view_data() passing conta_criterios_automatica() and its own _CRITERIOS_ALERTA dict.

## Inputs

- total_alertas (integer count of truthy criteria, >= 0)
- criterios['vermelho'] (integer count-threshold, >= 1)
- criterios['amarelo'] (integer count-threshold, >= 1)

## Outputs

- tipo_alerta (string enum {VERMELHO, AMARELO, NEUTRO})

## Logic

```text
# define_tipo_alerta (trilha_automatica/utils.py:75-81) - shared color mapping:
if total_alertas >= criterios["vermelho"]:
    return "VERMELHO"
elif 0 < total_alertas <= criterios["amarelo"]:
    return "AMARELO"
else:
    return "NEUTRO"

# Each *Sintetico / *_sintetico model calls it from generate_view_data() as:
#   define_tipo_alerta(self.conta_criterios_automatica(), self._CRITERIOS_ALERTA)
# Per-model _CRITERIOS_ALERTA {amarelo, vermelho} thresholds (verified @8166c07):
#   trilha1,2,3,4,8,9 & all v3 & *_Tasy: {"amarelo":2,"vermelho":3}
#   trilha5 sintetico (v3), trilha6 sintetico (v3): {"amarelo":3,"vermelho":4}
#   trilha7 sintetico (v3): {"amarelo":4,"vermelho":5}
# conta_criterios_automatica counts truthy criterio_1..N attributes; N varies:
#   1..6 (trilha1,2,8); 1..10 (trilha3,5,7); 1..20 (trilha4); etc.
#   (ranges frequently under-count relative to defined criteria, e.g. trilha1
#    counts only 1..6 of 12).
```

## Edge cases (as implemented)

total_alertas == 0 -> NEUTRO (AMARELO branch requires total > 0). VERMELHO uses >= (inclusive). AMARELO upper bound <= criterios["amarelo"] (inclusive). If criterios["amarelo"] < total_alertas < criterios["vermelho"], NEITHER branch matches -> NEUTRO (a value above the yellow threshold but below red is downgraded to neutral). In practice every _CRITERIOS_ALERTA in the codebase sets vermelho == amarelo+1, so this dead-zone is not exercised by shipped models.

## Divergence

Latent logic dead-zone: when amarelo < vermelho-1, a criteria count strictly between the two thresholds falls through both branches to NEUTRO instead of AMARELO (mid-range counts silently downgraded). Safe only while callers keep amarelo == vermelho-1 (all shipped models do). Also: this function never emits 'LARANJA' although an orange alert state exists elsewhere (core/models/leito.py:273; trilha_interativa_sepse sets alerta_trilha_interativa='LARANJA') - LARANJA is assigned by separate interactive-sepsis logic (see RULE-ALERTAS-006), not here.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/utils.py` | 75-81 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_automatica/models/trilha1.py` | 13, 50, 128-133, 209, 219-234 | `8166c07eae` | duplicate |
| ahlabs-trilhas | `trilha_automatica/models/trilha5.py` | 216, 237 | `8166c07eae` | duplicate |
| ahlabs-trilhas | `trilha_automatica/models/trilha6.py` | 172, 193 | `8166c07eae` | duplicate |
| ahlabs-trilhas | `trilha_automatica/models/trilha7.py` | 173, 194 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ALERT-BE-12-006`
- `RULE-alerta-BE-03-002`

**Related rules:**

- [RULE-ALERTAS-001](RULE-ALERTAS-001-count-triggered-criteria-contar-qtd-criterios-alerta.md)
- [RULE-ALERTAS-005](RULE-ALERTAS-005-bed-level-alert-rollup-util-define-tipo-alerta-leito-dead-co.md)

## Notes

Merge of the predicate-code capture of define_tipo_alerta (BE-12-006) with the catalog/model-layer capture of the same threshold applied to the Sintetico models with per-model constants (BE-03-002). define_tipo_alerta lives in trilha_automatica/utils.py; the _CRITERIOS_ALERTA constants and conta_criterios_automatica counting live on each model. conta_criterios_automatica is a distinct counter from contar_qtd_criterios_alerta (RULE-ALERTAS-001): the former counts criterio_1..N attributes, the latter iterates a trilha["criterios"] list. Threshold table re-verified against source @8166c07 (trilha5/6 v3 = 3/4, trilha7 v3 = 4/5, all others = 2/3).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
