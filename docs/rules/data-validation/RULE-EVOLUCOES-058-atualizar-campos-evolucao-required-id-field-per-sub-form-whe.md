# RULE-EVOLUCOES-058 — atualizar_campos_evolucao — required 'id' field per sub-form when updating an evolution

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When updating the dynamic sub-forms (campos) of an evolution, each campo's data dict must contain an 'id' key identifying the existing sub-record to update; if missing, raises a ValidationError naming which campo (chave) is missing its id. Campos with no data (falsy 'valor') are skipped entirely (not created, not updated, no error).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| campos_formulario |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| updated sub-form records |  |  |

## Logic
```text
FOR campo IN campos_formulario:
  Model = campo["model"]; data = campo.get("valor", {})
  IF data:
    TRY: pk = data.pop("id")
    EXCEPT KeyError: RAISE ValidationError(f"O campo {campo.get('chave','')} está sem id!! Favor Verificar se o id está sendo enviado!")
    create_object_serializer(instance=Model.objects.get(pk=pk), Serializer=campo["serializer"], data=data, partial=True)
```

## Edge cases (as implemented)
A campo with a falsy 'valor' (e.g. {} or None) is silently skipped with no update and no error, distinct from a campo with a truthy valor missing only the 'id' key (which does raise).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/evolucoes.py` | 45-83 | `8166c07e` | primary |
- Merged from: RULE-evo-BE-11-074
- Related rules: none

## Notes
Companion function criar_campos_evolucao (same file, lines 11-42) performs the analogous CREATE-time factory loop but has no comparable required-field predicate worth extracting as a separate rule.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
