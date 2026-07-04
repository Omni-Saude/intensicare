# RULE-EVOLUCOES-010 — Registered evolution types eligible for Tasy release, and their integration codes

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Only a fixed subset of professional evolution types are recognized as eligible for release into the external Tasy system, each mapped to a numeric integration code; "tecnico_enfermagem" (nursing technician) evolutions are explicitly excluded (commented out) from this set.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tipo [medico | enfermagem | fisioterapeuta | terapeuta | nutricionista | psicologo | musicoterapeuta | fonoaudiologo | intercorrencia] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| codigo_evolucao |  |  |

## Logic
```text
def get_evolucoes_para_liberar():
    return {
        "medico": 1151,
        # "tecnico_enfermagem": 1203,   # excluded
        "enfermagem": 1203,
        "fisioterapeuta": 1251,
        "terapeuta": 5,
        "nutricionista": 1133,
        "psicologo": 1131,
        "musicoterapeuta": 2332,
        "fonoaudiologo": 1121,
        "intercorrencia": 2584,
    }
def checar_tipo_evolucao_cadastrada(tipo):
    return tipo in get_evolucoes_para_liberar().keys()
def get_codigo_evolucao(tipo):
    return get_evolucoes_para_liberar().get(tipo)
```

## Edge cases (as implemented)
"tecnico_enfermagem" shares the same numeric code (1203) as "enfermagem" in the comment, but is entirely absent from the live dict — meaning technician evolutions can never be released to Tasy through this path (consistent with RULE-evolucao-BE-07-004's silent-skip behavior).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 351-377 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-011
- Related rules: RULE-EVOLUCOES-009, RULE-EVOLUCOES-011, RULE-EVOLUCOES-012

## Notes
AMBIGUOUS whether tecnico_enfermagem's exclusion is intentional (per-role Tasy config) or an oversight; recorded as implemented.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
