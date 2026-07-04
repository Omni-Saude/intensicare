# RULE-BALANCO-HIDRICO-027 — 07:00 shift boundary assigns pre-07:00 entries to previous day's balanco

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
When an Entrada/Saida/SinaisVitais record is (re)timed, its owning daily fluid balance is chosen by the 07:00 rule: an entry timed before 07:00 on the current calendar day belongs to the PREVIOUS day's BalancoHidrico (because the nursing day runs 07:00 to 07:00). This encodes the same 7-to-7 shift used by all 24h aggregations, and is displayed in templates as "Turno vigente: 7:00 as 7:00".

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| balanco_atual | — | — | — |
| horario | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| balanco | — | — |

## Logic
```text
if horario and horario < "07:00" (lexicographic string compare)
       and date.today() == balanco_atual.dia:
    return BalancoHidrico.objects.filter(nr_atendimento == balanco_atual.nr_atendimento)
                                 .get(dia == balanco_atual.dia - 1 day)
else:
    return balanco_atual
```

## Edge cases (as implemented)
String comparison "HH:MM" < "07:00" works only for zero-padded 24h strings. The previous-day lookup uses .get() and will raise DoesNotExist if yesterday's balanco is missing. Only reassigns when the balanco's dia equals today; otherwise leaves it unchanged.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 496-506 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-008
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-013, RULE-BALANCO-HIDRICO-023, RULE-BALANCO-HIDRICO-024

## Notes
Foundational 07:00 boundary shared with RULE-...-001..007. The "7:00 as 7:00" turno constant is also hard-coded in pdf_balanco_hidrico.html (l.156/168), pdf_balanco_hidrico_com_assinatura.html and pdf_prescription_v2.html (l.155).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
