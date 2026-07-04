# RULE-OPERACIONAL-INFRA-058 — verificar_setor_da_empresa — tenant-hierarchy consistency check

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
For each Setor whose pk is in a given list, validates that its estabelecimento's empresa matches the given empresa; raises a ValidationError naming the offending setor if not.

## Inputs

| name | type | unit |
|---|---|---|
| setores | list of Setor pks |  |
| empresa | Empresa instance |  |

## Outputs

| name | type | unit |
|---|---|---|
| validity | raises ValidationError otherwise |  |

## Logic

```text
FOR setor IN Setor.objects.filter(pk__in=setores):
  IF setor.estabelecimento.empresa != empresa:
    RAISE ValidationError({"setores": f"O setor {setor.nome} não pertence a empresa {empresa.nome}."})
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 99-106 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-util-BE-11-044`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-051](RULE-OPERACIONAL-INFRA-051-uniqueness-constraints-across-org-hierarchy.md)

## Notes

Conceptually duplicates the tenant-hierarchy checks performed at the HTTP-request level by EstabelecimentoMiddleware/SetorMiddleware (RULE-mw-BE-11-060, 061) — same business rule enforced in two different layers (explicit call-site validation vs URL-path middleware).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
