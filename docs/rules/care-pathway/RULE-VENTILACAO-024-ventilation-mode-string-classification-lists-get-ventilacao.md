# RULE-VENTILACAO-024 — Ventilation-mode string classification lists (get_ventilacao)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Returns, for a given ventilation category key, the list of free-text strings treated as belonging to that category; used by trilha models to bucket a recorded ventilation description into spontaneous / mechanical / mechanical-invasive / room-air.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo (string: ventilacao_espontanea | ventilacao_mecanica | ventilacao_mecanica_invasiva | ar_ambiente | other) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| match_list (list<string> | null) | | |

## Logic

```text
return {
  "ventilacao_espontanea": [
      "espontanea", "espontaneo", "espontaneo", "espontnaea", "espontanea",
      "espontanea"(=espontanea), "espontaneo em AA", "estpotanea", "esponatea",
      "cateter nasal", "cateter", "ve pela tqt por mascara", "mascara facial de o2",
      "O2", "vni/ mascara facial"],
  "ventilacao_mecanica": ["vm", "mecanica", "mecanica"],
  "ventilacao_mecanica_invasiva": ["invasiva vm", "invasiva", "vm invasiva"],
  "ar_ambiente": ["aa", "ar ambiente", "ar amb", "em ambiente", "ar ambienten"],
}.get(tipo)   # returns None for unknown tipo
```

## Edge cases (as implemented)

Matching is exact-string membership (callers use `value in get_ventilacao(...)` / splat into __in querysets), so any spelling not in the list is NOT classified. Lists contain duplicates and misspellings matched VERBATIM.

## Divergence

Exact-string membership preserves typos verbatim ('espontnaea','estpotanea','esponatea','espontaneo em AA', 'ar ambienten') and duplicates ('espontaneo' x2, 'espontanea' variants); it misclassifies 'vni/ mascara facial' (non-invasive ventilation) and 've pela tqt por mascara' (via tracheostomy) as ventilacao_espontanea rather than mechanical, and 'espontaneo em AA' as spontaneous rather than ar_ambiente. Record VERBATIM - do not correct.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/utils.py` | 100-130 | `8166c07e` | primary |

- Merged from: RULE-CLASSIF-BE-12-010
- Related rules: RULE-VENTILACAO-025

## Notes

Original accented strings preserved in source (espontanea/espontanea variants, mecanica, mascara). Callers: trilha_eficiencia, trilha_profilaxia, trilha_estabilidade, trilha_sepse (v3 models). Because matching is exact, a correctly-spelled input like 'espontaneo' without the extra token, or 'ventilacao espontanea', would miss.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
