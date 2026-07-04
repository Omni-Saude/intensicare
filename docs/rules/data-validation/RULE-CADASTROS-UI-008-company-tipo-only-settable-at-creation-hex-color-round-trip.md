# RULE-CADASTROS-UI-008 — Company "tipo" only settable at creation; hex color round-trip

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The company (Empresa) form only renders the "Tipo" (manual/automática) selector when opened in "modal" (creation) mode - it is not editable afterward through this form. The primary brand color (cor_primaria) is stored/transmitted without its leading "#", but is re-prefixed with "#" when loading initialValues so the native color <input type="color"> can display it.

## Inputs

| name | type |
|---|---|
| mode | 'in_page' \| 'modal' |
| values.cor_primaria | string (hex, no '#') |
| initialValues.cor_primaria | string (hex, no '#') |

## Outputs

| name | type |
|---|---|
| rendered "Tipo" field | boolean (present only if mode === "modal") |
| submitted cor_primaria | string (hex without '#') |

## Logic

```text
render Form.Item("tipo") only if mode === "modal"     // Options: manual | automatica
onFinish: cor_primaria = values.cor_primaria ? values.cor_primaria.replace("#","") : values.cor_primaria
Form initialValues.cor_primaria = initialValues.cor_primaria ? "#" + initialValues.cor_primaria : undefined
logo submitted as values.logo.b64 if present, else omitted
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormEmpresa/FormEmpresa.tsx` | 16-42,71-78 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-008`

**Related rules:**

- [RULE-CADASTROS-UI-002](RULE-CADASTROS-UI-002-leito-estabelecimento-name-and-code-locked-for-non-manual-co.md)

## Notes

The component's internal variable/function is named "FormGrupo" and its own comment-free code otherwise gives no hint that it is the Empresa form - confirmed only via the Props type (Models.Usuario.Empresa) and field content (logo, whitelabel, tempo_atualizacao). Folder/file names are unreliable per audit ground rules; this is called out explicitly.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
