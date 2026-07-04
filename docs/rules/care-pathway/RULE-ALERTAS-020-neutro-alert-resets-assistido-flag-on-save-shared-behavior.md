# RULE-ALERTAS-020 — NEUTRO alert resets assistido flag on save (shared behavior)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Across persisted trilhas, whenever the recomputed alert is NEUTRO the save() sets assistido=False, clearing any prior clinician acknowledgement when the patient no longer meets any criterion.

## Inputs

- computed alerta (enum)

## Outputs

- assistido (boolean)

## Logic

```text
def save(...):
  <compute criteria if v3>
  self.alerta = <calcular_alerta variant>
  if self.alerta == "NEUTRO": self.assistido = False
  super().save()
```

## Edge cases (as implemented)

Applied in trilha3 (Ventilacao), trilha5 (Antimicrobiano), trilha6 (Nutricao), trilha7 (Equilibrio), trilha9 (GlosaZero), and all v3 models. NOT applied in trilha1 (Sedacao v1), trilha2 (Estabilizacao v1), trilha4 (SEPSE v1), trilha8 (Profilaxias v1) - inconsistent.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 74-79 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-BE-03-134`

**Related rules:**

- [RULE-ALERTAS-003](../alert-threshold/RULE-ALERTAS-003-criteria-count-alert-color-mapping-define-tipo-alerta-per-mo.md)

## Notes

Cross-cutting save() behavior; representative source cited, replicated per model.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
