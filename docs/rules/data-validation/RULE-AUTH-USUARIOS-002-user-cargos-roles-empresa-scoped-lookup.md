# RULE-AUTH-USUARIOS-002 — User cargos (roles) empresa-scoped lookup

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
get_cargos returns the list of 'cargo' values from all non-deleted GrupoAcesso records linking this user within the company (empresa) currently injected on the request. If no empresa is present on the request context, returns None (not an empty list).

## Inputs

| name | type |
|---|---|
| request.empresa | object\|null |

## Outputs

| name | type |
|---|---|
| cargos | array of string \| null |

## Logic

```text
request = context.get("request")
if request and request.empresa:
    grupos = GrupoAcesso.objects_without_deleted.filter(
        usuarios=instance, empresa=request.empresa
    ).values_list("cargo", flat=True)
    return grupos if grupos else []
else:
    return None
```

## Edge cases (as implemented)

Distinguishes 'no empresa in context' (returns None) from 'empresa present but user has no groups' (returns []).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published/clinical reference exists. Proprietary internal multi-tenant RBAC rule (empresa-scoped cargo/roles lookup in UsuarioSerializer.get_cargos). Not a clinical calculation, guideline, or standard calculator. ([source](n/a))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a (returns list of cargo strings or null) |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| request=null_or_no_empresa | n/a; source-faithful: None (bare return) | None — else branch 'return' yields None (source lines 45-46) | yes |
| request.empresa=E1; user_groups_in_E1=["Enfermeiro", "Auditor"] | n/a; source-faithful: ['Enfermeiro','Auditor'] (cargo values_list) | queryset of cargo values ['Enfermeiro','Auditor'] — truthy queryset returned as-is | yes |
| request.empresa=E1; user_groups_in_E1=[] | n/a; source-faithful: [] (empty list, NOT None) | [] — 'return grupos if grupos else []' yields [] for empty/falsy queryset (source line 44) | yes |

**Verifier notes**

Catalog logic verified byte-faithful against legacy source core/api/v1/serializers/usuario.py lines 32-46 (commit 8166c07). Key semantic distinction confirmed: 'no empresa in request context' returns None (bare `return`), while 'empresa present but user has no groups' returns [] — two distinct null-ish sentinels. Uses objects_without_deleted manager (soft-delete-aware) filtering on usuarios=instance AND empresa=request.empresa. No authoritative published reference exists for an internal empresa-scoped role lookup; flagged for internal review, NOT treated as wrong. Extraction status was OK; nothing contradicts the source.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/usuario.py` | 32-46 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-usuario-BE-05-001`

**Related rules:**

- [RULE-AUTH-USUARIOS-044](../billing-administrative/RULE-AUTH-USUARIOS-044-clinical-administrative-role-cargo-enumeration-backend-model.md)

## Notes

verify=true because Phase-1 type is 'formula' per audit criteria (non-clinical empresa-scoped roles lookup, not a clinical calculation).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
