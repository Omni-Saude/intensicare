# RULE-SEPSE-064 — SEPSE invasive-devices decision (early NE, central access, CVC replacement)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Clinical decision-support text for the "dispositivos_invasivos" item: prefer early noradrenaline via calibrous peripheral access, secure central venous access within 6h with invasive BP monitoring (PAI) and bladder-catheter diuresis (SVD); if a central venous catheter is older than 7 days consider replacement; check chest X-ray after central puncture or intubation.

## Inputs

- idade_cateter_venoso_central (number, dias)

## Outputs

- acao (text)

## Logic

```text
Preferir inicio precoce de noradrenalina em acesso venoso periferico calibroso;
garantir acesso venoso central em ate 6 h; monitorar PA invasiva (PAI) e diurese (SVD).
IF cateter_venoso_central > 7 dias: considerar a troca.
Checar RX de torax apos puncao venosa central e/ou intubacao orotraqueal.
```

## Edge cases (as implemented)

Verbatim text. Threshold: CVC age > 7 days -> consider replacement; central access within 6h.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/item_trilha_interativa_sepse.py` | 208-217 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-016`

**Related rules:**

- [RULE-SEPSE-062](../alert-threshold/RULE-SEPSE-062-sepse-reassessment-lab-thresholds-bicarbonate-dobutamine-tra.md)
- [RULE-SEPSE-063](RULE-SEPSE-063-sepse-hemodynamic-status-decision-intubation-rass-2-fluid-ch.md)
- [RULE-SEPSE-065](../drug-dosing/RULE-SEPSE-065-sepse-vasoactive-drug-escalation-thresholds-and-shock-index.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
