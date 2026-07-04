# RULE-PRESCRICAO-009 — Medication administration status -> checkbox icon and actor label (decision tree)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
In the prescription-check PDFs, each scheduled dose horario is rendered with a tri-state status icon and an actor label derived from the 'administrado' flag and whether a not-administered reason exists.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario.administrado | boolean or null |  | True \| False \| None |
| horario.motivo_nao_administrado | string enum or null |  |  |
| horario.checado_por | user or null |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| rendered status | icon + label |  |

## Logic

```text
# icon (both templates):
if administrado == True:              filled/checked circle icon   (dose given)
elif administrado == False and motivo_nao_administrado:  X / crossed circle icon (not given, with reason)
else:                                 empty circle icon            (pending / no data)
# actor label (v1, pdf_prescription.html):
if motivo_nao_administrado:  show "Motivo:" humanize_choice(motivo)
if administrado == True:               label "Checado por:"  checado_por.nome
elif administrado == False and checado_por:  label "Registrado por:" checado_por.nome
```

## Edge cases (as implemented)
administrado is a strict tri-state: only literal True shows the given-icon; False-with-reason shows the X; every other case (False without reason, or None/pending) shows the empty circle. v1 humanizes the reason via humanize_choice; v2 prints motivo raw and lays doses into 2 columns.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/templates/arquivos/pdf_prescription.html` | 213-241 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-09-002

**Related rules:**

- RULE-PRESCRICAO-029
- RULE-PRESCRICAO-011

## Notes
Same tri-state icon logic duplicated in pdf_prescription_v2.html (lines 202-218 and 256-272, rendered twice for the split-column and single-column table variants). v2 is the newer layout (tabular, get_splited_query). Cross-reference RULE-prescricao-BE-09-003 for the reason enum.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
