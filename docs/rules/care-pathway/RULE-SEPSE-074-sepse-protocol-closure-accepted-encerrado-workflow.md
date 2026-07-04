# RULE-SEPSE-074 — SEPSE protocol closure (accepted -> encerrado) workflow

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
Updating an interactive SEPSE trilha that was previously accepted so that aceito becomes falsy closes the protocol: sets encerrado=true, finalizado=true, re-stamps horario_registro_aceitacao=now, sets the parent alert to "NEUTRO" and assistido=true, and posts a closure observation. Any other update passes through unchanged.

## Inputs

- instance.aceito (boolean)
- validated_data.aceito (boolean)

## Outputs

- encerrado (boolean)
- alerta_trilha_interativa (enum, {NEUTRO})

## Logic

```text
if instance.aceito and not validated_data.get("aceito"):
    validated_data["encerrado"] = True
    validated_data["finalizado"] = True
    validated_data["horario_registro_aceitacao"] = now()
    ti = update(instance, validated_data)
    TrilhaSepseV3Model.filter(pk=ti.trilha.get_pk).update(alerta_trilha_interativa="NEUTRO", assistido=True)
    post_observation("Protocolo de SEPSE foi encerrado as <ts> por <user>")
else:
    return update(instance, validated_data)   # no side effects
```

## Edge cases (as implemented)

Transition guard is specifically was-accepted -> now-not-accepted; toggling other fields while aceito stays true takes the passthrough branch.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/trilha_interativa_sepse.py` | 83-105 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-011`

**Related rules:**

- [RULE-SEPSE-072](RULE-SEPSE-072-sepse-protocol-acceptance-workflow-and-orange-alert.md)
- [RULE-SEPSE-073](RULE-SEPSE-073-sepse-protocol-rejection-workflow-and-neutral-alert.md)
- [RULE-SEPSE-097](RULE-SEPSE-097-sepsis-protocol-refusal-permission.md)

## Notes

Closure requires can_recusar_protocolo_sepse permission (RULE-sepse-BE-02-020).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
