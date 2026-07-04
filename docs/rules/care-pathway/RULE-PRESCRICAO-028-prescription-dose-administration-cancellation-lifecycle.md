# RULE-PRESCRICAO-028 — Prescription-dose administration/cancellation lifecycle

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | prescricao |

## Rule
A scheduled medication administration time (Prescricao.Horario) carries "administrado" (administered) and "suspenso" (suspended) booleans, an optional "motivo_nao_administrado" (reason not administered), and a server-computed "can_delete" eligibility flag; when updating/cancelling a dose, the SendValue payload additionally supports "qtd_exportada" (quantity exported, e.g. to a billing/pharmacy system) and "justificativa_cancelamento" (cancellation justification).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| administrado | boolean |  |  |
| suspenso | boolean |  |  |
| motivo_nao_administrado | string, optional |  | presumed required when administrado=false (implied by shape, not enforced in this partition) |
| qtd_exportada | number, optional |  |  |
| justificativa_cancelamento | string, optional |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| Horario lifecycle state | derived |  |

## Logic

```text
// shape-only inference, no explicit validation code in this partition:
if administrado == false:
  motivo_nao_administrado SHOULD be populated (not enforced by a validator in this partition)
can_delete: boolean   // opaque server-computed deletion-eligibility flag
SendValue (PATCH/POST payload) may include: motivo_nao_administrado, administrado,
           qtd_exportada, justificativa_cancelamento, horario
```

## Edge cases (as implemented)
motivo_nao_administrado remains optional at the type level even when administrado is explicitly false, so nothing in this partition prevents submitting a not-administered dose without a reason.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Prescricao.d.ts` | 19-41 | `f9656be2` | primary |

**Merged from:**

- RULE-prescricao-FE-07-001

**Related rules:**

- RULE-PRESCRICAO-008
- RULE-PRESCRICAO-030
- RULE-PRESCRICAO-014

## Notes
qtd_exportada suggests integration with a billing/pharmacy export process (category billing-administrative overlap), but no such logic is present in this frontend partition.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
