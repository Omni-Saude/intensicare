# RULE-SEPSE-097 — Sepsis protocol refusal permission

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sepse |

## Rule
Custom Django permission gating who may refuse (recusar) the sepsis protocol.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| user permission | permission | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| can_recusar_protocolo_sepse | permission | — |

## Logic
```text
Meta.permissions = (("can_recusar_protocolo_sepse", "Pode recusar protocolo de sepse"),)
```

## Edge cases (as implemented)
None documented beyond the permission declaration itself.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilhas_interativas/trilha_interativa_sepse.py` | 22-28 | 8166c07e | primary |

- Merged from: RULE-interativa-BE-03-133
- Related rules: RULE-SEPSE-074, RULE-SEPSE-071

## Notes
Lifecycle flags on TrilhaInterativaSpese (encerrado, finalizado, concluida, aceito) drive can_criar_novo_protocolo (RULE-sepse-BE-03-121).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
