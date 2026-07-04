# RULE-TRILHAS-ENGINE-015 — Refuse interactive protocol workflow (justification required)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
Refusing a protocol requires a free-text justification (motivo_descartado, required) and submits aceito = "false". If a protocol instance already exists it is PATCHed; otherwise a new one is POSTed with the refusal. On submit the occupancy is refreshed and the form reset.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| motivo_descartado | string (required) |  | non-empty (defaultFormRules required) |
| trilha.trilha_interativa | object\|null |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| PATCH/POST body | object |  |

## Logic
```text
onFinish(values):
  if (trilha.trilha_interativa):
    _patchTrilhaInterativa(trilha.trilha_interativa.id, { ...values, aceito: "false" })
  else:
    _postTrilhaInterativa({ ...values, aceito: "false" })
  onSubmit(idOcupacao)
  refuseForm.resetFields()
// values.motivo_descartado is required (Form.Item rules=defaultFormRules)
```

## Edge cases (as implemented)
aceito is submitted as the STRING "false" on refuse, whereas accept (RULE-TRILHAS-ENGINE-014) submits the BOOLEAN true. The Justificativa field is mandatory via defaultFormRules (required validator). Modal okText "Recusar".

## Divergence
Same `aceito` field is typed inconsistently across the two sibling workflows: accept (RULE-TRILHAS-ENGINE-014) sends boolean true, refuse (this rule) sends the string "false". Recorded verbatim from Phase 1; both go to the same interactive-protocol endpoint. Best interpretation: backend coerces both. Verifier should confirm the API accepts string "false" and boolean true interchangeably.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TrilhaInterativa/TrilhaInterativa.tsx` | 105-154 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-004`
- Related rules: RULE-TRILHAS-ENGINE-005, RULE-TRILHAS-ENGINE-014

## Notes
AMBIGUOUS/divergence flag is for the accept(boolean true) vs refuse(string "false") type inconsistency in the `aceito` field. defaultFormRules is defined in utils/defaultFormRules (out of partition) and enforces required-non-empty.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
