# RULE-EVOLUCOES-055 — Cannot inactivate a released (liberado) form - validation rule defined

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A helper method exists that forbids inactivating (soft-deleting) a Formulario whose status is already "liberado" (released/finalized).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.status [e.g. 'liberado'] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| raises ValidationError or no-op |  |  |

## Logic
```text
def validar_inativacao(instance):
    if instance.status == "liberado":
        raise ValidationError("Não é possível inativar um registro que já foi liberado!")
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_base.py` | 142-149 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-017
- Related rules: RULE-EVOLUCOES-030, RULE-EVOLUCOES-051

## Notes
See RULE-formulario-BE-08-018: this method is DEFINED but never invoked by destroy() in this commit, so the guard is currently inert / not enforced on the actual delete path.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
