# RULE-ALERTAS-011 — Assistido-overrides-alerta status color precedence (frontend render)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When rendering the visual alert status (border color, background, ball color, gender-icon color) for a patient/bed card or a trilha chip, the system always prefers the 'being assisted' state over the raw alert-level field. If assistido === true, statusKey "ASSISTIDO" is used regardless of the alerta value (VERMELHO/AMARELO/NEUTRO/LARANJA); only when not assistido does the raw alerta value select the color.

## Inputs

- ocupacao.assistido (boolean)
- ocupacao.alerta (VERMELHO|AMARELO|NEUTRO|LARANJA|ASSISTIDO|'')
- trilha.assistido (boolean)
- trilha.alerta (string enum)

## Outputs

- statusKey (string enum)
- color/background/ballColor (css color string)

## Logic

```text
statusKey = ocupacao.assistido ? "ASSISTIDO" : ocupacao.alerta
renderColor = statusTrilha[statusKey]?.ballColor
renderBackground = statusTrilha[statusKey]?.[isLight ? "backgroundLight" : "background"]
// identical pattern applied at trilha level:
trilhaStatusKey = trilha.assistido ? "ASSISTIDO" : trilha.alerta
```

## Edge cases (as implemented)

If statusKey resolves to "" (alerta empty/undefined and not assistido), statusTrilha[""] is undefined, so color/background expressions evaluate to `undefined`, which React/CSS silently drops (no border/background applied) rather than throwing.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/InfoPacienteHeader/InfoPacienteHeader.tsx` | 21-105 | `f9656be266` | primary |
| trilhas-frontend | `src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx` | 272-355, 540-556 | `f9656be266` | frontend-copy |
| trilhas-frontend | `src/components/MessageBallon/MessageBallon.tsx` | n/a (simpler alerta-only variant) | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-FE-06-001`

**Related rules:**

- [RULE-ALERTAS-024](../care-pathway/RULE-ALERTAS-024-care-pathway-trilha-status-severity-color-palette-statustril.md)

## Notes

Identical logic duplicated verbatim in CollapseCard.tsx (leito-level 272-355, trilha-level 540-556); MessageBallon.tsx uses a simpler alerta-only variant with no assistido override. statusTrilha (RULE-ALERTAS-024) is the shared color table: NEUTRO=green, AMARELO=yellow, VERMELHO=red, LARANJA=orange, ASSISTIDO=blue.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
