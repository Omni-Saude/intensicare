# RULE-SINAIS-VITAIS-007 — SinaisVitais soft-delete logs audit action (no balance adjustment)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Deleting a SinaisVitais record marks it deleted by the current user and logs an AcaoHomecare audit entry ("inativar" on "sinal_vital"). Unlike Entrada/Saida destroy, no BalancoHidrico field is adjusted (vital signs do not contribute to the fluid balance).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance | model instance (SinaisVitais) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| AcaoHomecare audit record | model instance |  |

## Logic
```text
@transaction.atomic
def destroy(request):
    instance.deletado_por = user
    instance.save()
    criar_acao_homecare(tipo="sinal_vital", acoes=["inativar"], leito=request.leito,
                         setor=request.setor, sinal_vital=instance, realizado_por=user)
    return super().destroy(request)
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/sinais_vitais.py` | 37-52 | `8166c07e` | primary |

- Merged from: RULE-sinal-BE-08-049
- Related rules: RULE-SINAIS-VITAIS-006, RULE-SINAIS-VITAIS-008

## Notes
Contrast with the entrada/saida destroy handlers (balanco-hidrico cluster: RULE-entrada-BE-08-011 / RULE-saida-BE-08-046) which DO adjust balanco_24h.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
