# RULE-BALANCO-HIDRICO-049 — Entrada/Saida default display name from tipo

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
If no "nome" is supplied when creating an Entrada, the record's display name is set to the humanized value of its "tipo" choice field.

## Inputs

- nome
- tipo

## Outputs

- nome

## Logic

```text
if not validated_data.nome:
    entrada.nome = entrada.get_tipo_display()
```

## Edge cases (as implemented)

Assignment happens on the in-memory `self.entrada` object AFTER super().create() already persisted the row without nome; entrada.save() is called later in the same create() (line ~116) so the default is still persisted, but only because of that trailing save — if that save call were ever removed the default would be silently lost.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/entradas.py` | 108-109 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/saidas.py` | 117-118 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-BE-07-004`
- `RULE-balanco-BE-07-012`

**Related rules:** _none_

## Notes

Same pattern duplicated in saidas.py (RULE-balanco-BE-07-013).
Identical in entradas.py:108-109 and saidas.py:117-118: `if not nome: obj.nome = obj.get_tipo_display()`. Assignment is on the in-memory object after super().create(); the value is persisted only by the trailing obj.save() later in create(). No divergence -> OK.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
