# RULE-MOVIMENTACAO-ADT-020 — Bed patient resolution and auto-creation

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Resolves the Paciente for a bed by attendance number, falling back to an external Oracle patient record, then to pathway-embedded demographics, creating a Paciente row when found.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| nr_atendimento | string |  |  |
| ocupado | bool |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| Paciente | or {}) (Paciente\|dict |  |

## Logic
```text
paciente = Paciente.objects.filter(nr_atendimento__isnull=False, nr_atendimento=self.nr_atendimento).first()
if not paciente:
  paciente = {}
  if self.ocupado:
    oracle = InfoPaciente.objects.using("oracle").filter(NR_ATENDIMENTO=self.nr_atendimento).first()
    if oracle:
      create Paciente(nome=NM_PESSOA_FISICA, nr_atendimento=NR_ATENDIMENTO,
                      data_nascimento=DT_NASCIMENTO, genero=IE_SEXO, nome_mae=NM_MAE)
    else:
      for Trilha in get_trilhas_automaticas() (v3+v2, in order):
        trilha = get_trilha(Trilha, self, "automatica")
        if trilha:
          if trilha NOT in v3 set: fields from trilha.ds_paciente/nr_atendimento/dt_nascimento/ie_sexo
          else: fields from trilha.paciente.{nome,nr_atendimento,data_nascimento,genero,nome_mae}
          create Paciente(**fields); break   # first matching pathway wins
return paciente
```

## Edge cases (as implemented)
Cross-database read on the "oracle" connection. v2 pathways expose flat ds_paciente/ie_sexo; v3 pathways expose a nested .paciente. Returns {} if bed empty and no source found.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/leito.py | 189-244 | 8166c07e | primary |
- Merged from: RULE-paciente-BE-04-020
- Related rules: RULE-MOVIMENTACAO-ADT-041, RULE-MOVIMENTACAO-ADT-007

## Notes
Called in Leito.save() to set self.paciente. v3 vs v2 pathways are handled as distinct sources (variant handling), not merged.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
