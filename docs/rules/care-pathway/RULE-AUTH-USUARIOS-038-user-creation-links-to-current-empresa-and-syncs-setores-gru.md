# RULE-AUTH-USUARIOS-038 — User creation links to current empresa and syncs setores/grupos

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
When a Usuario is created, it is always linked to request.empresa via UsuarioEmpresa. If setores_id is supplied, all sectors must belong to that empresa (validated by verificar_setor_da_empresa, which raises if not); the user is bulk-linked to every listed setor (UsuarioSetor) and to every distinct parent Estabelecimento not already linked (UsuarioEstabelecimento). If grupos_acessos_ids is a list, the user's access groups are set (replace-all).

## Inputs

| name | type |
|---|---|
| setores_id | array of uuid |
| grupos_acessos_ids | array of uuid |

## Outputs

| name | type |
|---|---|
| usuario | object |

## Logic

```text
usuario = super().create(validated_data)
UsuarioEmpresa.objects.create(usuario=usuario, empresa=request.empresa)
if isinstance(setores, list):
    verificar_setor_da_empresa(setores, request.empresa)  # raises if any setor not in empresa
    estabelecimentos_novos = Estabelecimento.objects.filter(
        Q(setores__in=setores), ~Q(usuarios=usuario)
    ).distinct("pk")
    bulk_create UsuarioSetor(usuario, setor_id) for setor in setores
    bulk_create UsuarioEstabelecimento(usuario, estabelecimento) for estabelecimento in estabelecimentos_novos
if isinstance(grupos_acessos_ids, list):
    usuario.grupos_acessos.set(grupos_acessos_ids)
```

## Edge cases (as implemented)

foto_perfil_b64, if provided, is converted to a file before create. No duplicate-check on UsuarioSetor bulk_create beyond what's implied by the caller-supplied list (could error on unique constraint if duplicated).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/usuario.py` | 107-139 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-039](RULE-AUTH-USUARIOS-039-user-update-performs-diff-based-setor-sync-scoped-to-current.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
