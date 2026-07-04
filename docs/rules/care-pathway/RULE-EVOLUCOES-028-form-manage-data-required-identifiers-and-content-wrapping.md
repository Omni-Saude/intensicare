# RULE-EVOLUCOES-028 — Form manage_data - required identifiers and content wrapping

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
On write, every form payload is stamped with tipo (the form's tipo_formulario), leito id, and nr_atendimento derived strictly from the 'ocupacoes__pk' URL kwarg (no nr_atendimento fallback, unlike the read path). Each named "conteudo" content block (here just "impressao_geral" at the base level; subclasses add more, see RULE-formulario-BE-08-019..029) is moved into a "<conteudo>_data" key and tagged with "tipo_conteudo": "<conteudo>".

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ocupacoes__pk (URL kwarg) |  |  |  |
| impressao_geral (payload field) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| data["tipo"] |  |  |
| data["leito"] |  |  |
| data["nr_atendimento"] |  |  |
| data["impressao_geral_data"] |  |  |

## Logic
```text
leito = Leito.objects.get(pk=kwargs["ocupacoes__pk"])   # raises if kwarg missing/invalid
data["tipo"] = tipo_formulario
data["leito"] = str(leito.id)
data["nr_atendimento"] = leito.nr_atendimento
for conteudo in ["impressao_geral"]:
    data[f"{conteudo}_data"] = {**data.pop(conteudo, {}), "tipo_conteudo": conteudo}
```

## Edge cases (as implemented)
Unlike get_queryset()/get_leito(), this write path has no nr_atendimento-query-param fallback: a write request lacking 'ocupacoes__pk' in the URL will raise (Leito.DoesNotExist or similar) rather than the friendly "Não foi possível identificar o leito" ValidationError from get_leito().

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_base.py` | 68-90 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-015
- Related rules: RULE-EVOLUCOES-006, RULE-EVOLUCOES-017

## Notes
Each conteudo block missing from the incoming payload defaults to an empty dict ({}) via data.pop(conteudo, {}).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
