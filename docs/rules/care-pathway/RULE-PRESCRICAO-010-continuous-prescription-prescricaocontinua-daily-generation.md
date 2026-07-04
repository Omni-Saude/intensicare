# RULE-PRESCRICAO-010 — Continuous-prescription (PrescricaoContinua) daily generation eligibility

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Scheduled task that materialises today's continuous prescriptions from the Tasy-sourced Prescricao table. A candidate prescription is first filtered by display/validity, then a PrescricaoContinua for today is created only if all generation conditions hold.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| (none - reads today's date and Prescricao table) |  |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| PrescricaoContinua records created (dia=today) | side-effect |  |

## Logic

```text
hoje = date.today()
candidates = Prescricao where
    IE_EXIBE == "S"
    AND (DT_FIM IS NULL OR DT_FIM > hoje)
    AND (DT_SUSPENSAO > hoje OR DT_SUSPENSAO IS NULL)
  order_by DS_ITEM_PRESCRITO
for obj in candidates:
    create if ALL of:
       (1) NOT PrescricaoContinua.exists(dia==hoje, prescricao==obj)
       (2) (obj.DT_PROX_GERACAO == hoje) if obj.IE_GERACAO_DIFERENTE == "S" else True
       (3) obj.DT_LIBERACAO is truthy        # prescription has been released
       (4) (obj.DT_INICIO <= hoje) if obj.DT_INICIO else False   # has started
    then PrescricaoContinua.create(dia=hoje, prescricao=obj)
```

## Edge cases (as implemented)
Condition (4) requires DT_INICIO present AND <= today; a null DT_INICIO makes the item ineligible. Condition (2) enforces DT_PROX_GERACAO == today only for items flagged IE_GERACAO_DIFERENTE == "S" (different generation schedule); others always pass (2). Idempotent per (prescricao, day) via (1). DT_FIM/DT_SUSPENSAO comparisons use '>' (strict).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/tasks.py` | 16-48 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-09-001

**Related rules:**

- RULE-PRESCRICAO-020

## Notes
Celery task criar_prescricao_continua. IE_EXIBE/DT_FIM/DT_SUSPENSAO/DT_LIBERACAO/DT_INICIO/ DT_PROX_GERACAO/IE_GERACAO_DIFERENTE are Tasy (Oracle) prescription columns mirrored on the Prescricao model (different partition). Creating a PrescricaoContinua triggers its save() which regenerates per-horario check rows (see RULE-prescricao-BE-09-004 note / tasks.atualizar_horarios_presc).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
