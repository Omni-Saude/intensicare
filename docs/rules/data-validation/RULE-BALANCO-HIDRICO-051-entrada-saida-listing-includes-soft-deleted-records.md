# RULE-BALANCO-HIDRICO-051 — Entrada/Saida listing includes soft-deleted records

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
EntradasViewSet.get_queryset() uses the default `Entrada.objects` manager (not `objects_without_deleted`), so soft-deleted entrada records (deletado_por/deletado_em set) remain visible in list/retrieve responses, ordered with deleted-state first.

## Inputs

- balancos__pk (URL kwarg)

## Outputs

- queryset

## Logic

```text
Entrada.objects.select_related("balanco")
  .filter(balanco_id=kwargs["balancos__pk"])
  .order_by("-deletado_em", "criado_em")
```

## Edge cases (as implemented)

No exclusion of soft-deleted rows; ordering by "-deletado_em" descending relies on the database's NULL ordering behavior (Postgres default: NULLS come first in DESC), so active (non-deleted, NULL deletado_em) records are typically listed before deleted ones, then by ascending creation time.

## Divergence

EntradasViewSet.get_queryset() (entradas.py:29-35) and SaidasViewSet.get_queryset() (saidas.py:27-33) both use the DEFAULT .objects manager (not objects_without_deleted), so soft-deleted records (deletado_em/deletado_por set) remain visible in list/retrieve, ordered .order_by('-deletado_em','criado_em') (relies on Postgres NULLS-first in DESC to list active rows before deleted). Contrasts with BalancoHidricoViewSet and HorarioPrescricaoViewSet which use objects_without_deleted. Both viewsets diverge identically from that convention.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/entradas.py` | 29-35 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/views/saidas.py` | 27-33 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-entrada-BE-08-010`
- `RULE-saida-BE-08-045`

**Related rules:**

- [RULE-BALANCO-HIDRICO-026](../care-pathway/RULE-BALANCO-HIDRICO-026-balanco-hidrico-sub-record-delete-authorization-can-delete-e.md)

## Notes

Contrasts with BalancoHidricoViewSet and HorarioPrescricaoViewSet, which both use `objects_without_deleted`. Same pattern repeats identically in saidas.py (RULE-saida-BE-08-045) and sinais_vitais.py (RULE-sinal-BE-08-048).

Phase-1 notes also referenced a parallel sinais_vitais.py capture (RULE-sinal-BE-08-048) with the same pattern, but no such entry exists in this cluster's input set; only the entrada and saida captures were present and are merged here.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
