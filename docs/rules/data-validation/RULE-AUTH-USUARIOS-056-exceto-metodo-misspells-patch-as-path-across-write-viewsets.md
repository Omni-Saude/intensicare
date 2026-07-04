# RULE-AUTH-USUARIOS-056 — exceto_metodo misspells PATCH as PATH across write viewsets

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Four viewsets (Entradas, Saidas, SinaisVitais, HorarioPrescricao) each declare exceto_metodo = ("GET", "POST", "PUT", "PATH") alongside a permission_trilhas requirement (e.g. "can_delete_balanco_hidrico"). The string "PATH" does not match the actual HTTP method name "PATCH". If the consuming mixin (ManageDataRequiredMixin, out of partition) checks `request.method in self.exceto_metodo` to decide whether permission_trilhas should be enforced, PATCH requests would NOT be excepted (since "PATCH" is absent from the tuple), meaning partial-update requests would be subject to a permission named for deletion ("can_delete_..."), inconsistent with GET/POST/PUT being excepted.

## Inputs

| name | type | range |
|---|---|---|
| request.method | string | 'GET'\|'POST'\|'PUT'\|'PATCH'\|'DELETE' |

## Outputs

| name | type |
|---|---|
| permission_trilhas enforcement | boolean (inferred) |

## Logic

```text
exceto_metodo = ("GET", "POST", "PUT", "PATH")   # should plausibly be "PATCH"
# assumed consumer logic (in core.mixins.view.ManageDataRequiredMixin, out of scope):
# if request.method not in self.exceto_metodo: enforce(permission_trilhas)
```

## Edge cases (as implemented)

Exact enforcement semantics depend on core.mixins.view.ManageDataRequiredMixin, which is outside partition BE-08. Recorded verbatim as found; the identical typo appears in all four files listed below.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/entradas.py` | 26-27 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-permissao-BE-08-031`

**Related rules:**

- [RULE-AUTH-USUARIOS-009](../billing-administrative/RULE-AUTH-USUARIOS-009-scope-based-rbac-permission-dispatch.md)
- [RULE-AUTH-USUARIOS-015](RULE-AUTH-USUARIOS-015-get-and-patch-bypass-can-manage-usuario-permission.md)

## Notes

Identical tuple ("GET","POST","PUT","PATH") also present in trilha_homecare/api/v1/views/saidas.py:24-25, trilha_homecare/api/v1/views/sinais_vitais.py:26-27, and trilha_homecare/api/v1/views/horario_prescricao.py:27-28. Contrast with all BaseFormViewSet subclasses, which instead use a single string exceto_metodo = "GET" (whose Python `in` substring semantics happen to work correctly for excepting only GET).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
