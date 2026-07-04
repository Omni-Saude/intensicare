# RULE-TENANCY-ORGANIZACAO-039 — Company owner (proprietario) access lifecycle on save

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Saving a company guarantees its owner has the 'p' (Proprietário) access code, and revokes 'p' from the previous owner when they no longer own any company.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| proprietario | Usuario FK |  |  |
| proprietario_antigo | Usuario FK (previous) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| proprietario.acessos | list[char] |  |

## Logic
```text
On Empresa.save():
  original = self.original_object  # DB state before save
  if "p" not in self.proprietario.acessos: append "p"; save proprietario
  proprietario_antigo = original.proprietario
  if self.proprietario != proprietario_antigo
     and NOT proprietario_antigo.empresas_proprietarias.exclude(pk=self.pk).exists():
        proprietario_antigo.acessos = [a for a in acessos if a != "p"]; save
  super().save()
```

## Edge cases (as implemented)
Uses original_object (pre-save snapshot from SetUpModel); on first create the old owner comparison relies on original.proprietario. exclude(pk=self.get_pk) prevents counting the company being reassigned.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/empresa.py | 44-62 | 8166c07e | primary |

- Merged from: RULE-empresa-BE-04-010

## Notes
Pairs with 'u' management in RULE-acesso-BE-04-031.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
