# RULE-BALANCO-HIDRICO-042 — Fluid-balance record signature eligibility

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A fluid-balance record (entrada, saida, or sinais vitais) may be signed only when it is active, not yet signed, and the current user is permitted. Signing issues a PATCH with { assinar: true }. Once signed (data_assinatura present) the sign action disappears and "Assinado em: <data_assinatura>" is shown.

## Inputs

- item.ativo
- item.data_assinatura
- item.can_assinar
- can_manage_balanco_hidrico

## Outputs

- sign action available?

## Logic

```text
showSignButton =
  item.ativo
  AND (item.data_assinatura is falsy)     // not yet signed
  AND item.can_assinar
  AND can_manage_balanco_hidrico           // (enforced in ItemSinaisVitais and
                                           //  in BalancoHidricoContent action col)
onConfirmSign -> onSign(route, item.id)
// Backend call: PATCH .../<route>/<id_registro> with body { assinar: true }
```

## Edge cases (as implemented)

A record already signed (data_assinatura truthy) never shows the sign button. An inactive/removed record (ativo=false) shows neither sign nor delete, and instead shows "Removido por: <deletado_por.nome>". In ItemEntrada and ItemSaida the button gate omits the explicit can_manage check (only !data_assinatura && can_assinar), whereas ItemSinaisVitais and the table action column additionally require can_manage_balanco_hidrico.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/BalancoHidricoItens/ItemSinaisVitais/ItemSinaisVitais.tsx` | 128-150 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-03-005`

**Related rules:**

- [RULE-BALANCO-HIDRICO-033](RULE-BALANCO-HIDRICO-033-balanco-hidrico-sub-record-digital-signature-eligibility-can.md)
- [RULE-BALANCO-HIDRICO-034](../triage-eligibility/RULE-BALANCO-HIDRICO-034-fluid-balance-action-authorization-manage-delete-permissions.md)
- [RULE-BALANCO-HIDRICO-043](RULE-BALANCO-HIDRICO-043-saida-record-sign-posts-to-the-entrada-route-bug.md)
- [RULE-BALANCO-HIDRICO-045](RULE-BALANCO-HIDRICO-045-fluid-balance-record-signing-deletion-lifecycle.md)

## Notes

Sign body { assinar: true } comes from BalancoHidricoContent.tsx _patchBalancoHidricoRegistro (lines 194-209). The same signature gate is duplicated across ItemEntrada (lines 79-99), ItemSaida (lines 87-107), and the desktop table action column ButtonShowRequest (BalancoHidricoContent.tsx lines 259-342, which also requires can_manage_balanco_hidrico at line 271).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
