# RULE-INDICADORES-ETL-011 — get_procedimentos_invasivos — invasive-procedure code lookup

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
If a micro_indicador record exists and its PROC_INVASIVO flag == 'S' (yes), splits the comma-separated CD_PROC_INVASIVO code string and maps each recognized code to a (tipo, nome) pair via a fixed lookup table of 10 known procedure codes (central venous access variants, orotracheal intubation, tracheostomy, indwelling urinary catheter variants); unrecognized codes are silently skipped.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| micro_indicador | MicroIndicadores instance or None |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| payload | list of {tipo: str, nome: str} |  |

## Logic
```text
procedimentos = {
  "148": ("puncao_de_acesso_venoso_central_mono_lumen", "Punção de Acesso Venoso Central Mono Lúmen"),
  "706": ("puncao_de_acesso_venoso_central_duplo_lumen", "Punção de Acesso Venoso Central Duplo Lúmen"),
  "707": ("puncao_de_acesso_venoso_central_triplo_lumen", "Punção de Acesso Venoso Central Triplo Lúmen"),
  "145": ("implante_de_cateter_venoso_central_por_puncao_cvc", "Implante de Cateter Venoso Central Por Punção - Cvc"),
  "734": ("implante_de_cateter_venoso_central_para_hemodialise", "Implante de Cateter Venoso Central Para Hemodialise"),
  "705": ("colocação_de_cateter_venoso_central_ou_portocath", "Colocação De Cateter Venoso Central Ou Portocath"),
  "140": ("intubacao_orotraqueal", "Intubação orotraqueal"),
  "20": ("traqueostomia", "Traqueostomia"),
  "13": ("passagem_de_sonda_vesical_de_demora_2_vias", "Passagem de Sonda Vesical de Demora - 2 Vias"),
  "236": ("passagem_de_sonda_vesical_de_demora_3_vias", "Passagem de Sonda Vesical de Demora - 3 Vias"),
}
IF micro_indicador AND micro_indicador.PROC_INVASIVO == "S":
  FOR codigo IN micro_indicador.CD_PROC_INVASIVO.split(","):
    IF codigo IN procedimentos:
      tipo, nome = procedimentos[codigo]
      payload.append({"tipo": tipo, "nome": nome})
RETURN payload  # [] if micro_indicador is falsy or PROC_INVASIVO != "S"
```

## Edge cases (as implemented)
Codes not in the 10-entry table are silently dropped (no error, no logging). PROC_INVASIVO must be the exact string 'S'; any other value (including lowercase 's') yields an empty list.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/micro_indicadores.py` | 1-44 | `8166c07e` | primary |

- Merged from: RULE-indic-BE-11-049
- Related rules: RULE-INDICADORES-ETL-012

## Notes
The numeric codes resemble Brazilian healthcare procedure/billing codes (TUSS-like); classified here as care-pathway since they feed clinical indicator displays, but could equally be viewed as billing-administrative — flagged as a categorization judgment call.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
