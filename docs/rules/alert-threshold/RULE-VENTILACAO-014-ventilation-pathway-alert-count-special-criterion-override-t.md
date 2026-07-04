# RULE-VENTILACAO-014 — Ventilation pathway alert (count + special-criterion override) - trilha_manual

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Ventilation alert is VERMELHO if >=3 criteria OR any of C1/C8/C9 is set; AMARELO if >=1; else NEUTRO.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| criterios_true_count (int 0-10) | | | |
| criterio_1 / criterio_8 / criterio_9 (bool) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alerta (enum {VERMELHO, AMARELO, NEUTRO}) | | |

## Logic

```text
n = count(True among criterio_1..10)
if n >= 3 or (criterio_1 or criterio_8 or criterio_9): 'VERMELHO'
elif n > 0: 'AMARELO'
else: 'NEUTRO'
```

## Edge cases (as implemented)

A single C1/C8/C9 -> immediate VERMELHO even though count is 1.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 346-364 | `8166c07e` | primary |

- Merged from: RULE-vent-BE-10-058
- Related rules: RULE-VENTILACAO-003, RULE-VENTILACAO-011, RULE-VENTILACAO-012, RULE-VENTILACAO-016, RULE-VENTILACAO-015

## Notes

Only pathway with a hard red-flag override on specific criteria (C1 high PINS/VC, C8 extubation-readiness, C9 shock-without-VM). Verified verbatim against source. Logic is IDENTICAL to the unused legacy alert in trilha_automatica trilha3.py (RULE-VENTILACAO-016), a separate pathway variant. Pure count/aggregation convention with no published clinical anchor -> verify=false.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
