# RULE-TRILHAS-ENGINE-002 — Homecare-bed pathway composition

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
Homecare beds evaluate exactly two pathway models — PioraClinica and Sepse.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| none (static) |  |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| pathway model list | list[Model] |  |

## Logic
```text
get_trilhas_homecare() = [PioraClinica, Sepse]  (from trilha_homecare.models)
```

## Edge cases (as implemented)
Homecare bed detail/payload additionally injects static NEUTRO stub cards for PrescricaoContinua, BalancoHidrico, Formulario, Ventilação, and Eficiência (display-only, not scored).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 165-167 | `8166c07e` | primary |

- Merged from: `RULE-trilha-BE-04-017`
- Related rules: RULE-TRILHAS-ENGINE-001, RULE-TRILHAS-ENGINE-003

## Notes
Static stub cards at leito.py lines 521-546 / 585-608.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
