# RULE-MOVIMENTACAO-ADT-036 — Homecare bed 'trilhas' list is a static fixed template, not per-patient data

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
_get_trilhas_homecare returns a fixed 3-item list built by calling get_payload() at the CLASS level (PrescricaoContinua.get_payload(), BalancoHidrico.get_payload(), Formulario.get_payload()) rather than any instance/patient-specific query. All code that would fetch the bed's actual PioraClinica/Sepse records, or append ventilacao/eficiencia entries, is commented out (dead). As a result every homecare bed's 'trilhas' list is currently identical regardless of the patient's real clinical state.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| instance | Leito |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| trilhas | array of object |  |

## Logic
```text
def _get_trilhas_homecare(instance):
    # (dead) piora_clinica = PioraClinica.objects.filter(...).order_by("-criado_em").first()
    # (dead) sepse = Sepse.objects.filter(nr_atendimento=instance.nr_atendimento).order_by("-criado_em").first()
    trilhas = [
        PrescricaoContinua.get_payload(),   # called on the class, not an instance
        BalancoHidrico.get_payload(),
        Formulario.get_payload(),
    ]
    # (dead) trilhas.append(piora_dict); trilhas.append(sepse_dict)
    # (dead) trilhas.append(ventilacao_payload_fake); trilhas.append(eficiencia_payload_fake)
    return trilhas
```

## Edge cases (as implemented)
Because get_payload() is invoked on the model class (not an instance), whatever it returns is necessarily a generic/default template rather than data queried for this specific instance/nr_atendimento.

## Divergence
Regression/incompleteness (single-implementation): the active code returns a class-level static template while surrounding dead code shows a richer intended per-patient implementation (piora_clinica/sepse lookups + ventilacao/eficiencia). Recorded verbatim, not corrected.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/leito.py` | 118-179 | `8166c07e` | primary |

- Merged from: RULE-leito-BE-05-004
- Related rules: RULE-MOVIMENTACAO-ADT-018, RULE-MOVIMENTACAO-ADT-037

## Notes
A verifier should check whether trilha_homecare/api or a newer version of this file supersedes this one.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
