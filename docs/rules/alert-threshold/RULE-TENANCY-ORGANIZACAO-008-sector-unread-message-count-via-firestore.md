# RULE-TENANCY-ORGANIZACAO-008 — Sector unread message count via Firestore

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_qtd_mensagens looks up the requesting user's unread-message counter for this specific sector from Firestore at chats/{setor.pk}/usuarios/{usuario.pk}, defaulting to 0 if the document or field is missing.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.pk | uuid |  |
| request.user.pk | uuid |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| qtd_mensagens | integer |  |

## Logic

```text
def get_qtd_msg_setor(setor, usuario, db):
    doc_ref = db.collection("chats").document(str(setor.pk)).collection("usuarios").document(str(usuario.pk))
    data = doc_ref.get().to_dict() or {}
    return data.get("qtd_mensagens", 0)
```

## Edge cases (as implemented)
Missing document or missing 'qtd_mensagens' field both resolve to 0, not an error.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Internal Firestore lookup: get_qtd_msg_setor reads chats/{setor.pk}/usuarios/{usuario.pk}, returning data.get('qtd_mensagens', 0). Legacy verbatim confirmed at core/api/v1/serializers/setor.py:270-286 @ 8166c07.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 270-286 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-012`
- Related rules: RULE-TENANCY-ORGANIZACAO-007

## Notes
Identical helper function is duplicated (not imported/shared) in estabelecimento.py (RULE-estabelecimento-BE-05-007), where it is summed across multiple sectors instead of looked up for one. | Reconciliation: establishment-level counterpart (see related) reuses this same Firestore lookup helper (duplicated, not shared) but sums it across every sector of the establishment without a user-membership filter. Kept separate; this sector-level version is scoped to exactly one already-resolved sector.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
