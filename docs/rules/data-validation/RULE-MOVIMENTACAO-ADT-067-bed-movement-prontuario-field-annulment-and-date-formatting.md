# RULE-MOVIMENTACAO-ADT-067 — Bed-movement prontuário field annulment and date formatting

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
When submitting a bed occupancy change (add patient / new movimentação / remove patient), the sub-records noradrenalina, parada cardiorrespiratória, and ventilação mecânica are included only if truthy AND not "empty" (per utils/isEmpty), otherwise sent as undefined (explicit annulment/clear); their horario_inicio (and, for ventilação mecânica, horario_fim) datetime fields are reformatted to "YYYY-MM-DD HH:mm". Sedativos is included as a {nome_sedativo, quantidade} array only if non-empty, else undefined. Patient sub-record reformats data_nascimento to "YYYY-MM-DD" and strips CPF mask formatting via unformat().

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| values.dados_prontuario.noradrenalina | object \| undefined | n/a | n/a |
| values.dados_prontuario.parada_cardiorrespiratoria | object \| undefined | n/a | n/a |
| values.dados_prontuario.ventilacao_mecanica | object \| undefined | n/a | n/a |
| values.dados_prontuario.sedativos | array \| undefined | n/a | n/a |
| values.paciente.data_nascimento | date | n/a | n/a |
| values.paciente.cpf | string (masked) | n/a | n/a |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valuesToSubmit.dados_prontuario | object | n/a |
| valuesToSubmit.paciente | object | n/a |

## Logic
```text
isPresent(field) = field && !isEmpty(field)
noradrenalina_out = isPresent(nora) ? { ...nora, horario_inicio: nora.horario_inicio && moment(nora.horario_inicio).format("YYYY-MM-DD HH:mm") } : undefined
parada_out        = isPresent(pcr)  ? { ...pcr,  horario_inicio: pcr.horario_inicio  && moment(pcr.horario_inicio).format("YYYY-MM-DD HH:mm") } : undefined
ventilacao_out     = isPresent(vm)   ? { ...vm, horario_inicio: vm.horario_inicio && moment(vm.horario_inicio).format("YYYY-MM-DD HH:mm"),
                                                 horario_fim:    vm.horario_fim    && moment(vm.horario_fim).format("YYYY-MM-DD HH:mm") } : undefined
sedativos_out = (sedativos && sedativos.length > 0) ? sedativos.map(s => ({ nome_sedativo: s.nome_sedativo, quantidade: s.quantidade })) : undefined
paciente_out = paciente ? { ...paciente,
                             data_nascimento: paciente.data_nascimento && moment(paciente.data_nascimento).format("YYYY-MM-DD"),
                             cpf: paciente.cpf && unformat(paciente.cpf) } : undefined
// then dispatched by `type`:
switch(type) { case "add": postAddPaciente(...); case "mov": postNovaMovimentacao(...); case "remove": postRemoverPaciente(...) }
```

## Edge cases (as implemented)
A field object that is truthy but considered "empty" by utils/isEmpty (out of partition) is annulled (sent as undefined) exactly like an absent field — the API cannot distinguish "user cleared this section" from "user never touched it".

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ListOcupacoes/ListOcupacoes.tsx | 172-245 | f9656be2 | primary |

- Merged from: RULE-prontuario-FE-06-013
- Related rules: None

## Notes
Complements RULE-prontuario-FE-06-014, which performs the inverse (string -> moment) transform for read/display of a past prontuário. utils/isEmpty and utils/formatter (unformat) are out of this partition's scope.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
