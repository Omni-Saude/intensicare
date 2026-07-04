# RULE-BALANCO-HIDRICO-039 — Saida soft-delete adjusts 24h fluid balance and logs audit action

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
Deleting (destroying) a Saida (fluid output) record marks it as deleted by the current user, logs an AcaoHomecare audit entry ("inativar" on "saida"), and ADDS the saida's quantity back to the parent BalancoHidrico's running 24h balance (balanco_24h) - the mirror operation of Entrada's destroy (RULE-entrada-BE-08-011), confirming saida quantities are subtracted from balanco_24h when originally recorded.

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
    criar_acao_homecare(tipo="saida", acoes=["inativar"], leito=request.leito,
                         setor=request.setor, saida=instance, realizado_por=user)
    instance.balanco.balanco_24h += instance.quantidade
    instance.balanco.save()
    return super().destroy(request)
```

## Edge cases (as implemented)

Same double-deletion caveat as RULE-entrada-BE-08-011.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Net fluid balance = total intake − total output (mirror of RULE-038). ADQI/KDIGO fluid-management convention; Malbrain MLNG et al., Anaesthesiol Intensive Ther 2014;46(5):361-380; Bouchard J et al., Kidney Int 2009;76:422-427. ([source](https://pubmed.ncbi.nlm.nih.gov/25432556/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | ok — quantidade mL, balanco_24h mL |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| balanco_24h_before=750; delete_saida_quantidade=300 | 1050 | 1050 | yes |
| balanco_24h_before=-200; delete_saida_quantidade=500 | 300 | 300 | yes |
| balanco_24h_before=1050; delete_saida_quantidade=300; note=double-delete of already soft-deleted saida | no further change | 1350 | no |

**Verifier notes**

Legacy views/saidas.py:44-53 does `instance.balanco.balanco_24h += instance.quantidade` on soft-delete — exact
mirror of RULE-038. An output was originally subtracted (RULE-015), so deleting it must add back. Sign/unit
consistent with FB = Σintake − Σoutput -> VERIFIED. Same double-delete / no-update-correction caveat as RULE-038
(3rd vector); edge-case robustness, not a reference discrepancy. Flagged for internal review.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/saidas.py` | 35-54 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-saida-BE-08-046`

**Related rules:**

- [RULE-BALANCO-HIDRICO-015](RULE-BALANCO-HIDRICO-015-fluid-balance-24h-accrual-on-output-saida.md)
- [RULE-BALANCO-HIDRICO-038](RULE-BALANCO-HIDRICO-038-entrada-soft-delete-adjusts-24h-fluid-balance-and-logs-audit.md)

## Notes

Mirror of RULE-entrada-BE-08-011.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
