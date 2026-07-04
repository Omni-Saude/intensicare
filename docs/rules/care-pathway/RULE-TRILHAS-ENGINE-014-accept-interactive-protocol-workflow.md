# RULE-TRILHAS-ENGINE-014 — Accept interactive protocol workflow

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
Accepting a protocol POSTs { aceito: true }, refreshes the occupancy, and navigates to the protocol screen. The Accept button is disabled once a protocol instance already exists (trilha_interativa !== null) and its label switches from "Aceitar" to "Aceito".

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilha.trilha_interativa | object\|null |  |  |
| trilha.can_criar_novo_protocolo | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| POST body | object |  |

## Logic
```text
// Accept controls shown when (can_criar_novo_protocolo || trilha_interativa)
acceptButton.disabled = (trilha.trilha_interativa !== null)
acceptButton.label    = trilha.trilha_interativa ? "Aceito" : "Aceitar"
onClick:
  _postTrilhaInterativa({ aceito: true })   // POST .../<trilha.id>
  onSubmit(idOcupacao)
  goToProtocolos()
// If already accepted, show:
//   "Aceito por <registrado_por.nome> em <horario_registro_aceitacao DD/MM/YYYY HH:mm>"
```

## Edge cases (as implemented)
aceito is sent as a boolean true on accept (contrast RULE-TRILHAS-ENGINE-015 which sends the string "false"). Button disabled purely on trilha_interativa !== null, so a null (never-created) protocol is acceptable, any existing instance is not.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TrilhaInterativa/TrilhaInterativa.tsx` | 199-233 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-003`
- Related rules: RULE-TRILHAS-ENGINE-005, RULE-TRILHAS-ENGINE-015

## Notes
Navigation target goToProtocolos (lines 165-173) builds /empresa/.../ocupacao/<idOcupacao>/<trilha.nome.toLowerCase()>/<trilha.id>} NOTE the template literal appends a stray literal "}" after ${trilha.id} (line 170), producing a trailing "}" in the URL path — recorded as a bug, not corrected. Verifier: confirm routing tolerance.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
