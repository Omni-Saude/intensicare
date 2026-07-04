# RULE-ANTIMICROBIANO-002 — Antimicrobiano alert color (legacy unused - calcular_alerta)

| Field | Value |
|---|---|
| Cluster | antimicrobiano |
| Category | alert-threshold |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Legacy antimicrobial severity/color alert (calcular_alerta) with a third weighted criterion group ("criterios"). Not called by save() - dead in the active path. Kept as a version variant of RULE-ANTIMICROBIANO-001, not merged.

## Inputs

| name | type | unit |
|---|---|---|
| criterio_1..14 | int flag (1) |  |

## Outputs

| name | type | unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO} |  |

## Logic

```text
amarelo   = [criterio_1, criterio_2, criterio_3].count(1)
criterios = [criterio_4, criterio_6, criterio_8, criterio_9,
             criterio_11, criterio_12, criterio_13, criterio_14].count(1)
vermelho  = [criterio_5, criterio_7, criterio_10].count(1)
if vermelho >= 1 or criterios > 3:
    return "VERMELHO"
elif amarelo >= 1 or (0 < criterios <= 2):
    return "AMARELO"
else:
    return "NEUTRO"
```

## Edge cases (as implemented)

criterios == 3 exactly falls through BOTH branches to NEUTRO (gap between the <=2 AMARELO condition and the >3 VERMELHO condition) - a latent defect if this code were reactivated. Uses .count(1) (literal 1) rather than .count(True); behaves identically to _v2 for 1-valued IntegerFields since 1 == True in Python.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha5.py` | 156-180 | `8166c07eae` | variant |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-antimicrobiano-BE-03-016`

**Related rules:**

- [RULE-ANTIMICROBIANO-001](RULE-ANTIMICROBIANO-001-antimicrobiano-alert-color-active-calcular-alerta-v2.md)
- [RULE-ANTIMICROBIANO-003](../care-pathway/RULE-ANTIMICROBIANO-003-antimicrobial-stewardship-criteria-catalog-12-criteria-durat.md)

## Notes

Dead code: save() calls calcular_alerta_v2 (RULE-ANTIMICROBIANO-001), never this. Status AMBIGUOUS retained (never downgraded) because of the criterios==3 fall-through gap. This is a version variant of RULE-ANTIMICROBIANO-001 (different criterion sets and the extra "criterios" bucket), so it is cross-referenced via related and NOT merged.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
