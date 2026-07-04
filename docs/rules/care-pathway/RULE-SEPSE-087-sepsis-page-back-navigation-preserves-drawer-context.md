# RULE-SEPSE-087 — Sepsis page "back" navigation preserves drawer context

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The back button on the sepsis interactive-pathway page navigates to the parent sector page with query parameters that identify the sepsis trilha, occupancy id, and bed name, so the parent page can reopen the recommendations drawer in the correct context.

## Inputs

- id_empresa, id_estabelecimento, id_setor (string (route params))
- ocupacao.id (string)
- ocupacao.leito.nome (string)

## Outputs

- destination URL (string)

## Logic

```text
router.replace(
  `/empresa/${id_empresa}/estabelecimento/${id_estabelecimento}/setor/${id_setor}` +
  `?trilha=sepse&ocupacao=${ocupacao.id}&leito=${ocupacao.leito.nome}`
)
```

## Edge cases (as implemented)

If ocupacao is not yet loaded, the button click is a no-op (guarded by `if (ocupacao)`).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/sepse/[id_trilha]/index.tsx` | 205-211 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-08-004`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
