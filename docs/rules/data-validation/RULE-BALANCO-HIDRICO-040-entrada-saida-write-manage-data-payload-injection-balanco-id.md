# RULE-BALANCO-HIDRICO-040 — Entrada/Saida write manage_data payload injection (balanco id + assinar passthrough)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When writing an Entrada, the parent balanco id is injected from the nested route kwarg, and an 'assinar' (sign) flag is passed through into the write payload only if present/truthy.

## Inputs

- balancos__pk (URL kwarg)
- assinar (payload field)

## Outputs

- data["balanco"]
- data["assinar"]

## Logic

```text
if isinstance(balanco, str): data["balanco"] = balanco
assinar = data.pop("assinar", None)
if assinar: data["assinar"] = assinar
```

## Edge cases (as implemented)

If balanco kwarg is not a str (e.g. already a model instance), it is not overwritten.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/entradas.py` | 69-82 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/views/saidas.py` | 56-67 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-entrada-BE-08-012`
- `RULE-saida-BE-08-047`

**Related rules:** _none_

## Notes

'assinar' semantics (electronic signature) are implemented in the serializer (out of partition, BE-07).
Identical logic in entradas.py view (69-82) and saidas.py view (56-67): if isinstance(balanco,str): data['balanco']=balanco; assinar=data.pop('assinar',None); if assinar: data['assinar']=assinar. 'assinar' semantics implemented in the serializers (RULE-BALANCO-HIDRICO-033 / signature flow).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
