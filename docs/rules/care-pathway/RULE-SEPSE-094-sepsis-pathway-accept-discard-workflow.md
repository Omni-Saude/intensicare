# RULE-SEPSE-094 — Sepsis-pathway accept/discard workflow

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A sepsis care-pathway (trilha) can be either accepted (aceito=true) or discarded with a mandatory reason (motivo_descartado), with the deciding actor (registrado_por) and decision timestamp (horario_registro_aceitacao) recorded at both the bed-occupancy Trilha level and the dedicated TrilhaInterativa.Sepse record level. Discarding is gated elsewhere by the can_recusar_protocolo_sepse permission.

## Inputs

- aceito (boolean)
- motivo_descartado (string, optional, required when aceito=false (implied by shape, not enforced in this partition))

## Outputs

- pathway acceptance state (derived)

## Logic

```text
if aceito == true:
  motivo_descartado not expected/used
else:  // discarded
  motivo_descartado should be populated (reason for refusing the sepsis protocol)
// gated by Permission "can_recusar_protocolo_sepse" (enforcement not present in this partition)
```

## Edge cases (as implemented)

motivo_descartado is optional at the type level even when aceito is false, so nothing prevents an empty/undefined reason from being submitted per the frontend types alone.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/TrilhaInterativa.d.ts` | 3-24 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-07-003`

**Related rules:**

- [RULE-SEPSE-072](RULE-SEPSE-072-sepse-protocol-acceptance-workflow-and-orange-alert.md)
- [RULE-SEPSE-073](RULE-SEPSE-073-sepse-protocol-rejection-workflow-and-neutral-alert.md)
- [RULE-SEPSE-097](RULE-SEPSE-097-sepsis-protocol-refusal-permission.md)

## Notes

Permission cross-reference at src/@types/models/Permissions.d.ts line 17 ("can_recusar_protocolo_sepse"); mirrored shape also at src/@types/models/Ocupacao.d.ts lines 94-103 (Trilha.trilha_interativa).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
