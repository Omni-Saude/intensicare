# RULE-MOVIMENTACAO-ADT-070 — FilterOcupacoes "todos" sentinel and occupancy creation-type filter

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
The Ocupações list filter defaults "Leitos" (ocupado) to "todos" and explicitly converts that sentinel to undefined (no filter) before calling onFilter, while "true"/"false" pass through unchanged; it also exposes a "Tipo" filter distinguishing manually-created vs automatically-created occupancy records.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ocupado | 'todos' (default) \| 'true' \| 'false' | n/a | n/a |
| tipo | 'manual' \| 'automatica' | n/a | n/a |

## Outputs
| Name | Type | Unit |
|---|---|---|
| onFilter({ ocupado, tipo, nome, ... }) | Models.Ocupacao.Filter | n/a |

## Logic
```text
Form initialValues: { ocupado: "todos" }
onFinish(value):
  onFilter({ ...value, ocupado: value.ocupado === "todos" ? undefined : value.ocupado })
Select("ocupado"): Option("todos")->Todos, Option("true")->Ocupados, Option("false")->Vazios
Select("tipo"): Option("manual")->Manual, Option("automatica")->Automático
```

## Edge cases (as implemented)
Only the "todos" value is special-cased to undefined; "tipo" has no default/no-filter option exposed in the UI (no "todos" equivalent for tipo), so a tipo filter, once touched, cannot be cleared back to "no filter" other than via the form's external onClear/reset.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FilterOcupacoes/FilterOcupacoes.tsx | 13-46 | f9656be2 | primary |

- Merged from: RULE-filtro-FE-05-004
- Related rules: None

## Notes
Cross-reference RULE-filtro-FE-05-003 for the inconsistent sentinel handling between the two filters.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
