# RULE-OPERACIONAL-INFRA-051 — Uniqueness constraints across org hierarchy

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
Composite uniqueness rules that structure the company > establishment > sector > bed hierarchy and identity fields.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| hierarchy identifiers | mixed |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| DB uniqueness | constraint |  |

## Logic

```text
Estabelecimento: unique_together(empresa, codigo)
Setor:           unique_together(estabelecimento, codigo)
Leito:           unique_together(setor, codigo, nome)
Empresa.whitelabel unique; Usuario.username unique; Usuario.cpf unique
UsuarioEmpresa unique_together(usuario, empresa)
UsuarioEstabelecimento unique_together(usuario, estabelecimento)
UsuarioSetor unique_together(usuario, setor)
UsuarioGrupoAcesso unique_together(usuario, grupo)
UsuarioNotificacao unique_together(notificacao, usuario)
UsuarioSetorPaciente unique_together(usuario, setor, paciente)
Reacao unique_together(observacao, usuario)  # see RULE-029
Glossario.nome unique
```

## Edge cases (as implemented)

Enforced at DB level; codes are scoped to their immediate parent (not globally unique).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 56-58 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-data-BE-04-051`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-058](RULE-OPERACIONAL-INFRA-058-verificar-setor-da-empresa-tenant-hierarchy-consistency-chec.md)

## Notes

Aggregated constraint rule. Individual sources: estabelecimento.py:29, setor.py:26, leito.py:58, empresa.py:14, usuario.py:53/18-29, usuario_empresa.py:14, usuario_estabelecimento.py:15, usuario_setor.py:15, usuario_grupo_acesso.py:13, usuario_notificacao.py:13, usuario_setor_paciente.py:15, reacao.py:19, glossario.py:6.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
