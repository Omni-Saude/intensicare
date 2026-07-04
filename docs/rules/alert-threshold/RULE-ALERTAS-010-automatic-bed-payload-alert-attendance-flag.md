# RULE-ALERTAS-010 — Automatic-bed payload alert + attendance flag

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
Builds an automatic bed's payload: overall alert = most severe un-attended pathway color; attended flag requires NEUTRO present alongside at least one other distinct color.

## Inputs

- pathway payloads (alerta, assistido) (list[dict])

## Outputs

- payload.alerta (string)
- payload.assistido (bool)

## Logic

```text
for each pathway t (if ocupado):
  cor_alertas.add(t.alerta)
  if t.alerta != "NEUTRO": assistido = assistido and t.assistido
alertas = [t.alerta for t in trilhas if t.alerta in ("VERMELHO","AMARELO") and t.assistido is not True]
if alertas:
  alertas.sort(); payload.alerta = alertas[-1]   # alphabetical: VERMELHO > AMARELO
else:
  payload.alerta = self.alerta
payload.assistido = assistido if ("NEUTRO" in cor_alertas and len(cor_alertas) != 1) else False
```

## Edge cases (as implemented)

alertas.sort() then [-1] yields VERMELHO before AMARELO (alphabetical V>A). attendance False if the only color present is NEUTRO OR if no NEUTRO at all (len==1 guard). Also attaches micro_indicadores + procedimentos_invasivos from MicroIndicadores by (NR_ATENDIMENTO, CD_UNIDADE==bed name).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 390-455 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-BE-04-022`

**Related rules:**

- [RULE-ALERTAS-009](RULE-ALERTAS-009-bed-attended-assistido-determination.md)
- [RULE-ALERTAS-006](RULE-ALERTAS-006-bed-alert-color-aggregation-get-alerta-leito-with-sepse-lara.md)

## Notes

Homecare analog at leito.py:548-651 uses self.alerta fallback and the same sort()/[-1] selection.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
