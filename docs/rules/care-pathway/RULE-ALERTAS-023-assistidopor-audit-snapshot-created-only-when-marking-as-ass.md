# RULE-ALERTAS-023 — AssistidoPor audit snapshot created only when marking as assistido=True

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
After save_assistido runs, an AssistidoPor audit record (tipo, leito, paciente, usuario, and a fully-stringified snapshot of every field on the trilha object) is created ONLY if the request's 'assistido' value (defaulting True) is truthy; explicitly un-marking a trilha (assistido=False) does not create any audit record.

## Inputs

- request.data.assistido (boolean; defaults True)

## Outputs

- AssistidoPor record (object | none)

## Logic

```text
if request.data.get("assistido", True):
    AssistidoPor.objects.create(
        tipo=request.data.get("tipo"), leito=leito, paciente=paciente, usuario=request.user,
        payload_trilha=dict((k, str(v)) for k, v in model_to_dict(trilha).items()))
```

## Edge cases (as implemented)

Every field value in the snapshot is coerced to str(), including None -> the literal string 'None', numbers, dates, etc. - so payload_trilha is a dict of strings, not typed values.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/assistido.py` | 137-147 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-assistido-BE-05-004`

**Related rules:**

- [RULE-ALERTAS-022](RULE-ALERTAS-022-marking-a-trilha-as-assistido-bulk-update-for-v3-models-inst.md)

## Notes

This audit record is consumed by the monthly 'Total de intervencoes' indicator (RULE-setor-BE-05-016, other cluster).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
