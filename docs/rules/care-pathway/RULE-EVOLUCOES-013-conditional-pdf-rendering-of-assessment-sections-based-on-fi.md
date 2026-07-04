# RULE-EVOLUCOES-013 — Conditional PDF rendering of assessment sections based on filled fields

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When building the print/PDF context for a nursing evolution, each assessment section (abdominal, cardiologic, genital, global, neurological, ventilation, invasive devices) is flagged as "present" for rendering only if at least one of its non-metadata fields is non-null; for invasive devices, each device sub-panel is additionally checked/flagged individually.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| formulario.<avaliacao>.__dict__ (per assessment section) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| context[<avaliacao>] |  |  |
| context["lista_dispositivos_existentes"] |  |  |

## Logic
```text
avaliacoes = ["avaliacao_abdominal","avaliacao_cardiologica","avaliacao_genital",
              "avaliacao_global","avaliacao_neurologica","avaliacao_ventilacao",
              "dispositivos_invasivos"]
dispositivos_invasivos = ["acesso_venoso_periferico","cateter_duplo_lumen_hemodialise",
              "cateter_venoso_central","fistula_arteriovenosa","hipodermoclise",
              "pressao_arterial_invasiva","port_a_cath","picc"]
for avaliacao in avaliacoes:
    if avaliacao == "dispositivos_invasivos":
        for sub_campo in dispositivos_invasivos:
            dispositivo = getattr(getattr(formulario, avaliacao), sub_campo)
            if not isinstance(dispositivo, dict):
                continue
            lista_auxiliar = [v for k, v in dispositivo.items()
                               if k not in ("formulario_id","id","criado_em","modificado_em","_state")
                               and v is not None]
            if bool(lista_auxiliar):
                lista_dispositivos_existentes.append(sub_campo)
            lista.extend(lista_auxiliar)
    else:
        lista = [v for k, v in vars(getattr(formulario, avaliacao)).items()
                 if k not in ("formulario_id","id","criado_em","modificado_em","_state")
                 and v is not None]
    context[avaliacao] = bool(lista)
context["lista_dispositivos_existentes"] = lista_dispositivos_existentes
```

## Edge cases (as implemented)
A section renders as "present" (True) if ANY single field is non-None, even if that field is e.g. an empty string or a False boolean (only None is excluded, not falsy values in general) — meaning a section with just one explicitly-False checkbox field will still show as "filled".

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_enfermagem.py` | 226-323 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-013
- Related rules: none

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
