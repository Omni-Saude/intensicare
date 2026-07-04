# RULE-SEDACAO-022 — Cardiac arrest within last 24h (PCR-24h helper, manual model)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | care-pathway |
| Type | threshold |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Determines whether a cardiac-arrest event counts as 'in the last 24h' for the manual sedation criteria.

## Inputs

| name | type |
|---|---|
| parada_cardiorrespiratoria.horario_inicio | datetime |

## Outputs

| name | type |
|---|---|
| pcr_24h | boolean |

## Logic

```text
if hasattr(dados_prontuario, 'parada_cardiorrespiratoria'):
  return abs((timezone.now() - pcr.horario_inicio).days) == 0
return False
```

## Edge cases (as implemented)

Uses timedelta.days == 0, i.e. 'recent' only if elapsed time is < 24h (days component 0). 24-48h -> days==1 -> False.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 90-101 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-018`

**Related rules:**

- [RULE-SEDACAO-018](RULE-SEDACAO-018-sedation-manual-c4-sedation-justified-by-severity.md)
- [RULE-SEDACAO-020](RULE-SEDACAO-020-sedation-manual-c6-severity-without-sedation.md)

## Notes

AMBIGUOUS: "last 24h" implemented as timedelta.days==0 (rolling <24h window), not a calendar day. Helper consumed by manual C4 (RULE-SEDACAO-018) and C6 (RULE-SEDACAO-020). Test test_trilha_sedacao.py:87-94.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
