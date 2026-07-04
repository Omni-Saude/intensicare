# RULE-SEPSE-090 — Sepsis protocol lifecycle state display

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Renders the state of an accepted sepsis interactive protocol (trilha interativa). It always shows who accepted it and the acceptance timestamp. If concluida it shows "Concluida"; otherwise if finalizado it shows "Finalizada" with an optional refusal-reason popover (motivo_descartado). If neither, only acceptance info is shown (in-progress).

## Inputs

- trilhaInterativa.registrado_por.nome (string)
- trilhaInterativa.horario_registro_aceitacao (datetime)
- trilhaInterativa.concluida (boolean)
- trilhaInterativa.finalizado (boolean)
- trilhaInterativa.motivo_descartado (string)

## Outputs

- status label (enum {Concluida, Finalizada, (in-progress)})

## Logic

```text
header:
  "Aceito por: <registrado_por.nome>"
  clock icon + format(horario_registro_aceitacao, "DD/MM/YYYY HH:mm")
if (concluida):
  show check icon + "Concluida"
else if (finalizado):
  show close icon + "Finalizada"
  popover.content = motivo_descartado ? ("Motivo Recusa: " + motivo_descartado) : null
// else: in progress, only acceptance info shown
// Data source: if trilhaInterativaId provided, fetch via getTrilhaIterativa;
//   else use trilhaInterativaAtual directly.
```

## Edge cases (as implemented)

concluida takes precedence over finalizado (checked first). If both false the protocol is treated as in-progress. Refusal reason popover content is null when motivo_descartado is empty. Timestamp formatted with moment in DD/MM/YYYY HH:mm.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ProtocoloSepseContent/ProtocoloSepseContent.tsx` | 44-114 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-03-001`

**Related rules:**

- [RULE-SEPSE-075](RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)
- [RULE-SEPSE-093](RULE-SEPSE-093-sepsis-pathway-dual-completion-flags.md)
- [RULE-SEPSE-085](RULE-SEPSE-085-interactive-sepsis-pathway-completion-transition.md)

## Notes

"Finalizada" here corresponds to a refused/closed-without-completion protocol (motivo_descartado = refusal reason), distinct from "Concluida" (completed). Acceptance/refusal are driven by TrilhaInterativa (RULE-trilha-FE-03-003/004).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
