# RULE-VENTILACAO-025 — VentilacaoMecanica ventilation / device / modality enumerations (backend model + frontend movimentacao form)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Enumerations for ventilation support type, airway device, and ventilation modality on VentilacaoMecanica - backend model choices (trilha_manual) reconciled with the frontend movimentacao form copy.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| ventilacao / dispositivo / modalidade (str enum) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| stored value (str) | | |

## Logic

```text
# Backend model choices (VentilacaoChoices, trilha_manual) - PRIMARY / most complete:
ventilacao:  ('assistida','assistida' [Sera desativado]), ('controlada','controlada' [Sera desativado]),
             ('ar_ambiente','Ar Ambiente'), ('vm_invasiva','Cateter Nasal de O2'),
             ('vm_nao_invasiva','VM Nao Invasiva'), ('mascara_facial_o2','Mascara Facial de O2'),
             ('tenda_o2_tqt','Tenda de O2 para TQT'), ('','Nao informado')
dispositivo: ('tot','TOT'), ('tqt','TQT'), ('dni','DNI' [Sera desativado]), ('','Nao informado')
modalidade:  ('psv','PSV'), ('vcv','VCV'), ('pcv','PCV'), ('','Nao informado')

# Frontend movimentacao form (dataFormMovimentacao.ts) - OMITS deactivated options:
ventilacao:  ar_ambiente('Ar ambiente'), vm_invasiva('Cateter Nasal de 02'),
             vm_nao_invasiva('VM Nao Invasiva'), mascara_facial_o2('Mascara Facial de O2'),
             tenda_o2_tqt('Tenda de O2 para TQT'), ''('Nao informado')
dispositivo: tot('TOT'), tqt('TQT'), ''('Nao informado')
modalidade:  psv('PSV'), vcv('VCV'), pcv('PCV'), ''('Nao informado')
# Also ventilacao_mecanica.horario_inicio datetime; frontend group is anulavel.
```

## Edge cases (as implemented)

Ventilacao C5/C6 (RULE-VENTILACAO-008/009) compare dispositivo == 'tot'. Ventilacao C4 (RULE-VENTILACAO-007) compares dispositivo == 'PCV'/'VCV' (uppercase) which are NOT valid dispositivo values (they are modalidade psv/vcv/pcv) - so that device-path is effectively unreachable.

## Divergence

BE model choices (trilha_manual) include deactivated options assistida & controlada (ventilacao) and dni (dispositivo) that the FE movimentacao form OMITS. Label text differs: BE 'Ar Ambiente' vs FE 'Ar ambiente'; BE vm_invasiva label 'Cateter Nasal de O2' (letter O) vs FE 'Cateter Nasal de 02' (digit zero). Shared defect on BOTH sides: vm_invasiva value (semantically invasive VM) is paired with a nasal-cannula label.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/choices/indicadores.py` | 47-86 | `8166c07e` | primary |
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 289-352 | `f9656be2` | frontend-copy |

- Merged from: RULE-choice-BE-10-070, RULE-resp-FE-01-030
- Related rules: RULE-VENTILACAO-024, RULE-VENTILACAO-019, RULE-VENTILACAO-007, RULE-VENTILACAO-002

## Notes

Verified both sides against source (backend indicadores.py 47-86 and frontend dataFormMovimentacao.ts 289-352). Backend Phase-1 tagged category care-pathway; frontend tagged data-validation - kept the more precise data-validation. "Sera desativado" markers indicate assistida/controlada/dni are slated for removal.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
