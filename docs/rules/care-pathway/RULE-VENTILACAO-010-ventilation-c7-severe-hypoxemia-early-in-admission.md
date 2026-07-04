# RULE-VENTILACAO-010 — Ventilation C7 - severe hypoxemia early in admission

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | medium |
| Cluster | ventilacao |

## Rule

Flags P/F<150 AND noradrenaline dose<25 AND admission length>7 days.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| relacao_po2_fio2 | | | |
| noradrenalina.quantidade (ml) | | | |
| dias_internacao (days) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criterio_7 (bool) | | |

## Logic

```text
all([
  (relacao_po2_fio2 < 150) if (po2 and fio2) else False,
  (noradrenalina.quantidade < 25) if verificar_objeto_existe(dp,'noradrenalina') else False,
  (movimentacao.buscar_dias_internacao > 7) if movimentacao.buscar_dias_internacao else False ])
```

## Edge cases (as implemented)

All three required. Strict <150, <25, >7. Depends on external movimentacao.buscar_dias_internacao.

## Verification

- Verdict: VERIFIED (clinical impact: none)
- Reference: PROSEVA trial (Guerin et al., NEJM 2013): severe ARDS defined by PaO2/FiO2 < 150 (with FiO2>=0.6, PEEP>=5) as the prone-positioning / severe-hypoxemia indication; Berlin ARDS definition

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 269-283 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-054
- Related rules: RULE-VENTILACAO-005, RULE-VENTILACAO-012

## Notes

_REGRAS text and code diverge in wording ("ausencia de noradrenalina com menos de 25 ml/h"); code requires noradrenaline PRESENT with quantity<25. P/F<150 is a published ARDS anchor. Test test_trilha_ventilacao.py:162-176.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
