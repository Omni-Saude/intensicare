# RULE-EVOLUCOES-009 — Evolution release (liberar) gated by registered evolution type

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Releasing ("liberar") an evolution document to the external Tasy system only actually triggers the release if (a) the caller requested it AND (b) the evolution's "tipo" is one of a fixed set of registered professional types; for any other tipo, the release flag is accepted but the Tasy call is silently skipped.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| liberar (flag) |  |  |  |
| formulario.tipo [must be a key of get_evolucoes_para_liberar()] |  |  |  |
| formulario.preenchido_por.cpf |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| formulario.dt_liberacao |  |  |

## Logic
```text
def liberar(formulario, liberar):
    if liberar and checar_tipo_evolucao_cadastrada(formulario.tipo):
        validar_cpf(formulario.preenchido_por)   # raises if no cpf
        formulario.dt_liberacao = timezone.now()
        liberar_evolucao.apply_async(args=[
            formulario.preenchido_por.cpf,
            formulario.nr_atendimento,
            get_codigo_evolucao(formulario.tipo),
        ])
        acoes.append("liberar")
```

## Edge cases (as implemented)
If tipo is not registered (e.g. "tecnico_enfermagem" — see RULE-evolucao-BE-07-006), calling this with liberar=True does nothing at all: no cpf validation, no dt_liberacao stamp, no async task, and no "liberar" action logged — yet the caller (create()/update()) may still have set formulario.status == "liberado" believing the release actually happened.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 212-224 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-004
- Related rules: RULE-EVOLUCOES-010, RULE-EVOLUCOES-011, RULE-EVOLUCOES-053

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
