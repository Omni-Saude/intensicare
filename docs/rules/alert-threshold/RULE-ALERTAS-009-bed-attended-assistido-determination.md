# RULE-ALERTAS-009 — Bed 'attended' (assistido) determination

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
Determines whether an occupied bed is fully attended: every non-NEUTRO pathway must be attended; a bed with only NEUTRO pathways is treated as not attended.

## Inputs

- pathway (alerta, assistido) (list[(str,bool)])
- tipo (automatica|homecare)

## Outputs

- assistido (bool)

## Logic

```text
if tipo=="automatica":
  assistido=True; neutro=True
  if ocupado:
    for each pathway t:
      if t.alerta != "NEUTRO":
        neutro=False
        if not t.assistido: return False
        assistido = assistido and t.assistido
  return assistido if not neutro else False
elif tipo=="homecare":
  assistidos = [t.assistido for pathway t if t and t.alerta != "NEUTRO"]
  return bool(assistidos and not assistidos.count(False))
```

## Edge cases (as implemented)

All-NEUTRO bed => not attended (returns False). Homecare: returns False if list empty OR any False. Empty/unoccupied bed => False for automatica (neutro stays True).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 818-848 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-BE-04-021`

**Related rules:**

- [RULE-ALERTAS-010](RULE-ALERTAS-010-automatic-bed-payload-alert-attendance-flag.md)

## Notes

Same "NEUTRO present and >1 distinct color" nuance is recomputed differently in RULE-ALERTAS-010 (payload builder).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
