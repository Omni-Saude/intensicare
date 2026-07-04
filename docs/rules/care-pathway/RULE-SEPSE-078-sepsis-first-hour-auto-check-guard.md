# RULE-SEPSE-078 — Sepsis first-hour auto-check guard

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
Automatic dispatch only fires for interactive-sepsis checklist items belonging to the 'first hour' bundle that are not yet checked; runs repeatedly (per docstring, every 1 min until 1h after protocol opening).

## Inputs

- item.pacote (string, 'primeira_hora' | other)
- item.checado (boolean, true|false)
- item.nome_item (string, solicitacao_exame | inicio_escalonamento_antimicrobiano | realizacao_expansao_volemica)

## Outputs

- side_effect (dispatch)

## Logic

```text
if item.pacote == "primeira_hora" and not item.checado:
    system_user = Usuario.objects.get(username="sistema").get_pk
    dispatch on item.nome_item -> RULE-003 / RULE-004 / RULE-005
# else: no-op
```

## Edge cases (as implemented)

Requires an existing Usuario with username=="sistema" (DoesNotExist would raise). Any nome_item outside the three handled values does nothing. Docstring states cadence of 1 min for up to 1 hour post-opening; the cadence itself is scheduled elsewhere (task checagem_trilha_interativa iterates items and calls this).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 214-220 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-CAREPATH-BE-12-002`

**Related rules:**

- [RULE-SEPSE-079](RULE-SEPSE-079-sepsis-1h-bundle-exam-solicitation-auto-check.md)
- [RULE-SEPSE-080](RULE-SEPSE-080-sepsis-1h-bundle-antimicrobial-escalation-auto-check-24h-win.md)
- [RULE-SEPSE-081](RULE-SEPSE-081-sepsis-1h-bundle-volume-expansion-auto-check-4h-window.md)

## Notes

Callers - trilha_automatica/tasks/checagem_trilha_interativa.py and trilha_automatica/api/v1/serializers/item_trilha_interativa_sepse.py. 'trilha' = sepsis care pathway; 'primeira_hora' = the 1-hour sepsis bundle.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
