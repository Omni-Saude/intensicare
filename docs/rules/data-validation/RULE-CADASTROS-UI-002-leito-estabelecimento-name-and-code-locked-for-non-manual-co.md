# RULE-CADASTROS-UI-002 — Leito/Estabelecimento name and code locked for non-manual companies

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On both the Estabelecimento and Leito edit forms, the "Nome" and "Código" fields are only editable when the parent company's type (empresaData.tipo) equals "manual"; for companies whose type is "automatica" (records synced from an external system) these fields are always disabled, regardless of the form's own disableAll/mode setting.

## Inputs

| name | type |
|---|---|
| empresaData.tipo | 'manual' \| 'automatica' |
| disableAll | boolean |

## Outputs

| name | type |
|---|---|
| Input/InputNumber disabled prop for nome and codigo | boolean |

## Logic

```text
disabled = disableAll || (empresaData?.tipo !== "manual")
```

## Edge cases (as implemented)

Even when the form is otherwise in an editable state (disableAll=false, e.g. an admin opened the edit modal), an "automatica" company still locks these two fields - there is no override/permission that re-enables them.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormEstabelecimento/FormEstabelecimento.tsx` | 39-60 | `f9656be266` | primary |
| trilhas-frontend | `src/components/FormLeito/FormLeito.tsx` | 40-56 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cadastro-FE-05-006`

**Related rules:**

- [RULE-CADASTROS-UI-004](RULE-CADASTROS-UI-004-camera-credential-fields-gated-on-can-manage-camera-permissi.md)
- [RULE-CADASTROS-UI-008](RULE-CADASTROS-UI-008-company-tipo-only-settable-at-creation-hex-color-round-trip.md)

## Notes

Identical predicate implemented independently in src/components/FormLeito/FormLeito.tsx lines 40-56 (same "manual" check, same disabled expression) - duplicated logic, not shared code.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
