# RULE-ALERTAS-005 — Bed-level alert rollup util (define_tipo_alerta_leito) - DEAD/commented-out

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Rolls up the tipo_alerta colors of all trilhas on a bed to a single bed color, with VERMELHO dominating AMARELO dominating NEUTRO. A pure color-priority rollup over a dict of trilha -> {tipo_alerta}; does NOT consider assistido attendance or LARANJA.

## Inputs

- leito (mapping trilha -> {tipo_alerta})

## Outputs

- tipo (string)

## Logic

```text
tipo = "NEUTRO"
for _, trilha in leito.items():
    if trilha.get("tipo_alerta") == "VERMELHO":
        tipo = "VERMELHO"
    elif tipo != "VERMELHO" and trilha.get("tipo_alerta") == "AMARELO":
        tipo = "AMARELO"
    elif tipo != "VERMELHO" and tipo != "AMARELO" and trilha.get("tipo_alerta") == "NEUTRO":
        tipo = "NEUTRO"
return tipo
```

## Edge cases (as implemented)

Priority VERMELHO > AMARELO > NEUTRO regardless of iteration order (once VERMELHO set it is never downgraded). Unknown/missing tipo_alerta values are ignored. Empty leito -> "NEUTRO". LARANJA is not considered in this rollup.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/utils.py` | 84-97 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ALERT-BE-12-007`

**Related rules:**

- [RULE-ALERTAS-006](RULE-ALERTAS-006-bed-alert-color-aggregation-get-alerta-leito-with-sepse-lara.md)

## Notes

DEAD CODE: only referenced in commented-out view code (trilha_automatica/api/v1/views/trilhas.py:6, 62; import also commented). NOT the same rule as the active bed rollup RULE-ALERTAS-006 (get_alerta_leito), which adds assistido-filtering and a LARANJA interactive-sepse override. Kept separate as an older/simpler variant (not merged, not flagged DISCREPANCY since this util is inactive).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
