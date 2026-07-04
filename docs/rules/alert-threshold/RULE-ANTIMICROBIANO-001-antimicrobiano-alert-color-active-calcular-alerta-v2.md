# RULE-ANTIMICROBIANO-001 — Antimicrobiano alert color (active - calcular_alerta_v2)

| Field | Value |
|---|---|
| Cluster | antimicrobiano |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Active antimicrobial severity/color alert wired into TrilhaAntimicrobianoModel.save() (line 102: self.alerta = self.calcular_alerta_v2()). Maps a subset of the boolean stewardship criteria flags to VERMELHO/AMARELO/NEUTRO. When NEUTRO, save() also resets assistido=False (lines 103-104).

## Inputs

| name | type | unit |
|---|---|---|
| criterio_3 | int flag (truthy) |  |
| criterio_4 | int flag (truthy) |  |
| criterio_5 | int flag (truthy) |  |
| criterio_6 | int flag (truthy) |  |
| criterio_8 | int flag (truthy) |  |

## Outputs

| name | type | unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |  |

## Logic

```text
amarelo  = [criterio_3, criterio_5, criterio_6].count(True)
vermelho = [criterio_4, criterio_8].count(True)
if vermelho >= 1:
    return "VERMELHO"
elif amarelo >= 1:
    return "AMARELO"
else:
    return "NEUTRO"
# In save(): self.alerta = calcular_alerta_v2(); if alerta == "NEUTRO": self.assistido = False
```

## Edge cases (as implemented)

Uses .count(True); Django IntegerField values of 1 equal True in Python so 1-flags count. save() forces assistido=False on NEUTRO. Only criteria 3,4,5,6,8 feed this alert (the criterios_mensagem property lists criterio_4 and criterio_8 as the red-driving ones).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha5.py` | 101-105, 182-201 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-antimicrobiano-BE-03-015`

**Related rules:**

- [RULE-ANTIMICROBIANO-002](RULE-ANTIMICROBIANO-002-antimicrobiano-alert-color-legacy-unused-calcular-alerta.md)
- [RULE-ANTIMICROBIANO-003](../care-pathway/RULE-ANTIMICROBIANO-003-antimicrobial-stewardship-criteria-catalog-12-criteria-durat.md)

## Notes

This is the version actually called by save(). RULE-ANTIMICROBIANO-002 (calcular_alerta) is the unused legacy variant with a different, richer criterion weighting - kept SEPARATE as a version variant, not merged. A THIRD, distinct severity path also exists in the same model but was NOT captured as a separate Phase-1 rule: generate_view_data() -> define_tipo_alerta(conta_criterios_automatica(), _CRITERIOS_ALERTA={"amarelo":2,"vermelho":3}) counts criterio_1..12 truthy (trilha5.py lines 12/51, 107-121). Recorded here for completeness; not fabricated as a rule.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
