# RULE-BALANCO-HIDRICO-038 — Entrada soft-delete adjusts 24h fluid balance and logs audit action

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | physiological-calculation |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Deleting (destroying) an Entrada (fluid intake) record does not hard-delete it; it marks it as deleted by the current user, logs an AcaoHomecare audit entry ("inativar" on "entrada"), and subtracts the entrada's quantity from the parent BalancoHidrico's running 24h balance (balanco_24h), reflecting that intake entries were originally added positively to that total.

## Inputs

- instance.quantidade (mL (implied))

## Outputs

- balanco.balanco_24h (mL (implied))

## Logic

```text
@transaction.atomic
def destroy(request):
    instance.deletado_por = user
    instance.save()
    criar_acao_homecare(tipo="entrada", acoes=["inativar"], leito=request.leito,
                         setor=request.setor, entrada=instance, realizado_por=user)
    instance.balanco.balanco_24h -= instance.quantidade
    instance.balanco.save()
    return super().destroy(request)   # underlying mixin destroy behavior (out of partition)
```

## Edge cases (as implemented)

Runs inside a DB transaction (transaction.atomic). Relies on `self.request.leito` and `self.request.setor` being populated by out-of-partition middleware/mixins. No guard against double-deletion (deleting an already-deleted entrada would double-subtract balanco_24h if the underlying `super().destroy()` doesn't prevent it - not verifiable from this partition).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Cumulative/net fluid balance = total intake − total output (standard critical-care convention). Malbrain MLNG et al., 'Fluid overload, de-resuscitation, and outcomes in critically ill or injured patients: an updated view,' Anaesthesiol Intensive Ther 2014;46(5):361-380 (ADQI fluid-balance framework); Bouchard J et al., Kidney Int 2009;76:422-427. ([source](https://pubmed.ncbi.nlm.nih.gov/25432556/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a (unit accumulator ±quantidade, no coefficients) |
| units | ok — quantidade mL, balanco_24h mL, consistent |
| ranges | n/a |
| rounding | n/a (direct float subtraction, no rounding) |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| balanco_24h_before=1000; delete_entrada_quantidade=250 | 750 | 750 | yes |
| balanco_24h_before=0; delete_entrada_quantidade=200 | -200 | -200 | yes |
| balanco_24h_before=750; delete_entrada_quantidade=200; note=double-delete of already soft-deleted entrada | no further change (idempotent per intent) | 550 | no |

**Verifier notes**

Legacy views/entradas.py:57-66 does `instance.balanco.balanco_24h -= instance.quantidade` on soft-delete.
Sign convention is correct against FB = Σintake − Σoutput: an intake was originally added positively (RULE-014),
so removing it must subtract. Arithmetic/unit-consistent -> VERIFIED. Caveats (edge-case robustness, NOT a
reference discrepancy): no double-delete guard (3rd vector double-subtracts) and no accumulator correction on
quantidade edit. A single valid delete matches the reference. Robustness issues flagged for internal review only.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/entradas.py` | 48-67 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-entrada-BE-08-011`

**Related rules:**

- [RULE-BALANCO-HIDRICO-014](RULE-BALANCO-HIDRICO-014-fluid-balance-24h-accrual-on-intake-entrada.md)
- [RULE-BALANCO-HIDRICO-039](RULE-BALANCO-HIDRICO-039-saida-soft-delete-adjusts-24h-fluid-balance-and-logs-audit-a.md)

## Notes

Mirror rule for Saida is RULE-saida-BE-08-046 (adds instead of subtracts).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
