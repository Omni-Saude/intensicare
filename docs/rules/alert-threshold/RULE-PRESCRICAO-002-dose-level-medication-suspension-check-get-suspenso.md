# RULE-PRESCRICAO-002 — Dose-level medication suspension check (get_suspenso)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Per-dose 'suspenso' flag: a scheduled dose is suspended if the source prescription's suspension date (DT_SUSPENSAO) is before the dose's scheduled day, or - on the same calendar day - if the suspension time-of-day is strictly earlier than the dose's scheduled time-of-day. Defined identically (byte-for-byte) in the offline and the primary HorarioPrescricao serializers; each class also carries a shadowed, never-executed first definition with inverted logic.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| DT_SUSPENSAO | datetime |  |  |
| prescricao_continua.dia | date |  |  |
| obj.horario | string(HH:MM) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| suspenso | boolean |  |

## Logic

```text
# LIVE (active) dose-level get_suspenso — identical in HorarioPrescricaoOfflineSerializer (l.65-80)
# and HorarioPrescricaoSerializer (l.147-162):
dt_suspensao = obj.prescricao_continua.prescricao.DT_SUSPENSAO
if dt_suspensao:
    dia_prescricao_continua = obj.prescricao_continua.dia
    dia_suspensao = dt_suspensao.date()
    if dia_prescricao_continua > dia_suspensao:
        return True
    elif dia_prescricao_continua == dia_suspensao:
        horario_split = obj.horario.split(":")
        if dt_suspensao.hour < int(horario_split[0]) or (
            dt_suspensao.hour == int(horario_split[0])
            and dt_suspensao.minute < int(horario_split[1])
        ):
            return True
return False
```

## Edge cases (as implemented)
Returns False whenever DT_SUSPENSAO is null (never suspended). Same-day comparison uses strict `<` (suspension at exactly the scheduled minute is NOT suspended). horario is split on ':' and cast to int, assuming an 'HH:MM' string. The shadowed dead first definition (recorded in divergence) uses `>=` and inverted date ordering but is unreachable.

## Divergence
Two divergences captured verbatim. (1) SHADOWED DEAD SIBLING: each serializer defines get_suspenso TWICE; the FIRST definition (l.50-63 offline, l.132-145 online) is dead code (Python keeps only the last same-named method) and encodes INVERTED semantics: `if dia_suspensao > dia_prescricao_continua: return True; if dia_suspensao == dia_prescricao_continua and dt_suspensao.hour >= int(h[0]): if dt_suspensao.minute >= int(h[1]): return True` (a LATER suspension retroactively suspends an earlier dose, using >= not <). It never executes. (2) The live version uses strict `<` for the same-day time comparison, so a suspension at exactly the dose's scheduled minute is NOT flagged suspended. This dose-level check also disagrees in scope with the header/order-level now-based check (RULE-PRESCRICAO-003) for doses not scheduled 'today'.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 147-162 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 65-80 | `8166c07e` | duplicate |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 50-63 | `8166c07e` | variant |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 132-145 | `8166c07e` | variant |

**Merged from:**

- RULE-prescricao-BE-07-001
- RULE-prescricao-BE-07-002
- RULE-prescricao-BE-07-003
- RULE-prescricao-BE-07-004

**Related rules:**

- RULE-PRESCRICAO-003

## Notes
Merged the offline+online byte-identical live definitions and their two byte-identical shadowed dead siblings into one dose-level rule. Live logic is the only one that executes. Kept DISCREPANCY because of the dead inverted-logic siblings and the scope disagreement with the header-level check (RULE-PRESCRICAO-003).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
