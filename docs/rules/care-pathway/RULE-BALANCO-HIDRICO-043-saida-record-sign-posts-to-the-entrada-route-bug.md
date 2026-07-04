# RULE-BALANCO-HIDRICO-043 — Saida record sign posts to the "entrada" route (bug)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When signing a fluid OUTPUT (saida) record from its card, the sign handler is invoked with the route argument "entrada" instead of "saida". The remove handler on the same card correctly uses "saida".

## Inputs

- item.id

## Outputs

- onSign call

## Logic

```text
// ItemSaida sign confirm:
onConfirm = () => onSign("entrada", item.id)   // BUG: should be "saida"
// ItemSaida remove confirm (correct):
onConfirm = () => onRemove("saida", item.id)
```

## Edge cases (as implemented)

onSign ultimately calls PATCH .../<route>/<id_registro>. With route="entrada" the PATCH targets the entrada endpoint using a saida record id, which will either 404/error or, worst case, mis-route the signature.

## Divergence

ItemSaida card sign confirm calls onSign('entrada', item.id) instead of onSign('saida', item.id); onSign issues PATCH .../<route>/<id_registro>, so the signature PATCH targets the entrada endpoint using a saida record id (404/error or mis-routed signature). The remove handler on the same card correctly uses onRemove('saida', item.id). Manifests on the mobile/card render path (ItemSaida.tsx:93); the desktop table action column signs with the correct outer `route` variable. Likely copy-paste bug from ItemEntrada; recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/BalancoHidricoItens/ItemSaida/ItemSaida.tsx` | 93-93 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-03-006`

**Related rules:**

- [RULE-BALANCO-HIDRICO-042](RULE-BALANCO-HIDRICO-042-fluid-balance-record-signature-eligibility.md)

## Notes

DISCREPANCY / likely copy-paste bug from ItemEntrada. Recorded verbatim, not corrected. Note the mobile-card sign path is only reached for entrada/saida via ItemMobileRender in BalancoHidricoContent (which passes onSign = _patchBalancoHidricoRegistro); the desktop table action column signs with the correct outer `route` variable, so the bug manifests on the mobile/card render.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
