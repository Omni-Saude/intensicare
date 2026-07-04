# RULE-MOVIMENTACAO-ADT-021 — Homecare vs automatica bed classification and tenant routing

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Beds sourced from the Tasy occupancy view are split into two care streams. A bed is HOME CARE only when cd_tipo_leito == 3 AND ds_tipo_leito == "HOME CARE"; those rows are routed to the "homecare" tenant (whitelabel="homecare", tipo="homecare"). All other beds are the "automatica" (ICU/hospital) stream, routed to whitelabel "americashealth", tipo="automatica".

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| cd_tipo_leito | integer |  |  |
| ds_tipo_leito | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| stream | enum {homecare, automatica} |  |

## Logic
```text
homecare_qs   = base.filter(cd_tipo_leito == 3 AND ds_tipo_leito == "HOME CARE")
automatica_qs = base.exclude(cd_tipo_leito == 3 AND ds_tipo_leito == "HOME CARE")
create_empresa_setor_leito(automatica_qs, whitelabel="americashealth", tipo="automatica")
create_empresa_setor_leito(homecare_qs,  whitelabel="homecare",       tipo="homecare")
# Django filter(a, b) == a AND b ; exclude(a, b) == NOT (a AND b)
```

## Edge cases (as implemented)
Both conditions must be true simultaneously for HOME CARE; a bed with cd_tipo_leito==3 but ds_tipo_leito != "HOME CARE" falls into the automatica stream. String comparison is exact/case-sensitive equality (not icontains).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/etl/estabelecimento_setor_leito.py | 117-130 | 8166c07e | primary |
- Merged from: RULE-leito-BE-02-001
- Related rules: RULE-MOVIMENTACAO-ADT-052, RULE-MOVIMENTACAO-ADT-024

## Notes
Whitelabel strings ("americashealth", "homecare") are hardcoded tenant identifiers.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
