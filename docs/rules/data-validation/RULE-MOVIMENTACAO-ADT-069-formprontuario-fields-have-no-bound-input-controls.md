# RULE-MOVIMENTACAO-ADT-069 — FormProntuario fields have no bound input controls

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Every Form.Item in the patient-record (Prontuário) creation form is declared with a `name` and `label` but no child input component, meaning none of the listed fields (paciente.nome, paciente.codigo, paciente.data_nascimento, paciente.genero, leito, data_entrada, and the final "Dados Prontuário" item) actually render an editable control or capture any value.

## Outputs
| Name | Type | Unit |
|---|---|---|
| form values on submit | effectively {} for the fields listed | n/a |

## Logic
```text
<Form.Item label="Nome do paciente" name={["paciente","nome"]}></Form.Item>
<Form.Item label="Código" name={["paciente","codigo"]}></Form.Item>
<Form.Item label="Data de nascimento" name={["paciente","data_nascimento"]}></Form.Item>
<Form.Item label="Gênero" name={["paciente","genero"]}></Form.Item>
<Form.Item label="leito" name="leito"></Form.Item>
<Form.Item label="Data de entrada" name="data_entrada"></Form.Item>
... (all rendered only when !pacienteCodigo)
<Form.Item></Form.Item>   // final, unnamed and childless
```

## Edge cases (as implemented)
Since Form.Item has no child, antd renders just the label with no input control at all; calling form.submit() would produce an onFinish payload missing these fields entirely (or with whatever stale values Form state happens to hold from elsewhere), regardless of what the user does on screen.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FormProntuario/FormProntuario.tsx | 13-47 | f9656be2 | primary |

- Merged from: RULE-prontuario-FE-05-001
- Related rules: None

## Notes
Recorded verbatim per audit ground rules even though it looks like an incomplete/broken implementation (a stub) rather than an intentional rule; a verifier should check whether a newer FormProntuario variant elsewhere in the app actually binds these fields, since as written this component captures no patient/admission data.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
