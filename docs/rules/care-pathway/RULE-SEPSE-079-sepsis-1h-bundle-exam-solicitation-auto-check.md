# RULE-SEPSE-079 — Sepsis 1h bundle - exam solicitation auto-check

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Auto-marks the 'solicitacao_exame' first-hour item as done when the bed's first CPOE record carries a sepsis protocol, and posts a system observation.

## Inputs

- cpoe.protocolo_sepse (any, truthy => sepsis protocol prescribed)

## Outputs

- item.checado (boolean)
- observacao (text)

## Logic

```text
if item.nome_item == "solicitacao_exame":
    cpoe = item.trilha_interativa.trilha.cpoe_leito.first()
    if cpoe.protocolo_sepse:
        item.checado = True; item.save()
        mensagem = f"solicitados Exames na 1a hora, prescrito por {cpoe_first.nm_protocolo_sepse} as {cpoe_first.dt_protocolo_sepse}"
        enviar_observacao_trilha_interativa(mensagem, tipo_trilha="sepse", trilha_interativa=item.trilha_interativa, responsavel=system_user)
```

## Edge cases (as implemented)

Uses cpoe_leito.first() (no ordering guarantee). If cpoe_leito.first() is None, cpoe.protocolo_sepse raises AttributeError. Message re-queries cpoe_leito.first() for name/date fields.

## Divergence

Auto-check dispatch (core/utils.py) matches item.nome_item == 'solicitacao_exame' (SINGULAR), but the bundle item is created and enumerated as 'solicitacao_exames' (PLURAL) in RULE-SEPSE-076 (creation list) and RULE-SEPSE-096 (choices enum). The names never match, so this exam first-hour auto-check branch is dead code and never fires; only antimicrobial (RULE-SEPSE-080) and volume (RULE-SEPSE-081) auto-checks can trigger.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 221-235 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-CAREPATH-BE-12-003`

**Related rules:**

- [RULE-SEPSE-078](RULE-SEPSE-078-sepsis-first-hour-auto-check-guard.md)
- [RULE-SEPSE-076](RULE-SEPSE-076-sepse-interactive-protocol-bundle-hour-1-vs-reassessment-ite.md)
- [RULE-SEPSE-096](RULE-SEPSE-096-sepsis-interactive-bundle-step-and-package-enums.md)

## Notes

Truthiness (not equality) test on protocolo_sepse. Message text has 1a-hour attribution to prescriber.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
