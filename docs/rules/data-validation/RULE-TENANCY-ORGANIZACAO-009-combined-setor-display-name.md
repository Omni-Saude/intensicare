# RULE-TENANCY-ORGANIZACAO-009 — Combined setor display name

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
SetorUsuarioSerializer.get_nome concatenates the parent establishment's name and the sector's own name for display.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.estabelecimento.nome | string |  |
| instance.nome | string |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| nome | string |  |

## Logic

```text
return instance.estabelecimento.nome + " - " + instance.nome
```

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Internal display-string rule: SetorUsuarioSerializer.get_nome returns instance.estabelecimento.nome + ' - ' + instance.nome. Legacy verbatim confirmed at core/api/v1/serializers/setor.py:22-23 @ 8166c07.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 22-23 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-001`

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
