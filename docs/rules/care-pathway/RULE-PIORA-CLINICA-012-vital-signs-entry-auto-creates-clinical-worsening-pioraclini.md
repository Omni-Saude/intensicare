# RULE-PIORA-CLINICA-012 — Vital signs entry auto-creates clinical-worsening (PioraClinica) record

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Every time a SinaisVitais (vital signs) record is created, the system automatically creates a linked PioraClinica ("clinical worsening") record for the same encounter, unconditionally.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais (created instance) | object reference | — | — |
| nr_atendimento | string/integer (encounter number) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| PioraClinica record | object | — |

## Logic
```text
PioraClinica.objects.create(
    sinais_vitais=self.sinais_vitais,
    nr_atendimento=self.sinais_vitais.balanco.nr_atendimento,
)
```

## Edge cases (as implemented)
Triggered unconditionally on every vital-signs creation, regardless of the actual vital sign values — the clinical-worsening evaluation logic itself (if any threshold exists) lives in the PioraClinica model, out of this partition's scope.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/sinais_vitais.py | 130-133 | 8166c07e | primary |
- Merged from: RULE-sepse-BE-07-001

## Notes
Runs immediately before the Sepse-record trigger (RULE-sepse-BE-07-002) in the same create() call.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
