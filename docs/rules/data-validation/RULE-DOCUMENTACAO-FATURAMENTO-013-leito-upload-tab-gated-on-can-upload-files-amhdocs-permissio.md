# RULE-DOCUMENTACAO-FATURAMENTO-013 — Leito upload tab gated on can_upload_files_amhdocs permission

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
The "Enviar arquivo" tab (and the drawer's Save/Ok button) inside the leito files drawer is only rendered/enabled for users holding the can_upload_files_amhdocs permission; users without it only see the "Arquivos Enviados" (already-sent files) tab.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| can_upload_files_amhdocs | boolean (from useEffectivePermissions()) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| visibility of "Enviar arquivo" Tabs.TabPane | boolean |  |
| DrawerBuilder hideOk | boolean |  |

## Logic
```text
hideOk = !can_upload_files_amhdocs
if can_upload_files_amhdocs:
  render Tabs.TabPane("Enviar arquivo") containing FilesPickContent
always render Tabs.TabPane("Arquivos Enviados") containing ArquivosContent
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FilesLeitoComponent/FilesLeitoComponent.tsx | 35,46,50-60 | f9656be2 | primary |
- Merged from: RULE-upload-FE-05-004
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-012

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
