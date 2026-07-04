# RULE-PRESCRICAO-029 — Not-administered reason enum (motivo_nao_administrado)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Closed set of coded reasons a scheduled dose was not administered, mapped to human labels. Defined on the frontend (select options) and the backend (model choices + PDF humanize filter).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| motivo_nao_administrado | enum/string |  | recusa_paciente \| medicacao_suspensa \| nao_tem_farmacia \| outros(frontend-only) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| label | string |  |

## Logic

```text
# Frontend enum (src/utils/motivosNaoAdministrado.ts) - FOUR options:
recusa_paciente    -> "Paciente recusou a administração"   (patient refused)
medicacao_suspensa -> "Medicação suspensa pelo médico"     (suspended by physician)
nao_tem_farmacia   -> "Em falta na farmácia"               (out of stock)
outros             -> "Outros"                              (other)   # frontend-only

# Backend PrescricaoChoices.motivo() and templatetags humanize_choice - THREE codes only:
recusa_paciente    -> "Paciente recusou a administração"
medicacao_suspensa -> "Medicação suspensa pelo médico"
nao_tem_farmacia   -> "Em falta na farmácia"
# humanize_choice(val) = motivos[val]   # dict index, NO default -> KeyError on any other value
```

## Edge cases (as implemented)
Backend model field motivo_nao_administrado is a FREE CharField (not enum-constrained). humanize_choice does keyless dict indexing -> KeyError on any value outside the three codes. pdf_prescription_v2 prints the raw stored code instead (no crash).

## Divergence
Cross-implementation divergence: the FRONTEND enum defines FOUR options including 'outros' -> 'Outros'; the BACKEND (PrescricaoChoices.motivo() and templatetags humanize_choice) defines only THREE codes with NO 'outros'. When the frontend picks 'outros' it actually stores the free-text 'outros_motivos' string (RULE-PRESCRICAO-030), i.e. a value the backend enum does not recognise; humanize_choice (v1 PDF) then raises KeyError on that value (and on any code outside the three). v2 PDF prints the raw code and does not crash.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/motivosNaoAdministrado.ts` | 1-18 | `f9656be2` | frontend-copy |
| ahlabs-trilhas | `trilha_homecare/models/choices/prescricao.py` | 5-11 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_homecare/templatetags/prescricao.py` | 7-14 | `8166c07e` | duplicate |

**Merged from:**

- RULE-medicacao-FE-02-001
- RULE-prescricao-BE-06-004
- RULE-prescricao-BE-09-003

**Related rules:**

- RULE-PRESCRICAO-030
- RULE-PRESCRICAO-009

## Notes
NEW divergence surfaced during reconciliation: none of the three source captures was flagged in Phase 1, but comparing them shows the frontend adds a 4th 'outros' option that the backend enum / humanize_choice cannot map (KeyError). Labels otherwise match verbatim.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
