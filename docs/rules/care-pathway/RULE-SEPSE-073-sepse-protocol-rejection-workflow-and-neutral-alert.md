# RULE-SEPSE-073 — SEPSE protocol rejection workflow and neutral alert

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Creating an interactive SEPSE trilha with aceito falsy marks it finalized, sets the parent TrilhaSepseV3 alert to "NEUTRO" and assistido=true, and posts a "rejection" observation.

## Inputs

- aceito (boolean)

## Outputs

- alerta_trilha_interativa (enum, {NEUTRO})
- assistido (boolean)
- finalizado (boolean)

## Logic

```text
else:  # not aceito
    validated_data["finalizado"] = True
    ti = create(validated_data)
    TrilhaSepseV3Model.filter(pk=ti.trilha.get_pk).update(alerta_trilha_interativa="NEUTRO", assistido=True)
    post_observation("Abertura do Protocolo de SEPSE Recusada as "
                     + ti.horario_registro_aceitacao.astimezone().strftime(...) + " por <user>")
```

## Edge cases (as implemented)

In the rejection branch horario_registro_aceitacao is never assigned, so the message builds from ti.horario_registro_aceitacao which is None/unset -> None.astimezone() raises AttributeError. The DB writes (finalizado, NEUTRO, assistido) run before the message, but the observation post and serializer return would fail.

## Divergence

DISCREPANCY: rejection message dereferences an unset horario_registro_aceitacao (likely NoneType.astimezone crash) unlike the acceptance/closure branches which set it to now(). Recorded verbatim; behavior depends on the model default for that field.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/trilha_interativa_sepse.py` | 66-81 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-010`

**Related rules:**

- [RULE-SEPSE-072](RULE-SEPSE-072-sepse-protocol-acceptance-workflow-and-orange-alert.md)
- [RULE-SEPSE-074](RULE-SEPSE-074-sepse-protocol-closure-accepted-encerrado-workflow.md)

## Notes

DISCREPANCY: rejection message dereferences an unset horario_registro_aceitacao (likely NoneType.astimezone crash) unlike the acceptance/closure branches which set it to now(). Recorded verbatim; behavior depends on the model default for that field.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
