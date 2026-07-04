# RULE-OPERACIONAL-INFRA-057 — upload_to — model-type-based storage folder convention

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Determines the storage sub-folder prefix for an uploaded file based on the type of the owning model instance: Usuario -> 'usuario', ObservacaoArquivo -> 'observacao', Empresa -> 'empresa', Formulario -> 'formulario-<instance.tipo>'. If the instance type matches none of these, raises a ValidationError instructing that a prefix must be set.

## Inputs

| name | type | unit |
|---|---|---|
| instance | Django model instance (Usuario \| ObservacaoArquivo \| Empresa \| Formulario \| other) |  |
| filename | string |  |

## Outputs

| name | type | unit |
|---|---|---|
| path | string |  |

## Logic

```text
prefix = ""
IF isinstance(instance, Usuario): prefix = "usuario"
ELIF isinstance(instance, ObservacaoArquivo): prefix = "observacao"
ELIF isinstance(instance, Empresa): prefix = "empresa"
IF isinstance(instance, Formulario): prefix = "formulario-" + instance.tipo   # note: independent `if`, not `elif`
IF NOT prefix: RAISE ValidationError({"file": "Não foi possível fazer upload, coloque um prefixo para pasta."})
RETURN "{prefix}/{instance.pk}-{filename}"
```

## Edge cases (as implemented)

The Formulario check is a separate `if`, not chained via `elif` to the preceding Usuario/ObservacaoArquivo/Empresa checks — harmless in practice since the four types are mutually exclusive classes, but notable as the only branch NOT part of the elif chain.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 76-96 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-util-BE-11-043`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
