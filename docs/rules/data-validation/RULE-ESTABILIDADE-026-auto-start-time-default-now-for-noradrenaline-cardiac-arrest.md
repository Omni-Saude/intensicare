# RULE-ESTABILIDADE-026 — Auto start-time default (now) for noradrenaline & cardiac arrest

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Noradrenalina and ParadaCardioRespiratoria default horario_inicio to timezone.now() at save if unset.

## Inputs

| name | type |
|---|---|
| horario_inicio | datetime \| None |

## Outputs

| name | type |
|---|---|
| horario_inicio | datetime |

## Logic

```text
def save(): if not self.horario_inicio: self.horario_inicio = timezone.now(); super().save()
```

## Edge cases (as implemented)

Only sets when falsy. Drives the "started in last 24h" criteria (sepse C4, estabilidade C2, sedacao PCR-24h).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/noradrenalina.py` | 19-23 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cons-BE-10-067`

**Related rules:**

- [RULE-ESTABILIDADE-018](../care-pathway/RULE-ESTABILIDADE-018-estabilidade-manual-c2-noradrenaline-started-in-last-24h.md)

## Notes

Same pattern in parada_cardiorrespiratoria.py:18-22. VentilacaoMecanica.horario_inicio is a required field with NO default.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
