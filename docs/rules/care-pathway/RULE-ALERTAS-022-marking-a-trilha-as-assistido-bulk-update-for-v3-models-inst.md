# RULE-ALERTAS-022 — Marking a trilha as assistido - bulk update for v3 models, instance save for legacy

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
save_assistido sets a trilha record's assistido flag (defaulting to True if not specified), assistido_por (current user, or None if assistido is being set False), and assistido_em (now). For v3 automatic-pathway models (per Leito.get_trilhas_automaticas_v3()), done via a bulk .update() call (bypassing instance .save(), signals, custom save side-effects); for any other model (legacy automatica, manual, homecare), an instance is fetched, attributes set, then saved normally.

## Inputs

- request.data.assistido (boolean; defaults True if absent)
- trilha_pk (uuid)

## Outputs

- trilha.assistido (boolean)
- trilha.assistido_por (uuid | null)
- trilha.assistido_em (datetime)

## Logic

```text
agora = timezone.now()
assistido = request.data.get("assistido", True)
trilha_obj = Model.objects.get(pk=trilha_pk)
if isinstance(trilha_obj, tuple(Leito.get_trilhas_automaticas_v3())):
    Model.objects.filter(pk=trilha_pk).update(
        assistido=assistido, assistido_por=(request.user if assistido else None), assistido_em=agora)
else:
    trilha_obj.assistido = assistido
    trilha_obj.assistido_por = request.user if trilha_obj.assistido else None   # reads the just-assigned value, equivalent to "if assistido"
    trilha_obj.assistido_em = agora
    trilha_obj.save()
```

## Edge cases (as implemented)

assistido_por is always cleared to None when assistido is False (un-marking), for both branches - the audit trail of 'who attended' is erased on un-assist, not preserved.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/assistido.py` | 89-105 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-assistido-BE-05-002`

**Related rules:**

- [RULE-ALERTAS-017](RULE-ALERTAS-017-assist-action-trilha-resolution-dual-movimentacao-leito-mode.md)
- [RULE-ALERTAS-023](RULE-ALERTAS-023-assistidopor-audit-snapshot-created-only-when-marking-as-ass.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
