# RULE-ALERTAS-007 — Automatic-bed alert ignoring attendance (alerta_nao_assistido)

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
Highest-severity alert among an automatic bed's pathways, disregarding whether they were attended.

## Inputs

- pathway alerts (list[str] VERMELHO|AMARELO|NEUTRO)

## Outputs

- alerta_nao_assistido (string)

## Logic

```text
alertas = [t.alerta for each pathway t where t and t.alerta != "NEUTRO"]  (only if bed.ocupado)
if alertas:
  if "VERMELHO" in alertas: "VERMELHO"
  elif "AMARELO" in alertas: "AMARELO"
  else: "NEUTRO"
else: "" (empty string)
```

## Edge cases (as implemented)

Returns "" when no non-neutral pathways (or bed empty). Stored to Leito.alerta_nao_assistido in save() when tipo=="automatica" and ocupado.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 457-480 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-BE-04-014`

**Related rules:**

- [RULE-ALERTAS-006](RULE-ALERTAS-006-bed-alert-color-aggregation-get-alerta-leito-with-sepse-lara.md)
- [RULE-ALERTAS-008](RULE-ALERTAS-008-homecare-bed-alert-ignoring-attendance-pioraclinica-sepse.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
