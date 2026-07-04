# RULE-TRILHAS-ENGINE-007 — Mark-pathway-assisted eligibility and own-record authorization

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
A user may mark a pathway as "Assistido" (attended) only when the pathway has a non-NEUTRO alert, has criteria, the user holds can_assist_ocupacao, and a postAssistido handler exists. A pathway already assisted by another user cannot be toggled; only the user who assisted it may un-assist it. Any eligible user may check (assist); only the owner may uncheck.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilha.alerta | enum(string) |  | must be truthy and !== "NEUTRO" |
| trilha.criterios | array |  |  |
| can_assist_ocupacao | boolean (permission) |  |  |
| trilha.assistido | boolean |  |  |
| trilha.assistido_por.id | string |  |  |
| user.usuario.id | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| postAssistido(ocupacao.id, {tipo, assistido, id}) | side-effect |  |

## Logic
```text
showAssistCheckbox =
  trilha.alerta AND trilha.alerta !== "NEUTRO"
  AND trilha.criterios AND can_assist_ocupacao AND postAssistido
checkbox.defaultChecked = trilha.assistido
checkbox.disabled =
  trilha.assistido_por
  AND user.usuario.id !== trilha.assistido_por.id
  AND trilha.assistido                       // assisted by someone else -> locked
canUncheck =
  trilha.assistido_por
  AND user.usuario.id === trilha.assistido_por.id
  AND trilha.assistido                       // only owner can uncheck
onClick(e):
  if ((canUncheck AND !e.target.checked) OR e.target.checked):
    postAssistido(ocupacao.id, { tipo: trilha.tipo,
                                 assistido: e.target.checked,
                                 id: trilha.id })
```

## Edge cases (as implemented)
Checking (assist) is always permitted for eligible users. Unchecking is only submitted when canUncheck is true; an uncheck attempt by a non-owner is short-circuited (the button is also disabled). A pathway with NEUTRO or no alert, or without criteria, shows no assist control.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TabRecomendacoes/TabRecomendacoes.tsx` | 156-211 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-007`
- Related rules: RULE-TRILHAS-ENGINE-004

## Notes
Author name shown truncated to 10 chars on collapsed (<1260px) viewports, else 256 (lines 201-204). tipo is the pathway type sent back so the backend knows which pathway was assisted.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
