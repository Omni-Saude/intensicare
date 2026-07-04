# RULE-COMUNICACAO-035 — Homecare feed action-type vocabulary — acaoDict render map vs Feed.Acao TS union

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The setor activity feed renders each recorded 'ação' using a fixed dictionary mapping raw action keys to pt-BR display labels (acaoDict, 8 keys). Separately, the shared TypeScript model declares the closed Feed.Acao union type consumed by Feed.acoes — but that union only enumerates 7 values, omitting 'editar' even though acaoDict maps 'editar' -> 'Editar' and force-casts itself `as Record<Models.Feed.Acao, string>`.

## Inputs

| name | type | unit |
|---|---|---|
| acao | Models.Feed.Acao (declared: 7 values) at runtime rendered against an 8-key dict |  |

## Outputs

| name | type |
|---|---|
| displayed label | string |
| acao | string enum |

## Logic

```text
// FeedBallon.tsx:28-39 (render map — 8 keys)
acaoDict = {
  criar: "Criar", alterar: "Alterar", editar: "Editar", inativar: "Inativar",
  assinar: "Assinar", liberar: "Liberar", administrar: "Administrar",
  nao_administrar: "Não Administrar"
} as Record<Models.Feed.Acao, string>
render: itemFeed.acoes.map(acao => Tag(color="cyan", acaoDict[acao]))

// src/@types/models/Feed.d.ts:25-32 (declared union — 7 values, no 'editar')
type Feed.Acao =
  | "criar" | "alterar" | "inativar" | "assinar"
  | "liberar" | "administrar" | "nao_administrar"
```

## Edge cases (as implemented)

No fallback/default label is used for an unrecognized acao value — acaoDict[acao] would be undefined and the Tag would render with empty text rather than the raw key or a placeholder. Separately: the 'as Record<Models.Feed.Acao, string>' cast on an object literal with an EXTRA key ('editar') beyond the declared union bypasses TypeScript's excess-property check (assertions, unlike direct annotations, don't flag this), so this divergence would not surface as a compile error.

## Divergence

acaoDict (FeedBallon.tsx) implements 8 action keys including 'editar' -> 'Editar'; the Feed.Acao TS union (Feed.d.ts) declares only 7 values and omits 'editar' entirely. Either the type declaration is stale (the backend/model can emit an 'editar' action that renders correctly here but is not type-recognized anywhere else consuming Feed.Acao) or 'editar' is unreachable dead code in the dictionary — confirmed by direct inspection of both files at the pinned frontend commit.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FeedBallon/FeedBallon.tsx` | 28-39,161-170 | `f9656be266` | primary |
| trilhas-frontend | `src/@types/models/Feed.d.ts` | 25-32 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-feed-FE-05-001`
- `RULE-feed-FE-07-001`

**Related rules:**

- [RULE-COMUNICACAO-034](RULE-COMUNICACAO-034-validacao-de-leito-para-acao-de-feed-homecare.md)
- [RULE-COMUNICACAO-003](../care-pathway/RULE-COMUNICACAO-003-acaohomecare-balanco-hidrico-method-reference-bug.md)

## Notes

The Models.Feed.Acao type definition itself is out of this partition's scope; the enumerated keys are inferred solely from this dictionary's literal keys. | administrar/nao_administrar align with Prescricao's administrado boolean lifecycle (RULE-prescricao-FE-07-001); assinar/liberar align with the signing/release themes seen in BalancoHidrico and Evolucao.Status. | Reconciled during Phase-2: the Models.Feed.Acao type definition (out of the original FE-05 partition's scope) was located and compared directly against acaoDict's literal keys — divergence confirmed, not merely inferred.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
