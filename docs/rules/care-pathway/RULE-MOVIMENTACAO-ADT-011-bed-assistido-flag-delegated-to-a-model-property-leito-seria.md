# RULE-MOVIMENTACAO-ADT-011 — Bed 'assistido' flag delegated to a model property (leito serializer)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | formula |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | low |
| Cluster | movimentacao-adt |

## Rule
OcupacaoSerializer.get_assistido returns instance.get_assistido - a model-level property/method defined in core/models (out of partition). The docstring and a large block of commented-out dead code in the same file describe the intended algorithm: for 'automatica' beds, iterate all non-NEUTRO trilhas and require ALL to be assistido=True (short-circuiting to False), but if every trilha is NEUTRO the overall result is forced False; for 'homecare' beds, collect assistido flags of only non-NEUTRO trilhas and return True only if that list is non-empty and contains no False.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.tipo | string enum |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| assistido | boolean |  |

## Logic
```text
# ACTIVE code:
def get_assistido(instance):
    return instance.get_assistido
# Commented-out (dead) code in the same file suggests the underlying algorithm:
# if tipo == "automatica":
#     assistido, neutro = True, True
#     if instance.ocupado:
#         for Trilha in instance.get_trilhas_automaticas():
#             trilha = get_trilha(Trilha, instance, instance.tipo)
#             if trilha and trilha.alerta != "NEUTRO":
#                 neutro = False
#                 if not trilha.assistido:
#                     assistido = False; break
#                 assistido = assistido and trilha.assistido
#     return assistido if not neutro else False
# elif tipo == "homecare":
#     assistidos = [trilha.assistido for Trilha in instance.get_trilhas_homecare()
#                   if (trilha := get_trilha(Trilha, instance, instance.tipo)) and trilha.alerta != "NEUTRO"]
#     return bool(assistidos and not assistidos.count(False))
```

## Edge cases (as implemented)
If ALL of a bed's non-manual trilhas are NEUTRO, the commented algorithm returns False (not True) for 'assistido' - an all-neutral bed is reported as NOT attended, which may be counter-intuitive (this all-neutral->False behavior IS confirmed for the manual/movimentacao path in RULE-013).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference exists. This is a proprietary internal business rule: an aggregation of IntensiCare care-pathway (trilha) alert states into a per-bed boolean 'assistido' (attended-by-care-team) flag. It is not a validated clinical score, equation, or standard calculator (not APACHE/SAPS/SOFA/etc.), and no clinical guideline governs how a bed-management UI derives an 'attended' boolean from internal traffic-light alert levels.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/leito.py | 191-200, 365-395 (commented, dead) | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-007
- Related rules: RULE-MOVIMENTACAO-ADT-013, RULE-MOVIMENTACAO-ADT-046

## Notes
Kept SEPARATE from RULE-013 (the confirmed active manual-path assistido resolution) because this is the Leito-serializer variant for automatica/homecare beds delegating to an unread Leito.get_assistido model property; only dead-code evidence is available here. NOT merged (different bed-type family, unconfirmed). A verifier with access to core/models/leito.py must confirm whether the live property matches the commented algorithm and RULE-013.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
