# RULE-MOVIMENTACAO-ADT-013 — Patient 'assisted' resolution across pathways (movimentacao)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Determines whether a patient is fully 'assisted' - every non-neutral pathway must be marked assisted; all-neutral returns False.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| 4 trilhas | alerta, assistido) (objects |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| assistido | bool |  |

## Logic
```text
get_assistido_por_trilha(t) = t.assistido if t.alerta != 'NEUTRO' else True
if all 4 alertas == 'NEUTRO': return False
return all(get_assistido_por_trilha(t) for t in [sedacao, estabilidade, ventilacao, sepse])
```

## Edge cases (as implemented)
All-neutral -> False (nothing to assist). A neutral pathway counts as assisted(True) so it does not block. Any non-neutral, non-assisted pathway -> False.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_manual/models/dados_prontuario.py | 214-234 | 8166c07e | primary |
- Merged from: RULE-mov-BE-10-061
- Related rules: RULE-MOVIMENTACAO-ADT-011, RULE-MOVIMENTACAO-ADT-046

## Notes
Active code verified at dados_prontuario.py:218-234 (get_assistido / get_assistido_por_trilha). get_trilhas/get_detalhe assemble per-pathway alert & payload for the API. This is the confirmed manual/movimentacao variant; RULE-011 is the (unconfirmed) leito-serializer variant for automatica/homecare.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
