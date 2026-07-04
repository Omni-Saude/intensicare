# RULE-AUTH-USUARIOS-039 — User update performs diff-based setor sync scoped to current empresa

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When updating a user's setores_id, the serializer computes a symmetric difference against the user's currently-known setores: newly listed setores are added (UsuarioSetor + UsuarioEstabelecimento bulk_create), and setores no longer listed are removed - but the removal query is additionally scoped to setor__estabelecimento__empresa=request.empresa, so setores belonging to a different empresa than the current context are never removed even if absent from the new list.

## Inputs

| name | type |
|---|---|
| setores_id | array of uuid |

## Outputs

| name | type |
|---|---|
| usuario.setores | M2M-like set (through UsuarioSetor) |

## Logic

```text
setores_existentes = list(instance.setores.values_list("pk", flat=True))
setores_novos = [s for s in setores if s not in setores_existentes]
remover_setores = [s for s in setores_existentes if s not in setores]
if remover_setores:
    UsuarioSetor.objects.filter(
        usuario=usuario, setor__in=remover_setores,
        setor__estabelecimento__empresa=empresa
    ).delete()
if setores_novos:
    bulk_create UsuarioSetor(usuario, setor_id) for setor in setores_novos
    bulk_create UsuarioEstabelecimento(usuario, estabelecimento) for new estabelecimentos not already linked
```

## Edge cases (as implemented)

verificar_setor_da_empresa(setores, empresa) is called before the diff, so all NEW setores in the payload must belong to the current empresa (raises otherwise); setores from other companies already assigned to the user are left untouched even if omitted from the payload.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/usuario.py` | 141-189 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-003`

**Related rules:**

- [RULE-AUTH-USUARIOS-038](RULE-AUTH-USUARIOS-038-user-creation-links-to-current-empresa-and-syncs-setores-gru.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
