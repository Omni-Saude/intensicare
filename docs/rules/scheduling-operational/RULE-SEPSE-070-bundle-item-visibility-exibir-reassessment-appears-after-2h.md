# RULE-SEPSE-070 — Bundle item visibility (exibir) - reassessment appears after 2h

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Reassessment (reavaliacao) items are hidden until 2h after protocol creation; all others always shown.

## Inputs

- pacote, trilha_interativa.criado_em (string / datetime)

## Outputs

- exibir (boolean)

## Logic

```text
if pacote == "reavaliacao": return (now - 2h > criado_em)
return True
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilhas_interativas/item_trilha_interativa.py` | 46-52 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-interativa-BE-03-132`

**Related rules:**

- [RULE-SEPSE-069](RULE-SEPSE-069-bundle-item-overdue-atraso-item-interativa-time-windows.md)
- [RULE-SEPSE-091](../care-pathway/RULE-SEPSE-091-sepsis-protocol-item-conditional-visibility-and-expandabilit.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
