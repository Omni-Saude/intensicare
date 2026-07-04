# RULE-SEPSE-072 — SEPSE protocol acceptance workflow and orange alert

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
Creating an interactive SEPSE trilha with aceito=true stamps the acceptance time, sets the parent TrilhaSepseV3 alert to "LARANJA" (orange), generates the 7 bundle items, and posts an audit observation recording protocol opening by the acting user.

## Inputs

- aceito (boolean)
- trilha (parent SepseV3 pk) (identifier)

## Outputs

- alerta_trilha_interativa (enum, {LARANJA})
- horario_registro_aceitacao (datetime)

## Logic

```text
if validated_data["aceito"]:
    validated_data["horario_registro_aceitacao"] = now()
    ti = create(validated_data)
    TrilhaSepseV3Model.filter(pk=ti.trilha.get_pk).update(alerta_trilha_interativa="LARANJA")
    criar_itens_trilha_interativa_sepse(ti.get_pk)   # 7 items (RULE-sepse-BE-02-008)
    post_observation("Realizada a abertura do Protocolo de SEPSE as <ts> por <user>")
```

## Edge cases (as implemented)

Timestamp formatted as %d/%m/%Y as %H:%M:%S in local tz (astimezone()).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/trilha_interativa_sepse.py` | 48-65 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-009`

**Related rules:**

- [RULE-SEPSE-073](RULE-SEPSE-073-sepse-protocol-rejection-workflow-and-neutral-alert.md)
- [RULE-SEPSE-074](RULE-SEPSE-074-sepse-protocol-closure-accepted-encerrado-workflow.md)
- [RULE-SEPSE-075](RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)
- [RULE-SEPSE-076](RULE-SEPSE-076-sepse-interactive-protocol-bundle-hour-1-vs-reassessment-ite.md)
- [RULE-SEPSE-096](RULE-SEPSE-096-sepsis-interactive-bundle-step-and-package-enums.md)

## Notes

Alert color state machine — accepted=LARANJA (see -010 rejected=NEUTRO, -012 completed=None).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
