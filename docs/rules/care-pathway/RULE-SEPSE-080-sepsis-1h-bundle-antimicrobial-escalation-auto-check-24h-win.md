# RULE-SEPSE-080 — Sepsis 1h bundle - antimicrobial escalation auto-check (24h window)

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
Auto-marks 'inicio_escalonamento_antimicrobiano' done when a CPOE updated within the 24h preceding the interactive pathway's creation time has a non-null day-0 antibiotic; posts a system observation naming the antibiotic.

## Inputs

- cpoe.dt_atualizacao_cpoe (datetime, >= trilha_interativa.criado_em - 24h)
- cpoe.ds_antibiotico_d0 (string, not null)

## Outputs

- item.checado (boolean)
- observacao (text)

## Logic

```text
elif item.nome_item == "inicio_escalonamento_antimicrobiano":
    cpoe_24 = trilha.cpoe_leito.filter(dt_atualizacao_cpoe__gte = trilha_interativa.criado_em - timedelta(hours=24))
    if cpoe_24.filter(ds_antibiotico_d0__isnull=False).exists():
        item.checado = True; item.save()
        mensagem = f"Iniciado novo ciclo de {cpoe_leito.first().ds_antibiotico_d0}"
        enviar_observacao_trilha_interativa(mensagem, "sepse", item.trilha_interativa, system_user)
```

## Edge cases (as implemented)

Window boundary is inclusive (__gte). Filter reference time is trilha_interativa.criado_em (pathway open time), NOT now. Message uses cpoe_leito.first().ds_antibiotico_d0 which may differ from the record that satisfied the filter.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 237-251 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-CAREPATH-BE-12-004`

**Related rules:**

- [RULE-SEPSE-078](RULE-SEPSE-078-sepsis-first-hour-auto-check-guard.md)
- [RULE-SEPSE-080](RULE-SEPSE-080-sepsis-1h-bundle-antimicrobial-escalation-auto-check-24h-win.md)

## Notes

24-hour lookback threshold. isnull=False => antibiotic present.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
