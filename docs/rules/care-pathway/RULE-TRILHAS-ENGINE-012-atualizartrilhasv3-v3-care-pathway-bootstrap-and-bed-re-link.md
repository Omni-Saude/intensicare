# RULE-TRILHAS-ENGINE-012 — AtualizarTrilhasV3 — v3 care-pathway bootstrap and bed re-linking

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | trilhas-engine |

## Rule
For a given bed (leito), ensures the patient has exactly one instance of each of the five automatic v3 care pathways (Eficiencia, Sedacao, Estabilidade, Sepse, Profilaxia), creating any missing ones tied to the current leito/paciente/nr_atendimento, then re-points ALL FIVE existing pathway instances' leito foreign key to the current leito.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| leito | Leito model instance |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| trilhas_*_v3 records | created/updated model rows |  |

## Logic
```text
paciente = leito.paciente
FOR (related_name, Model) IN [
  ("trilhas_eficiencia_v3", TrilhaEficienciaV3Model),
  ("trilhas_sedacao_v3", TrilhaSedacaoV3Model),
  ("trilhas_estabilidade_v3", TrilhaEstabilidadeV3Model),
  ("trilhas_sepse_v3", TrilhaSepseV3Model),
  ("trilhas_profilaxia_v3", TrilhaProfilaxiaV3Model),
]:
  IF NOT getattr(paciente, related_name).exists():
    Model.objects.create(leito=leito, paciente=paciente, nr_atendimento=leito.nr_atendimento)
trilhas = [
  paciente.trilhas_sedacao_v3.first(), paciente.trilhas_eficiencia_v3.first(),
  paciente.trilhas_estabilidade_v3.first(), paciente.trilhas_sepse_v3.first(),
  paciente.trilhas_profilaxia_v3.first(),
]
FOR trilha IN trilhas:
  trilha.leito = leito
  trilha.save()
```

## Edge cases (as implemented)
get_trilhas() re-fetches via the paciente relation with .first() and NO filter on nr_atendimento — if a patient has pathway records from a prior encounter/admission, this could re-point a stale pathway record's leito to the new bed instead of creating/using an encounter-scoped one.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/atualizar_trilhas_v3.py` | 1-45 | `8166c07e` | primary |

- Merged from: `RULE-trilha-BE-11-002`
- Related rules: RULE-TRILHAS-ENGINE-001, RULE-TRILHAS-ENGINE-003, RULE-TRILHAS-ENGINE-011

## Notes
AMBIGUOUS: whether patients are expected to only ever have one lifetime record per v3 pathway type (making the missing nr_atendimento filter harmless) or one per encounter (making it a bug) cannot be determined from this partition alone; flag for verifier with access to trilha_automatica/models.py. The five v3 pathways match the v3 composition set in RULE-TRILHAS-ENGINE-001.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
