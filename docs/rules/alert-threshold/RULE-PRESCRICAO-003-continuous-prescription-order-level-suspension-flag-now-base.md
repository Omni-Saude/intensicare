# RULE-PRESCRICAO-003 — Continuous-prescription (order-level) suspension flag - now-based

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Order/header-level 'suspenso': the whole continuous prescription is suspended once its source prescription's DT_SUSPENSAO is at or before the current wall-clock time. Computed identically in the PrescricaoContinua model property and the PrescricaoContinua serializer.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| prescricao.DT_SUSPENSAO | datetime |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| suspenso | boolean |  |

## Logic

```text
# Byte-identical in PrescricaoContinua.suspenso property and PrescricaoContinuaSerializer.get_suspenso:
dt_suspensao = <prescricao>.DT_SUSPENSAO
if dt_suspensao:
    return dt_suspensao <= timezone.now()
else:
    return False
```

## Edge cases (as implemented)
A future DT_SUSPENSAO -> not yet suspended (False). Null DT_SUSPENSAO -> False. Uses timezone.now() (current time), so the flag for a given day's order can change purely with the passage of time.

## Divergence
This order-level check (DT_SUSPENSAO <= now(), whole order, wall-clock) is byte-identical between the model property (prescricao_continua.py 54-60) and the serializer (serializers/prescricao.py 145-151) - so those two AGREE. It DISAGREES with the dose-level get_suspenso (RULE-PRESCRICAO-002), which compares the specific dose's scheduled day/time to DT_SUSPENSAO rather than to now(); the header can therefore report suspenso True/False inconsistently with an individual dose scheduled on a day other than today.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/prescricao.py` | 145-151 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_homecare/models/prescricao_continua.py` | 54-60 | `8166c07e` | duplicate |

**Merged from:**

- RULE-prescricao-BE-06-002
- RULE-prescricao-BE-07-005

**Related rules:**

- RULE-PRESCRICAO-002

## Notes
Model property and serializer method are identical; merged. Kept DISCREPANCY (carried from BE-07-005) for the cross-scope disagreement with the dose-level suspension check.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
