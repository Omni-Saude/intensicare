# RULE-SEPSE-069 — Bundle item overdue (atraso_item_interativa) time windows

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
A bundle item is overdue when unchecked past its package deadline relative to protocol creation: 1h for primeira_hora, 3h for reavaliacao.

## Inputs

- pacote, trilha_interativa.criado_em, checado (string / datetime / bool)

## Outputs

- atraso_item_interativa (boolean)

## Logic

```text
if pacote == "primeira_hora": return (now - 1h > criado_em) and not checado
elif pacote == "reavaliacao": return (now - 3h > criado_em) and not checado
# else: returns None (implicit)
```

## Edge cases (as implemented)

Returns None for any other pacote value; time via django.utils.timezone.now().

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Surviving Sepsis Campaign Hour-1 Bundle (Levy MM, Evans LE, Rhodes A. The Surviving Sepsis Campaign Bundle: 2018 update. Crit Care Med 2018;46:997) - initial sepsis interventions to begin within the first hour. The exact overdue-flag windows (1h primeira_hora, 3h reavaliacao) are internal operational parameters. ([source](https://www.sccm.org/survivingsepsiscampaign/guidelines-and-resources/surviving-sepsis-campaign-adult-guidelines))

**Checks**

| Dimension | Result |
|---|---|
| equation | Overdue = (now - deadline > criado_em) AND not checado - correct threshold logic. |
| coefficients | 1h deadline for primeira_hora aligns with SSC Hour-1 Bundle; 3h for reavaliacao is an internal operational choice (loosely echoes the retired SSC 3-hour bundle). |
| units | hours (timedelta) vs datetime criado_em - consistent. |
| ranges | n/a |
| rounding | strict > comparison - item overdue only strictly past the deadline. |
| cutoffs | 1h / 3h windows; returns None for any other pacote value (neither True nor False). |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| pacote=primeira_hora, criado_em=90 min ago, checado=False | past 1h Hour-1 Bundle deadline, not done -> overdue | now-1h > criado_em(90m) TRUE and not checado -> True | yes |
| pacote=primeira_hora, criado_em=30 min ago, checado=False | within first hour -> not overdue | now-1h > criado_em(30m) FALSE -> False | yes |
| pacote=reavaliacao, criado_em=4h ago, checado=False | past reassessment window -> overdue | now-3h > criado_em(4h) TRUE -> True | yes |
| pacote=reavaliacao, criado_em=2h ago, checado=True | already checked -> not overdue | not checado FALSE -> False | yes |
| pacote=other value | n/a (no bundle deadline) | returns None (implicit) - neither overdue nor not-overdue | yes |

**Verifier notes**

The 1h deadline for the primeira_hora package correctly anchors to the SSC Hour-1 Bundle (Levy 2018). The 3h reavaliacao window and the exact UI overdue-flag mechanics are internal operational parameters with no conflicting guideline value. Threshold logic (strict > deadline AND not checado) is sound; implicit None return for any pacote other than primeira_hora/reavaliacao is a documented edge case, not a reference discrepancy.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilhas_interativas/item_trilha_interativa.py` | 34-44 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-interativa-BE-03-131`

**Related rules:**

- [RULE-SEPSE-070](RULE-SEPSE-070-bundle-item-visibility-exibir-reassessment-appears-after-2h.md)
- [RULE-SEPSE-075](../care-pathway/RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)
- [RULE-SEPSE-095](../alert-threshold/RULE-SEPSE-095-sepsis-protocol-item-first-hour-delay-alert.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
