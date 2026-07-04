# RULE-MOVIMENTACAO-ADT-046 — Assistido (attend-to) action on a bed's care pathway (frontend endpoint)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
Marking a specific care-pathway (trilha) on a bed occupancy as attended-to ("assistido") is performed via a dedicated POST endpoint accepting a partial Trilha payload; this action is gated elsewhere by the "can_assist_ocupacao" permission flag.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| idMovimentacao | string |  |  |
| body | Partial<Models.Ocupacao.Trilha> |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| response | unknown, untyped POST response |  |

## Logic
```text
POST empresas/{idEmpresa}/estabelecimentos/{idEstabelecimento}/setores/{idSetor}
     /ocupacoes/{idMovimentacao}/assistido/
body: Partial<Ocupacao.Trilha>
// gated by Permission "can_assist_ocupacao" (enforcement not present in this partition)
```

## Edge cases (as implemented)
No client-side check of the permission is performed before calling this endpoint in this partition (enforcement presumed server-side and/or via conditional rendering elsewhere).

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/networking/ocupacao.ts` | 72-92 | `f9656be2` | primary |

- Merged from: RULE-ocupacao-FE-07-007
- Related rules: RULE-MOVIMENTACAO-ADT-011, RULE-MOVIMENTACAO-ADT-013

## Notes
Permission cross-reference at src/@types/models/Permissions.d.ts line 8 ("can_assist_ocupacao").

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
