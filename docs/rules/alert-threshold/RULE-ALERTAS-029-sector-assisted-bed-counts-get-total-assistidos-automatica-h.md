# RULE-ALERTAS-029 — Sector assisted-bed counts (get_total_assistidos_automatica / _homecare)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | alertas |

## Rule

Sector 'total_assistidos' (assisted beds) KPI, two paths. Automatica: counts occupied beds where leito.get_assistido (RULE-ALERTAS-009) is truthy. Homecare: for each bed it collects the `assistido` flag of every non-NEUTRO homecare track and counts the bed only if there is at least one such track AND none of them is False. Feeds setor/estabelecimento 'total_assistidos' (setor.py:257,266; estabelecimento.py:216,225).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| leitos | iterable[Leito] | - | - |
| leito.get_assistido (automatica) | bool | - | RULE-ALERTAS-009 |
| homecare track .alerta / .assistido | string / bool|null | - | alerta != NEUTRO contributes |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total_assistidos | int | bed count |

## Logic

```text
# get_total_assistidos_automatica(leitos):
total_assistidos = 0
for leito in leitos:
    if leito.ocupado and leito.get_assistido:
        total_assistidos += 1
return total_assistidos

# get_total_assistidos_homecare(leitos):
Trilhas = Leito.get_trilhas_homecare()
total_assistidos = 0
for leito in leitos:
    assistidos = []
    for Trilha in Trilhas:
        trilha = get_trilha(Trilha, leito, leito.tipo)
        if trilha and trilha.alerta != "NEUTRO":
            assistidos.append(trilha.assistido)
    if assistidos and not assistidos.count(False):
        total_assistidos += 1
return total_assistidos
```

## Edge cases (as implemented)

Automatica path delegates the per-bed decision to leito.get_assistido (RULE-ALERTAS-009). Homecare path: a bed with NO non-NEUTRO tracks yields assistidos == [] -> the `assistidos and ...` guard is falsy -> the bed is NOT counted (a fully-neutral bed is never 'assisted'). Only an explicit False in assistidos blocks the count: `not assistidos.count(False)` treats an assistido value of None as 'not False', so a None among non-neutral tracks still lets the bed count as assisted. Only non-NEUTRO homecare tracks contribute.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 332-361 | `8166c07e` | primary |

- Merged from: RULE-gap6-03
- Related rules: RULE-ALERTAS-009, RULE-ALERTAS-008

## Notes

Feeds setor/estabelecimento 'total_assistidos'. Mirrors the per-bed rule RULE-ALERTAS-009 but the sector-count aggregation (notably the homecare `assistidos and not assistidos.count(False)` predicate) is a distinct, previously uncited predicate.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
