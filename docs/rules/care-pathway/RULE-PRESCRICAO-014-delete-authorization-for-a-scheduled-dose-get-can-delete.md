# RULE-PRESCRICAO-014 — Delete authorization for a scheduled dose (get_can_delete)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Whether the requesting user may delete a scheduled-dose (HorariosPrescricao) record. Both serializers allow it for the original creator (criado_por == user); they diverge in how the permission is sourced and in the fallback when request context is missing.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.user | User |  |  |
| request.empresa | Empresa |  |  |
| instance.criado_por | User |  |  |
| context.can_delete_horario | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| can_delete | boolean\|null |  |

## Logic

```text
# HorarioPrescricaoSerializer.get_can_delete (l.343-355):
user    = request.user    if request else None
empresa = request.empresa if request else None
if user and empresa:
    return ("can_delete_horario_prescricao" in get_permissoes_empresa(user, empresa)
            or instance.criado_por == user)
else:
    return None

# HorarioPrescricaoOfflineSerializer.get_can_delete (l.82-87):
return (self.context.get("can_delete_horario", False)
        or instance.criado_por == self.context.get("request").user)
```

## Edge cases (as implemented)
Primary serializer explicitly returns None (not False) when user/empresa context is unavailable; the offline serializer never returns None. Offline depends on the caller having precomputed and injected context['can_delete_horario'] (its computation is out of this partition).

## Divergence
Same logical rule, two permission sources: the primary HorarioPrescricaoSerializer calls the LIVE get_permissoes_empresa(user, empresa) and checks membership of 'can_delete_horario_prescricao', returning None when request/user/empresa is missing; the offline HorarioPrescricaoOfflineSerializer reads a PRECOMPUTED boolean context['can_delete_horario'] (default False) and never returns None. Both fall back to instance.criado_por == user.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 343-355 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 82-87 | `8166c07e` | duplicate |

**Merged from:**

- RULE-prescricao-BE-07-011
- RULE-prescricao-BE-07-012

**Related rules:**

- RULE-PRESCRICAO-015

## Notes
Backend delete-authorization computation. Frontend consumes the resulting can_delete flag in RULE-PRESCRICAO-015.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
