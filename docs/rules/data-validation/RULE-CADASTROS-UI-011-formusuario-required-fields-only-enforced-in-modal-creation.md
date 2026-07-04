# RULE-CADASTROS-UI-011 — FormUsuario required fields only enforced in modal (creation) mode

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Nome, CPF, username, password and e-mail are only marked as required (defaultFormRules / emailFormRules applied) when the form is rendered in "modal" mode (i.e. creating a new professional); in "in_page" (edit-in-place) mode these same fields render without the required rule.

## Inputs

| name | type |
|---|---|
| mode | 'in_page' \| 'modal' |

## Outputs

| name | type |
|---|---|
| Form.Item rules for nome/cpf/username/email/password | array \| undefined |

## Logic

```text
for each of [nome, cpf, username, password]:
  rules = (mode === "modal") ? defaultFormRules : undefined
email:
  rules = [...emailFormRules, ...(mode === "modal" ? defaultFormRules : [])]
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormUsuario/FormUsuario.tsx` | 111-216 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-005`

**Related rules:** _none_

## Notes

The same mode-gated required-field pattern (required only in "modal"/create mode) also appears in FormEstabelecimento.tsx, FormSetor.tsx and FormLeito.tsx.

VERIFICATION CORRECTION (this pass): the Phase-1 note claims "the same mode-gated required-field pattern ...also appears in FormEstabelecimento.tsx, FormSetor.tsx and FormLeito.tsx". Re-reading those three files at commit f9656be2660ec2048ce6240b4ac418b7fe7d5a5b shows this is NOT accurate: FormEstabelecimento.tsx (nome/codigo, lines 39-60), FormLeito.tsx (nome/codigo, lines 40-56) and FormSetor.tsx (estabelecimento_id/nome/codigo, lines 44-72) all declare `rules={defaultFormRules}` UNCONDITIONALLY (always required), with no `mode === "modal"` gate at all - they only gate field VISIBILITY or DISABLED state by mode/tipo, never the required-ness of the rule itself. FormUsuario.tsx (this rule) is the only one of the four forms that actually gates required-ness by mode. The original Phase-1 note is preserved above for traceability but should be treated as incorrect regarding the other three forms.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
